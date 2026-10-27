"""Oracle-backed individual assignment demonstrations and schema explorer."""
import inspect
import json
import re
import secrets
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for, Response
from . import db, services
from .assignment_queries import MODULES, EXTRA_SELECTS, find_module
from .registry import TABLES, table_info
from .web import require_role

bp = Blueprint('presentation', __name__)
FLOW_TITLES = ['Create an artwork','Assign it to an exhibition','Record expert assessments',
               'Create and open an auction','Maya bids ₹65,000','Sara bids ₹70,000',
               'Close the lot and record the sale','Complete payment and show revenue']


def workspace():
    token = session.get('oracle_workspace','')
    if not isinstance(token,str) or not re.fullmatch(r'[a-f0-9]{32}',token):
        token = secrets.token_hex(16)
        session['oracle_workspace'] = token
    return token


def result(conn, sql, binds=None):
    cur=conn.execute(sql,binds or {})
    records=cur.fetchall()
    return dict(columns=[c[0] for c in cur.description],rows=[dict(r) for r in records[:200]],truncated=len(records)>200)


def events(conn, token):
    with conn.raw.cursor() as cur:
        cur.execute('SELECT payload FROM lab_evidence WHERE workspace_id=:w ORDER BY evidence_id',w=token)
        return [json.loads(row[0].read()) for row in cur]


def record_event(conn, module_id, query_id, payload):
    import oracledb
    payload.update(module_id=module_id,query_id=query_id)
    with conn.raw.cursor() as cur:
        cur.setinputsizes(payload=oracledb.DB_TYPE_CLOB)
        cur.execute("INSERT INTO lab_evidence(evidence_id,workspace_id,module_id,query_id,payload) VALUES(lab_id_seq.NEXTVAL,:w,:m,:q,:payload)",
                    w=workspace(),m=module_id,q=query_id,payload=json.dumps(payload,ensure_ascii=False))


@bp.get('/staff/presentation')
@require_role('staff')
def index():
    conn=db.get_db()
    view=request.args.get('view','modules')
    if view == 'walkthrough':
        view='flow'
    if view == 'architecture':
        view='modules'
    if view not in ('modules','database','rules','coverage','flow'):
        abort(404)
    selected=find_module(request.args.get('module','collection'))
    if selected is None:
        abort(404)
    evidence=events(conn,workspace())
    state=conn.execute('SELECT * FROM lab_workspace WHERE workspace_id=? AND module_id=?',(workspace(),selected['id'])).fetchone()
    completed={m['id']:set(e['query_id'] for e in evidence if e['module_id']==m['id']) for m in MODULES}
    context=dict(view=view,modules=MODULES,selected=selected,state=state,evidence=evidence,
                 completed=completed,extras=EXTRA_SELECTS,health=dict(version=conn.raw.version,
                 schema=conn.execute('SELECT USER FROM dual').fetchone()[0]))
    if view=='flow':
        context['flow_state']=conn.execute("SELECT * FROM lab_workspace WHERE workspace_id=? AND module_id='workflow'",(workspace(),)).fetchone()
        context['flow_titles']=FLOW_TITLES
    if view=='database':
        table=request.args.get('table','artwork')
        if table not in TABLES:
            abort(404)
        context.update(table=table,columns=table_info(conn,table),
            preview=result(conn,'SELECT * FROM '+table+' WHERE ROWNUM<=8'),
            constraints=result(conn,"SELECT constraint_name,constraint_type,status FROM user_constraints WHERE table_name=:t ORDER BY constraint_type,constraint_name",{'t':table.upper()}),
            ddl='')
        with conn.raw.cursor() as cur:
            cur.execute("SELECT DBMS_METADATA.GET_DDL('TABLE',:t) FROM dual",t=table.upper())
            context['ddl']=cur.fetchone()[0].read()
    elif view=='rules':
        context['sources']=[]
        for name in ('VALIDATE_BID','VALIDATE_SALE','LOT_UPDATE_GUARD','AUCTION_UPDATE_GUARD'):
            source=conn.execute('SELECT text FROM user_source WHERE name=? ORDER BY line',(name,)).fetchall()
            context['sources'].append(dict(name=name,code=''.join(r[0] for r in source)))
        context['service_source']=inspect.getsource(services)
    return render_template('admin/oracle.html',**context)


@bp.post('/staff/presentation/execute/<module_id>/<query_id>')
@require_role('staff')
def execute(module_id,query_id):
    mod=find_module(module_id)
    query=next((q for q in mod['queries'] if q['id']==query_id),None) if mod else None
    if query is None:
        abort(404)
    conn=db.get_db()
    try:
        state=conn.execute('SELECT * FROM lab_workspace WHERE workspace_id=? AND module_id=? FOR UPDATE',(workspace(),module_id)).fetchone()
        if state is None:
            conn.execute('INSERT INTO lab_workspace(workspace_id,module_id,record_id,stage) VALUES(?,?,?,0)',(workspace(),module_id,conn.next_id()))
            state=conn.execute('SELECT * FROM lab_workspace WHERE workspace_id=? AND module_id=? FOR UPDATE',(workspace(),module_id)).fetchone()
        presenter=request.form.get('presenter','').strip()[:100] or mod['presenter']
        conn.execute('UPDATE lab_workspace SET presenter=? WHERE workspace_id=? AND module_id=?',(presenter,workspace(),module_id))
        check=f"SELECT * FROM {mod['table']} WHERE {mod['pk']}=:record_id"
        all_binds=dict(record_id=state['record_id'],value=request.form.get('value','').strip()[:150] or (mod['changed'] if query_id=='update' else mod['initial']),
                       email=f"demo-{state['record_id']}@atelier.example",search='%'+request.form.get('search','').strip()[:100]+'%')
        binds={k:v for k,v in all_binds.items() if ':'+k in query['sql']}
        before=result(conn,check,{'record_id':state['record_id']}) if query['kind']!='SELECT' else None
        if query['kind']=='SELECT':
            output=result(conn,query['sql'],binds)
            affected=None
        else:
            expected={'insert':0,'update':1,'delete':2}[query_id]
            if state['stage']!=expected:
                raise ValueError('Run INSERT, then UPDATE, then DELETE once, in that order. Completed results remain below.')
            changed=conn.execute(query['sql'],binds)
            affected=changed.rowcount
            if affected!=1:
                raise ValueError('Expected exactly one demonstration record. No changes committed.')
            output=result(conn,check,{'record_id':state['record_id']})
            conn.execute('UPDATE lab_workspace SET stage=? WHERE workspace_id=? AND module_id=?',(expected+1,workspace(),module_id))
        payload=dict(title=query['title'],kind=query['kind'],presenter=presenter,sql=query['sql'],binds=binds,
                     before=before,result=output,affected=affected,transaction='COMMIT',database='Oracle '+conn.raw.version)
        record_event(conn,module_id,query_id,payload)
        conn.commit()
        flash(f"{query['kind']} executed in Oracle. Result saved for your report.",'success')
    except (ValueError,db.IntegrityError,db.OperationalError) as error:
        conn.rollback()
        flash(str(error),'error')
    return redirect(url_for('presentation.index',module=module_id)+'#latest-result')


@bp.post('/staff/presentation/supplement/<key>')
@require_role('staff')
def supplement(key):
    conn=db.get_db()
    statements=[]
    outputs=[]
    try:
        extra=next((q for q in EXTRA_SELECTS if q['id']==key),None)
        if extra:
            statements.append(extra['sql'])
            outputs.append(result(conn,extra['sql']))
        elif key=='tcl':
            number=conn.next_id()
            steps=[("INSERT INTO curator(curator_id,name) VALUES(:id,'TCL demonstration')",{'id':number}),
                   ('COMMIT',{}),('SAVEPOINT before_change',{}),
                   ("UPDATE curator SET name='Temporary value' WHERE curator_id=:id",{'id':number}),
                   ('SELECT curator_id,name FROM curator WHERE curator_id=:id',{'id':number}),
                   ('ROLLBACK TO before_change',{}),('SELECT curator_id,name FROM curator WHERE curator_id=:id',{'id':number}),
                   ('DELETE FROM curator WHERE curator_id=:id',{'id':number}),('ROLLBACK',{}),
                   ('SELECT curator_id,name FROM curator WHERE curator_id=:id',{'id':number}),
                   ('DELETE FROM curator WHERE curator_id=:id',{'id':number}),('COMMIT',{})]
            for sql,binds in steps:
                statements.append(sql)
                if sql.startswith('SELECT'):
                    outputs.append(result(conn,sql,binds))
                else:
                    conn.execute(sql,binds)
        elif key=='ddl':
            name='LAB_DDL_'+str(conn.next_id())
            steps=[f'CREATE TABLE {name} (example_id NUMBER PRIMARY KEY,note VARCHAR2(100))',
                   f'ALTER TABLE {name} ADD created_on DATE DEFAULT SYSDATE',
                   f'CREATE INDEX {name}_IX ON {name}(note)',
                   f"SELECT column_name,data_type FROM user_tab_columns WHERE table_name='{name}' ORDER BY column_id",
                   f'DROP TABLE {name} PURGE']
            for sql in steps:
                statements.append(sql)
                if sql.startswith('SELECT'):
                    outputs.append(result(conn,sql))
                else:
                    conn.execute(sql)
        else:
            abort(404)
        payload=dict(title=extra['title'] if extra else key.upper()+' demonstration',kind=key.upper(),presenter='Group',
                     sql=';\n'.join(statements),binds={},result=outputs[-1],outputs=outputs,
                     before=None,affected=None,transaction='COMMIT',database='Oracle '+conn.raw.version)
        record_event(conn,'supplement',key,payload)
        conn.commit()
        flash('Oracle result saved. DDL auto-commits; TCL results show the rollback effects.','success')
    except (ValueError,db.OperationalError) as error:
        conn.rollback()
        flash(str(error),'error')
    return redirect(url_for('presentation.index',view='coverage')+'#latest-result')


@bp.get('/staff/presentation/export')
@require_role('staff')
def export():
    evidence=events(db.get_db(),workspace())
    text=['# Atelier — Oracle SQL execution evidence','',
          'Executed in the Oracle project schema. Parameters and recorded results follow each statement.','']
    for event in evidence:
        text += [f"## {event['presenter']} · {event['title']}",'','```sql',event['sql']+';','```','',
                 'Parameters: `'+json.dumps(event['binds'],ensure_ascii=False)+'`','',
                 'Transaction: '+event['transaction'],'','```json',json.dumps(event,indent=2,ensure_ascii=False),'```','']
    return Response('\n'.join(text),mimetype='text/markdown',headers={'Content-Disposition':'attachment; filename=Atelier_Oracle_Results.md'})


@bp.post('/staff/presentation/start')
@require_role('staff')
def start():
    return redirect(url_for('presentation.index',view='flow'))


@bp.post('/staff/presentation/flow/next')
@require_role('staff')
def flow_next():
    conn=db.get_db()
    try:
        state=conn.execute("SELECT * FROM lab_workspace WHERE workspace_id=? AND module_id='workflow' FOR UPDATE",(workspace(),)).fetchone()
        if state is None:
            conn.execute("INSERT INTO lab_workspace(workspace_id,module_id,record_id,stage,presenter) VALUES(?,'workflow',?,0,'Group')",(workspace(),conn.next_id()))
            state=conn.execute("SELECT * FROM lab_workspace WHERE workspace_id=? AND module_id='workflow' FOR UPDATE",(workspace(),)).fetchone()
        stage=state['stage']
        if request.form.get('expected_stage')!=str(stage) or stage>=8:
            raise ValueError('This step has already run. Refresh to show the latest result.')
        history=[event for event in events(conn,workspace()) if event['module_id']=='workflow']
        ids=dict(history[-1]['flow']) if history else {'artwork_id':state['record_id']}
        conn.trace=[]
        conn.defer_commit=True
        before=result(conn,'SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id',{'id':ids['artwork_id']})
        if stage==0:
            conn.execute("INSERT INTO artwork(artwork_id,artist_id,title,year_created,medium,image_path) VALUES(?,1,?,2026,'Oil on canvas','images/artwork-01.webp')",(ids['artwork_id'],f"Presentation Study {ids['artwork_id']}"))
        elif stage==1:
            conn.execute("INSERT INTO exhibition_artwork(exhibition_id,artwork_id,display_position) VALUES(1,?,'Presentation wall')",(ids['artwork_id'],))
        elif stage==2:
            conn.execute("INSERT INTO appraisal(artwork_id,expert_id,appraisal_date,estimated_value,notes) VALUES(?,1,TRUNC(SYSDATE),8000000,'Presentation assessment')",(ids['artwork_id'],))
            conn.execute("INSERT INTO authentication(artwork_id,expert_id,certificate_no,authentication_date,result,notes) VALUES(?,1,?,TRUNC(SYSDATE),'Authentic','Presentation certificate')",(ids['artwork_id'],f"DEMO-{ids['artwork_id']}"))
        elif stage==3:
            ids['auction_id']=conn.execute('INSERT INTO auction(gallery_id,title,"DATE",venue) VALUES(1,?,TRUNC(SYSDATE),\'Atelier Mumbai\')',(f"Presentation Auction {ids['artwork_id']}",)).lastrowid
            ids['lot_id']=conn.execute('INSERT INTO auction_lot(auction_id,artwork_id,lot_number,starting_price,reserve_price) VALUES(?,?,1,5000000,6000000)',(ids['auction_id'],ids['artwork_id'])).lastrowid
            services.open_auction(conn,ids['auction_id'])
        elif stage in (4,5):
            ids['bid_id']=services.place_bid(conn,ids['lot_id'],1 if stage==4 else 3,6500000 if stage==4 else 7000000)
        elif stage==6:
            outcome=services.close_lot(conn,ids['lot_id'])
            ids['sale_id']=outcome['sale_id']
        else:
            services.update_payment(conn,ids['sale_id'],'completed')
        after=result(conn,'SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id',{'id':ids['artwork_id']})
        outputs=[after]
        if ids.get('lot_id'):
            outputs.append(result(conn,'SELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id',{'id':ids['lot_id']}))
        if ids.get('sale_id'):
            outputs.append(result(conn,'SELECT sale_id,sale_price/100 AS sale_inr,payment_status FROM sale WHERE sale_id=:id',{'id':ids['sale_id']}))
            outputs.append(result(conn,'SELECT * FROM gallery_revenue ORDER BY gallery_id'))
        executed=list(conn.trace)
        conn.execute("UPDATE lab_workspace SET stage=? WHERE workspace_id=? AND module_id='workflow'",(stage+1,workspace()))
        record_event(conn,'workflow',f'step{stage+1}',dict(title=FLOW_TITLES[stage],kind='WORKFLOW',presenter='Group',flow=ids,
            sql=';\n'.join(e['sql'] for e in executed),binds={},executed=executed,result=after,outputs=outputs,
            before=before,affected=None,transaction='COMMIT',database='Oracle '+conn.raw.version))
        conn.commit()
        flash('Oracle workflow step committed. SQL and outputs are saved.','success')
    except (ValueError,db.OperationalError) as error:
        conn.rollback()
        flash(str(error),'error')
    finally:
        conn.defer_commit=False
    return redirect(url_for('presentation.index',view='flow')+'#latest-result')
