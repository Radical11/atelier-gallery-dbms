"""Staff presentation studio: inspect the real schema and run an isolated live demo."""
import inspect
import json
from pathlib import Path
import re
import secrets
import sqlite3
import threading

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from . import db, services
from .seed import seed_db
from .registry import TABLES
from .web import require_role

bp = Blueprint('presentation', __name__)
_runner_lock = threading.RLock()
STEPS = [
    dict(title='Create an artwork', concept='INSERT · primary & foreign keys',
         explanation='A new artwork receives its own primary key and references an existing artist. Its image comes from the original demo collection.'),
    dict(title='Place it in an exhibition', concept='Many-to-many · composite key',
         explanation='An associative row links the artwork to an exhibition. The composite primary key prevents the same pair appearing twice.'),
    dict(title='Record the expert checks', concept='Normalized relationships',
         explanation='Appraisal and authentication reference an expert ID. Expert names are joined from ART_EXPERT rather than duplicated in assessment records.'),
    dict(title='Open the auction room', concept='Atomic transaction · state rules',
         explanation='Create a draft auction and lot, then open them through the real auction service. The artwork must be available and may have only one active listing.'),
    dict(title='Maya places a bid', concept='Validation · transaction',
         explanation='Maya offers ₹65,000. SQLite validates the open lot and starting price; BEGIN IMMEDIATE protects the read/check/write operation.'),
    dict(title='Sara bids higher', concept='Aggregation · bid history',
         explanation='Sara offers ₹70,000. The highest bid changes while Maya’s accepted offer remains in the immutable bid history.'),
    dict(title='Close the lot', concept='Winning bid · atomic sale',
         explanation='The highest bid meets the ₹60,000 reserve. One transaction records Sara as collector, creates a sale, and updates the lot and artwork states.'),
    dict(title='Complete the payment', concept='UPDATE · derived aggregate',
         explanation='Mark the payment completed. Sara’s total spending is calculated from completed sales instead of stored as a duplicated collector attribute.'),
]
VIEWS = ('walkthrough', 'database', 'rules', 'architecture')


def _directory():
    directory = Path(current_app.config.get('PRESENTATION_DIR', Path(current_app.config['DATABASE']).parent / 'presentation'))
    directory.mkdir(parents=True, exist_ok=True)
    return directory.resolve()


def sandbox_path():
    token = session.get('presentation_id', '')
    if not isinstance(token, str) or not re.fullmatch(r'[a-f0-9]{32}', token):
        return None
    path = _directory() / f'{token}.sqlite'
    return path if path.is_file() else None


def start_sandbox():
    old = sandbox_path()
    token = secrets.token_hex(16)
    path = _directory() / f'{token}.sqlite'
    conn = db.connect(path)
    try:
        db.init_db(conn)
        seed_db(conn)
        conn.executescript('''CREATE TABLE demo_state (
            id INTEGER PRIMARY KEY CHECK(id=1), stage INTEGER NOT NULL,
            artwork_id INTEGER, auction_id INTEGER, lot_id INTEGER, sale_id INTEGER);
            INSERT INTO demo_state(id,stage) VALUES(1,0);
            CREATE TABLE demo_event(stage INTEGER PRIMARY KEY, title TEXT NOT NULL,
            sql_text TEXT NOT NULL, read_sql TEXT NOT NULL, before_json TEXT NOT NULL,
            after_json TEXT NOT NULL, columns_json TEXT NOT NULL);''')
    except Exception:
        conn.close()
        path.unlink(missing_ok=True)
        raise
    finally:
        conn.close()
    session['presentation_id'] = token
    # Only delete the previous signed-session sandbox under the resolved presentation folder.
    if old and old.parent.resolve() == _directory() and old != path:
        old.unlink(missing_ok=True)


def _query(conn, stage, state):
    artwork_id, auction_id, lot_id = state['artwork_id'], state['auction_id'], state['lot_id']
    if stage == 1:
        sql = 'SELECT artwork_id, title, artist_id, status FROM artwork ORDER BY artwork_id DESC LIMIT 3'
        params = ()
    elif stage == 2:
        sql = '''SELECT e.title AS exhibition, w.title AS artwork, ea.display_position
FROM exhibition_artwork ea JOIN exhibition e ON e.exhibition_id=ea.exhibition_id
JOIN artwork w ON w.artwork_id=ea.artwork_id WHERE w.artwork_id=?'''
        params = (artwork_id,)
    elif stage == 3:
        sql = '''SELECT w.title, e.name AS expert, p.estimated_value AS estimate_paise,
t.certificate_no, t.result FROM artwork w
LEFT JOIN appraisal p ON p.artwork_id=w.artwork_id
LEFT JOIN art_expert e ON e.expert_id=p.expert_id
LEFT JOIN authentication t ON t.artwork_id=w.artwork_id WHERE w.artwork_id=?'''
        params = (artwork_id,)
    elif stage == 4:
        sql = '''SELECT a.title AS auction, a.status AS auction_status, l.lot_id,
l.status AS lot_status, w.status AS artwork_status FROM auction a
JOIN auction_lot l ON l.auction_id=a.auction_id
JOIN artwork w ON w.artwork_id=l.artwork_id WHERE a.auction_id=?'''
        params = (auction_id,)
    elif stage in (5, 6):
        sql = '''SELECT b.bid_id, r.name AS bidder, b.bid_amount AS amount_paise,
b.bid_time FROM bid b JOIN bidder r ON r.bidder_id=b.bidder_id
WHERE b.lot_id=? ORDER BY b.bid_amount DESC'''
        params = (lot_id,)
    elif stage == 7:
        sql = '''SELECT l.lot_id, l.status AS lot_status, w.status AS artwork_status,
s.sale_id, c.name AS buyer, s.sale_price AS price_paise, s.payment_status
FROM auction_lot l JOIN artwork w ON w.artwork_id=l.artwork_id
LEFT JOIN sale s ON s.bid_id=(SELECT b.bid_id FROM bid b
WHERE b.lot_id=l.lot_id ORDER BY b.bid_amount DESC LIMIT 1)
LEFT JOIN collector c ON c.collector_id=s.collector_id
WHERE l.lot_id=?'''
        params = (lot_id,)
    else:
        sql = '''SELECT c.name AS collector, s.payment_status,
SUM(CASE WHEN s.payment_status='completed' THEN s.sale_price ELSE 0 END) AS spent_paise
FROM collector c JOIN sale s ON s.collector_id=c.collector_id
WHERE c.bidder_id=3 GROUP BY c.collector_id, s.payment_status'''
        params = ()
    cursor = conn.execute(sql, params)
    return sql, [c[0] for c in cursor.description], [dict(r) for r in cursor]


def _perform(conn, stage, state):
    if stage == 1:
        state['artwork_id'] = conn.execute('''INSERT INTO artwork
            (artist_id,title,year_created,medium,dimensions,description,image_path)
            VALUES(1,'A New Perspective',2026,'Oil on canvas','80 × 60 cm',
            'A work created during the live presentation.','images/artwork-12.webp')''').lastrowid
        conn.commit()
    elif stage == 2:
        conn.execute('INSERT INTO exhibition_artwork(exhibition_id,artwork_id,display_position) VALUES(3,?,?)',
                     (state['artwork_id'], 'East wall · presentation'))
        conn.commit()
    elif stage == 3:
        conn.execute("INSERT INTO appraisal(artwork_id,expert_id,appraisal_date,estimated_value,notes) VALUES(?,1,date('now'),9000000,'Live presentation assessment.')", (state['artwork_id'],))
        conn.execute("INSERT INTO authentication(artwork_id,expert_id,certificate_no,authentication_date,result,notes) VALUES(?,1,'PRESENTATION-001',date('now'),'Authentic','Live presentation certificate.')", (state['artwork_id'],))
        conn.commit()
    elif stage == 4:
        state['auction_id'] = conn.execute("INSERT INTO auction(gallery_id,title,date,venue,description) VALUES(1,'The Presentation Room',date('now'),'Atelier Mumbai','A live demonstration auction.')").lastrowid
        state['lot_id'] = conn.execute('INSERT INTO auction_lot(auction_id,artwork_id,lot_number,starting_price,reserve_price) VALUES(?,?,1,5000000,6000000)', (state['auction_id'], state['artwork_id'])).lastrowid
        conn.commit()
        services.open_auction(conn, state['auction_id'])
    elif stage == 5:
        services.place_bid(conn, state['lot_id'], 1, 6500000)
    elif stage == 6:
        services.place_bid(conn, state['lot_id'], 3, 7000000)
    elif stage == 7:
        state['sale_id'] = services.close_lot(conn, state['lot_id'])['sale_id']
    elif stage == 8:
        services.update_payment(conn, state['sale_id'], 'completed')


def run_step(expected_stage):
    path = sandbox_path()
    if path is None:
        raise services.DomainError('Start a presentation demo first.')
    with _runner_lock:
        conn = db.connect(path)
        staged = db.connect(':memory:')
        try:
            state = dict(conn.execute('SELECT * FROM demo_state WHERE id=1').fetchone())
            if expected_stage != state['stage']:
                raise services.DomainError('That step has already changed. The latest result is shown below.')
            if state['stage'] >= len(STEPS):
                raise services.DomainError('All steps are complete. Restart the demo to present it again.')
            stage = state['stage'] + 1
            # Stage a complete database snapshot, using the unmodified production services.
            # Publishing the backup commits the step and its evidence together; a failed
            # service or evidence write cannot leave the presentation halfway advanced.
            conn.backup(staged)
            _, _, before = _query(staged, stage, state)
            trace = []
            staged.set_trace_callback(trace.append)
            _perform(staged, stage, state)
            staged.set_trace_callback(None)
            sql, columns, after = _query(staged, stage, state)
            writes = list(dict.fromkeys(s for s in trace if re.match(r'\s*(INSERT|UPDATE|DELETE|BEGIN|COMMIT)', s, re.I)))
            staged.execute('UPDATE demo_state SET stage=?, artwork_id=?, auction_id=?, lot_id=?, sale_id=? WHERE id=1',
                           (stage,state['artwork_id'],state['auction_id'],state['lot_id'],state['sale_id']))
            staged.execute('INSERT INTO demo_event VALUES(?,?,?,?,?,?,?)',
                (stage,STEPS[stage-1]['title'],';\n\n'.join(writes),sql,json.dumps(before),json.dumps(after),json.dumps(columns)))
            staged.commit()
            staged.backup(conn)
            return stage
        finally:
            staged.close()
            conn.close()


def walkthrough():
    state, events = None, []
    path = sandbox_path()
    if path:
        conn = db.connect(path)
        try:
            state = dict(conn.execute('SELECT * FROM demo_state WHERE id=1').fetchone())
            for row in conn.execute('SELECT * FROM demo_event ORDER BY stage'):
                item = dict(row)
                for name in ('before','after','columns'):
                    item[name] = json.loads(item.pop(name+'_json'))
                events.append(item)
        finally:
            conn.close()
    requested = request.args.get('step', type=int)
    selected = next((e for e in events if e['stage']==requested), events[-1] if events else None)
    return dict(state=state,events=events,selected=selected,steps=STEPS,
                next_step=STEPS[state['stage']] if state and state['stage']<len(STEPS) else None)


def database_details(table):
    if table not in TABLES:
        abort(404)
    conn = db.get_db()
    columns = [dict(r) for r in conn.execute(f'PRAGMA table_info({table})')]
    foreign_keys = [dict(r) for r in conn.execute(f'PRAGMA foreign_key_list({table})')]
    indexes = []
    for row in conn.execute(f'PRAGMA index_list({table})'):
        index = dict(row)
        # Index names originate in SQLite, quoted as identifiers rather than interpolated SQL.
        quoted = index['name'].replace('"','""')
        index['columns'] = [r['name'] for r in conn.execute(f'PRAGMA index_info("{quoted}")')]
        indexes.append(index)
    ddl = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone()['sql']
    records = [dict(r) for r in conn.execute(f'SELECT * FROM {table} ORDER BY 1 LIMIT 8')]
    return dict(table=table,table_label=TABLES[table],schema_columns=columns,foreign_keys=foreign_keys,
        indexes=indexes,ddl=ddl,preview_rows=records,
        record_count=conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0],
        domain_counts=[dict(name=k,label=v,count=conn.execute(f'SELECT COUNT(*) FROM {k}').fetchone()[0]) for k,v in TABLES.items()])


@bp.get('/staff/presentation')
@require_role('staff')
def index():
    view = request.args.get('view','walkthrough')
    if view not in VIEWS:
        abort(404)
    context = dict(view=view,health=dict(
        version=sqlite3.sqlite_version,
        foreign_keys=bool(db.get_db().execute('PRAGMA foreign_keys').fetchone()[0]),
        integrity=db.get_db().execute('PRAGMA quick_check').fetchone()[0]))
    if view=='walkthrough':
        context.update(walkthrough())
    elif view=='database':
        context.update(database_details(request.args.get('table','artwork')))
    elif view=='rules':
        context['triggers']=[dict(r) for r in db.get_db().execute("SELECT name,tbl_name,sql FROM sqlite_master WHERE type='trigger' ORDER BY tbl_name,name")]
        context['service_sources']=[dict(name=name,code=inspect.getsource(getattr(services,name))) for name in ('_transaction','place_bid','open_auction','close_lot','update_payment')]
    return render_template('admin/presentation.html',**context)


@bp.post('/staff/presentation/start')
@require_role('staff')
def start():
    with _runner_lock:
        start_sandbox()
    flash('A fresh presentation copy is ready. Your main gallery records are unchanged.','success')
    return redirect(url_for('presentation.index')+'#demo-result')


@bp.post('/staff/presentation/next')
@require_role('staff')
def next_step():
    try:
        raw = request.form.get('expected_stage','')
        if not raw.isdigit() or len(raw)>2:
            raise services.DomainError('Reload the presentation before running the next step.')
        stage = run_step(int(raw))
        return redirect(url_for('presentation.index',step=stage)+'#demo-result')
    except (services.DomainError,sqlite3.Error) as error:
        flash(str(error),'error')
        return redirect(url_for('presentation.index'))
