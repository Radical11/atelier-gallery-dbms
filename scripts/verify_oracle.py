"""Run the assignment through Flask + Oracle and save real submission evidence.

This creates fictional presentation history in Oracle; it never resets either DB.
"""
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from atelier import create_app
from atelier.assignment_queries import MODULES, EXTRA_SELECTS
from atelier.presentation import events
from atelier.db import get_db
from atelier.registry import TABLES


def token(response):
    return re.search(rb'name="csrf_token" value="([^"]+)"',response.data).group(1).decode()


def main():
    app=create_app({'TESTING':True})
    checked=[]
    with app.test_client() as client:
        for email,password,role in [('admin@atelier.example','AdminDemo!2026','staff'),
            ('maya@atelier.example','BidderDemo!2026','bidder'),('arjun@atelier.example','BidderDemo!2026','bidder'),
            ('sara@atelier.example','BidderDemo!2026','bidder')]:
            response=client.get('/login')
            response=client.post('/login',data=dict(csrf_token=token(response),email=email,password=password))
            assert response.status_code==302,email
            assert client.get('/staff').status_code==(200 if role=='staff' else 403)
            checked.append(email+' login and '+role+' role')
            response=client.get('/')
            client.post('/logout',data=dict(csrf_token=token(response)))
        page=client.get('/login')
        client.post('/login',data=dict(csrf_token=token(page),email='admin@atelier.example',password='AdminDemo!2026'))
        for url in ['/', '/collection','/collection/1','/exhibitions','/exhibitions/1','/auctions','/auctions/1','/staff',
                    '/staff/presentation?view=database','/staff/presentation?view=rules','/staff/presentation?view=coverage']:
            assert client.get(url).status_code==200,url
        for table in TABLES:
            assert client.get('/staff/data/'+table).status_code==200,table
        for name in ('collection','exhibitions','bidding','revenue','collectors','assessments'):
            assert client.get('/staff/reports?query='+name).status_code==200,name
        for mod in MODULES:
            for query in mod['queries']:
                page=client.get('/staff/presentation?module='+mod['id'])
                data=dict(csrf_token=token(page),presenter=mod['presenter'])
                response=client.post('/staff/presentation/execute/'+mod['id']+'/'+query['id'],data=data,follow_redirects=True)
                assert response.status_code==200,(mod['id'],query['id'])
                assert b'executed in Oracle' in response.data,(mod['id'],query['id'],response.data[-1000:])
                checked.append(mod['id']+'/'+query['id'])
        for key in ['ddl','tcl']+[e['id'] for e in EXTRA_SELECTS]:
            page=client.get('/staff/presentation?view=coverage')
            response=client.post('/staff/presentation/supplement/'+key,data=dict(csrf_token=token(page)),follow_redirects=True)
            assert b'Oracle result saved' in response.data,key
            checked.append(key)
        for stage in range(8):
            page=client.get('/staff/presentation?view=flow')
            response=client.post('/staff/presentation/flow/next',data=dict(csrf_token=token(page),expected_stage=stage),follow_redirects=True)
            assert b'Oracle workflow step committed' in response.data,('workflow step',stage,response.data[-1000:])
            checked.append('workflow '+str(stage+1))
        report=client.get('/staff/presentation/export')
        assert report.status_code==200
        (ROOT/'docs'/'assignment'/'ORACLE_EXECUTION_OUTPUTS.md').write_bytes(report.data)
        with client.session_transaction() as state:
            workspace=state['oracle_workspace']
        with app.app_context():
            conn=get_db()
            evidence=events(conn,workspace)
            assert len(evidence)==55,len(evidence)
            for mod in MODULES:
                assert len({e['query_id'] for e in evidence if e['module_id']==mod['id']})==8
                dml=[e for e in evidence if e['module_id']==mod['id'] and e['kind']!='SELECT']
                assert all(e['affected']==1 for e in dml)
            flow=[e for e in evidence if e['module_id']=='workflow']
            ids=flow[-1]['flow']
            sale=conn.execute('SELECT * FROM sale WHERE sale_id=?',(ids['sale_id'],)).fetchone()
            assert sale['payment_status']=='completed' and sale['sale_price']==7000000
            checked.append('new Oracle connection sees completed ₹70,000 sale')
            assert conn.execute("SELECT COUNT(*) FROM user_objects WHERE status<>'VALID'").fetchone()[0]==0
            assert conn.execute("SELECT COUNT(*) FROM user_triggers WHERE status<>'ENABLED'").fetchone()[0]==0
        (ROOT/'docs'/'assignment'/'VERIFICATION.json').write_text(json.dumps(dict(engine='Oracle',checks=checked,
            records=len(evidence),workspace=workspace,workflow=ids),indent=2,ensure_ascii=False),encoding='utf-8')
    print('Oracle verified: four accounts, public/staff pages, all 40 individual statements, seven supplements, eight workflow steps.')
    print('Actual SQL and outputs saved in docs/assignment/ORACLE_EXECUTION_OUTPUTS.md')


if __name__=='__main__':
    main()
