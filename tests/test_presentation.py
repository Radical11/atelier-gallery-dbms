"""End-to-end database rules exercised by the presentation walkthrough."""
from atelier import db, seed, services


def test_isolated_walkthrough_executes_real_database_rules(tmp_path):
    main = db.connect(tmp_path / 'main.sqlite')
    sandbox = db.connect(tmp_path / 'sandbox.sqlite')
    try:
        for conn in (main, sandbox):
            db.init_db(conn)
            seed.seed_db(conn)
        tables = ('artwork', 'exhibition_artwork', 'appraisal', 'authentication', 'auction', 'auction_lot', 'bid', 'sale', 'collector')
        def snapshot(conn):
            return {table: [tuple(r) for r in conn.execute(f'SELECT * FROM {table} ORDER BY 1')] for table in tables}
        main_before = snapshot(main)
        # Exercise create, update and delete before keeping the actual demo work.
        with sandbox:
            scratch = sandbox.execute("INSERT INTO artwork(artist_id,title) VALUES(1,'Scratch')").lastrowid
            sandbox.execute("UPDATE artwork SET title='Scratch updated' WHERE artwork_id=?", (scratch,))
            assert sandbox.execute('SELECT title FROM artwork WHERE artwork_id=?', (scratch,)).fetchone()[0] == 'Scratch updated'
            sandbox.execute('DELETE FROM artwork WHERE artwork_id=?', (scratch,))
            art = sandbox.execute("INSERT INTO artwork(artist_id,title,year_created,medium) VALUES(1,'Studio Walkthrough',2026,'Acrylic')").lastrowid
            sandbox.execute("INSERT INTO exhibition_artwork VALUES(1,?,'Studio')", (art,))
            sandbox.execute("INSERT INTO appraisal(artwork_id,expert_id,appraisal_date,estimated_value) VALUES(?,1,date('now'),7500000)", (art,))
            sandbox.execute("INSERT INTO authentication(artwork_id,expert_id,certificate_no,authentication_date,result) VALUES(?,1,'STUDIO-TEST-001',date('now'),'Authentic')", (art,))
            auction = sandbox.execute("INSERT INTO auction(gallery_id,title,date,status) VALUES(1,'Studio Auction',date('now'),'draft')").lastrowid
            lot = sandbox.execute("INSERT INTO auction_lot(auction_id,artwork_id,lot_number,starting_price,reserve_price) VALUES(?,?,1,6000000,6500000)", (auction,art)).lastrowid
        services.open_auction(sandbox, auction)
        maya_bid = services.place_bid(sandbox, lot, 1, 6500000)
        sara_bid = services.place_bid(sandbox, lot, 3, 7000000)
        result = services.close_lot(sandbox, lot)
        sale = sandbox.execute('SELECT * FROM sale WHERE sale_id=?', (result['sale_id'],)).fetchone()
        assert (result['status'], sale['bid_id'], sale['sale_price'], sale['payment_status']) == ('sold',sara_bid,7000000,'pending')
        assert sandbox.execute('SELECT bidder_id FROM collector WHERE collector_id=?', (sale['collector_id'],)).fetchone()[0] == 3
        assert sandbox.execute('SELECT bid_amount FROM bid WHERE bid_id=?', (maya_bid,)).fetchone()[0] == 6500000
        assert sandbox.execute('SELECT status FROM artwork WHERE artwork_id=?', (art,)).fetchone()[0] == 'sold'
        assert sandbox.execute('SELECT status FROM auction WHERE auction_id=?', (auction,)).fetchone()[0] == 'closed'
        services.update_payment(sandbox, result['sale_id'], 'completed')
        assert sandbox.execute('SELECT payment_status FROM sale WHERE sale_id=?', (result['sale_id'],)).fetchone()[0] == 'completed'
        assert snapshot(main) == main_before
    finally:
        main.close()
        sandbox.close()

import pytest
from flask import session
from atelier import create_app, presentation


@pytest.fixture
def studio(tmp_path):
    return create_app({'TESTING': True, 'SECRET_KEY':'test-only-secret',
        'DATABASE':str(tmp_path/'main.sqlite'), 'PRESENTATION_DIR':str(tmp_path/'sandboxes'),
        'WTF_CSRF_ENABLED':False})


def login_as(client, user_id):
    with client.session_transaction() as sess:
        sess['user_id'] = user_id


def path_for(client, app):
    with client.session_transaction() as sess:
        token = sess['presentation_id']
    return __import__('pathlib').Path(app.config['PRESENTATION_DIR']) / f'{token}.sqlite'


def test_studio_access_and_schema_allowlist(studio):
    anonymous = studio.test_client()
    assert anonymous.get('/staff/presentation').status_code == 302
    assert anonymous.post('/staff/presentation/start').status_code == 302
    bidder = studio.test_client()
    login_as(bidder, 2)
    assert bidder.get('/staff/presentation').status_code == 403
    assert bidder.post('/staff/presentation/start').status_code == 403
    assert bidder.post('/staff/presentation/next', data={'expected_stage':'0'}).status_code == 403
    staff = studio.test_client()
    login_as(staff, 1)
    for view in ('walkthrough','database','rules','architecture'):
        assert staff.get(f'/staff/presentation?view={view}').status_code == 200
    assert staff.get('/staff/presentation?view=missing').status_code == 404
    assert staff.get('/staff/presentation?view=database&table=user_account').status_code == 404
    assert staff.get('/staff/presentation?view=database&table=artwork%3BDELETE%20FROM%20artist').status_code == 404
    conn = db.connect(studio.config['DATABASE'])
    try:
        secret_hash = conn.execute('SELECT password_hash FROM user_account WHERE user_id=1').fetchone()[0]
    finally:
        conn.close()
    for view in ('walkthrough','database','rules','architecture'):
        body = staff.get(f'/staff/presentation?view={view}').get_data(as_text=True)
        assert secret_hash not in body
        assert 'password_hash' not in body


def test_studio_requires_csrf_when_enabled(tmp_path):
    app = create_app({'TESTING':True,'SECRET_KEY':'csrf-test-key','DATABASE':str(tmp_path/'main.sqlite'),
                      'PRESENTATION_DIR':str(tmp_path/'sandboxes'),'WTF_CSRF_ENABLED':True})
    client = app.test_client()
    login_as(client,1)
    assert client.post('/staff/presentation/start').status_code == 400
    assert client.post('/staff/presentation/next',data={'expected_stage':'0'}).status_code == 400
    assert not list((tmp_path/'sandboxes').glob('*.sqlite'))
    import re
    login_page = client.get('/login').get_data(as_text=True)
    token = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', login_page).group(1)
    assert client.post('/staff/presentation/start',data={'csrf_token':token}).status_code == 302
    assert len(list((tmp_path/'sandboxes').glob('*.sqlite'))) == 1


def test_studio_steps_replay_isolation_and_reset(studio):
    first, second = studio.test_client(), studio.test_client()
    login_as(first,1)
    login_as(second,1)
    main = db.connect(studio.config['DATABASE'])
    tables = ('artwork','exhibition_artwork','appraisal','authentication','auction','auction_lot','bid','sale','collector')
    def snapshot(conn):
        return {table:[tuple(r) for r in conn.execute(f'SELECT * FROM {table} ORDER BY 1')] for table in tables}
    before = snapshot(main)
    assert first.post('/staff/presentation/start').status_code == 302
    first_path = path_for(first,studio)
    assert first_path.exists()
    assert second.post('/staff/presentation/start').status_code == 302
    second_path = path_for(second,studio)
    assert second_path != first_path and second_path.exists()
    for stage in range(8):
        assert first.post('/staff/presentation/next',data={'expected_stage':str(stage)}).status_code == 302
        conn = db.connect(first_path)
        state = dict(conn.execute('SELECT * FROM demo_state').fetchone())
        assert state['stage'] == stage + 1
        assert conn.execute('SELECT count(*) FROM demo_event').fetchone()[0] == stage + 1
        conn.close()
        # A second submit from a stale tab must leave state and history unchanged.
        assert first.post('/staff/presentation/next',data={'expected_stage':str(stage)}).status_code == 302
        conn = db.connect(first_path)
        assert conn.execute('SELECT count(*) FROM demo_event').fetchone()[0] == stage + 1
        assert conn.execute('SELECT stage FROM demo_state').fetchone()[0] == stage + 1
        conn.close()
    conn = db.connect(first_path)
    state = conn.execute('SELECT * FROM demo_state').fetchone()
    assert conn.execute('SELECT COUNT(*) FROM bid WHERE lot_id=?',(state['lot_id'],)).fetchone()[0] == 2
    sale = conn.execute('SELECT s.*, c.bidder_id FROM sale s JOIN collector c ON c.collector_id=s.collector_id WHERE sale_id=?',(state['sale_id'],)).fetchone()
    assert (sale['bidder_id'],sale['sale_price'],sale['payment_status']) == (3,7000000,'completed')
    assert conn.execute('SELECT status FROM artwork WHERE artwork_id=?',(state['artwork_id'],)).fetchone()[0] == 'sold'
    assert all(row['sql_text'] and row['read_sql'] and row['after_json'] for row in conn.execute('SELECT * FROM demo_event'))
    conn.close()
    isolated = db.connect(second_path)
    assert isolated.execute('SELECT stage FROM demo_state').fetchone()[0] == 0
    isolated.close()
    assert snapshot(main) == before
    assert first.post('/staff/presentation/start').status_code == 302
    replacement = path_for(first,studio)
    assert replacement != first_path and not first_path.exists() and second_path.exists()
    reset = db.connect(replacement)
    assert reset.execute('SELECT stage FROM demo_state').fetchone()[0] == 0
    assert reset.execute('SELECT COUNT(*) FROM demo_event').fetchone()[0] == 0
    reset.close()
    assert snapshot(main) == before
    main.close()


def test_failed_staged_step_does_not_publish(studio, monkeypatch):
    client = studio.test_client()
    login_as(client,1)
    client.post('/staff/presentation/start')
    with client.session_transaction() as sess:
        token = sess['presentation_id']
    path = path_for(client,studio)
    conn = db.connect(path)
    before = [tuple(row) for row in conn.execute('SELECT * FROM artwork ORDER BY artwork_id')]
    conn.close()
    perform = presentation._perform
    def fail_after_mutation(conn, stage, state):
        perform(conn, stage, state)
        raise RuntimeError('forced failure after staged commit')
    monkeypatch.setattr(presentation, '_perform', fail_after_mutation)
    with studio.test_request_context():
        session['presentation_id'] = token
        with pytest.raises(RuntimeError, match='forced failure'):
            presentation.run_step(0)
    conn = db.connect(path)
    assert conn.execute('SELECT stage FROM demo_state').fetchone()[0] == 0
    assert conn.execute('SELECT COUNT(*) FROM demo_event').fetchone()[0] == 0
    assert [tuple(row) for row in conn.execute('SELECT * FROM artwork ORDER BY artwork_id')] == before
    conn.close()


def test_concurrent_duplicate_step_is_applied_once(studio):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    client = studio.test_client()
    login_as(client,1)
    client.post('/staff/presentation/start')
    with client.session_transaction() as sess:
        token = sess['presentation_id']
    gate = Barrier(2)
    def step(_):
        with studio.test_request_context():
            session['presentation_id'] = token
            gate.wait()
            try:
                return presentation.run_step(0)
            except services.DomainError:
                return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(step, range(2)), key=lambda x: x or 0) == [None,1]
    conn = db.connect(path_for(client,studio))
    assert conn.execute('SELECT stage FROM demo_state').fetchone()[0] == 1
    assert conn.execute('SELECT COUNT(*) FROM demo_event').fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM artwork WHERE title='A New Perspective'").fetchone()[0] == 1
    conn.close()
