from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import sqlite3

import pytest
from werkzeug.security import check_password_hash
from atelier import db, seed, services


@pytest.fixture
def database(tmp_path):
    path = tmp_path / 'test.sqlite'
    conn = db.connect(path)
    db.init_db(conn)
    seed.seed_db(conn)
    yield path, conn
    conn.close()


def test_seed_is_coherent_and_idempotent(database):
    _, conn = database
    before = [tuple(row) for row in conn.execute('SELECT * FROM sale ORDER BY sale_id')]
    seed.seed_db(conn)
    assert [tuple(row) for row in conn.execute('SELECT * FROM sale ORDER BY sale_id')] == before
    assert [tuple(r) for r in conn.execute('SELECT auction_id,status FROM auction ORDER BY auction_id')] == [(1,'open'),(2,'draft'),(3,'closed')]
    assert [tuple(r) for r in conn.execute('SELECT c.name,s.payment_status FROM sale s JOIN collector c ON c.collector_id=s.collector_id ORDER BY s.sale_id')] == [('Maya Sharma','completed'),('Arjun Patel','pending')]
    assert conn.execute('SELECT COUNT(*) FROM bid WHERE bidder_id=3').fetchone()[0] == 0
    assert conn.execute('SELECT status FROM auction_lot WHERE lot_id=303').fetchone()[0] == 'unsold'
    assert conn.execute('SELECT status FROM artwork WHERE artwork_id=3').fetchone()[0] == 'available'
    for email,password in [('admin@atelier.example','AdminDemo!2026'),('sara@atelier.example','BidderDemo!2026')]:
        assert check_password_hash(conn.execute('SELECT password_hash FROM user_account WHERE email=?',(email,)).fetchone()[0],password)


def test_bidding_rules_and_sql_trigger(database):
    _, conn = database
    for amount in (5500000, 4999999, 5500000.5, -1, True):
        with pytest.raises(services.DomainError):
            services.place_bid(conn,101,3,amount)
    with pytest.raises(services.DomainError):
        services.place_bid(conn,301,3,6000000)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute('INSERT INTO bid(lot_id,bidder_id,bid_amount) VALUES(101,3,5500000)')
    conn.rollback()
    bid_id = services.place_bid(conn,101,3,7000000)
    assert conn.execute('SELECT bid_amount FROM bid WHERE bid_id=?',(bid_id,)).fetchone()[0] == 7000000
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute('UPDATE bid SET bid_amount=1 WHERE bid_id=?',(bid_id,))
    conn.rollback()


def test_closing_sale_and_reserve_miss(database):
    _, conn = database
    bid_id = services.place_bid(conn,101,3,7000000)
    result = services.close_lot(conn,101)
    assert result == services.close_lot(conn,101)
    sale = conn.execute('SELECT s.*,c.bidder_id FROM sale s JOIN collector c ON c.collector_id=s.collector_id WHERE s.sale_id=?',(result['sale_id'],)).fetchone()
    assert (result['status'],sale['bid_id'],sale['bidder_id'],sale['sale_price']) == ('sold',bid_id,3,7000000)
    assert conn.execute('SELECT status FROM artwork WHERE artwork_id=4').fetchone()[0] == 'sold'
    assert services.close_lot(conn,102) == {'status':'unsold','sale_id':None}
    assert conn.execute('SELECT status FROM auction WHERE auction_id=1').fetchone()[0] == 'closed'
    assert conn.execute('SELECT status FROM artwork WHERE artwork_id=5').fetchone()[0] == 'available'
    services.update_payment(conn,result['sale_id'],'completed')
    assert conn.execute('SELECT payment_status FROM sale WHERE sale_id=?',(result['sale_id'],)).fetchone()[0] == 'completed'
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE auction_lot SET status='open' WHERE lot_id=101")
    conn.rollback()


def test_sale_cannot_be_forged(database):
    _, conn = database
    bid = conn.execute('SELECT bid_id FROM bid WHERE lot_id=101 ORDER BY bid_amount DESC LIMIT 1').fetchone()[0]
    collector = conn.execute('SELECT collector_id FROM collector WHERE bidder_id=1').fetchone()[0]
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO sale(bid_id,collector_id,sale_price,sale_date,payment_status) VALUES(?,?,?,date('now'),'pending')",(bid,collector,5500000))
    conn.rollback()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute('DELETE FROM artist WHERE artist_id=1')
    conn.rollback()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO exhibition VALUES(99,1,1,'Bad date','2026-02-30','2026-03-02','test')")
    conn.rollback()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO auction_lot(auction_id,artwork_id,lot_number,starting_price,reserve_price) VALUES(2,8,3,1.5,10)")
    conn.rollback()


def test_concurrent_bids_and_closes_are_serialized(database):
    path, conn = database
    gate = Barrier(2)
    def bid():
        c = db.connect(path)
        try:
            gate.wait()
            try:
                return services.place_bid(c,101,3,7000000)
            except services.DomainError:
                return None
        finally:
            c.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        bids = list(pool.map(lambda _: bid(),range(2)))
    assert sum(x is not None for x in bids) == 1
    gate = Barrier(2)
    def close():
        c = db.connect(path)
        try:
            gate.wait()
            return services.close_lot(c,101)
        finally:
            c.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: close(),range(2)))
    assert results[0] == results[1] and results[0]['status'] == 'sold'
    assert conn.execute('SELECT COUNT(*) FROM sale s JOIN bid b ON b.bid_id=s.bid_id WHERE b.lot_id=101').fetchone()[0] == 1


def test_opening_requires_available_work_and_is_atomic(database):
    _, conn = database
    conn.execute('UPDATE artwork SET status=\'sold\' WHERE artwork_id=6')
    conn.commit()
    with pytest.raises(services.DomainError):
        services.open_auction(conn,2)
    assert conn.execute('SELECT status FROM auction WHERE auction_id=2').fetchone()[0] == 'draft'
    assert conn.execute('SELECT COUNT(*) FROM auction_lot WHERE auction_id=2 AND status=\'open\'').fetchone()[0] == 0
    conn.execute('UPDATE artwork SET status=\'available\' WHERE artwork_id=6')
    conn.commit()
    services.open_auction(conn,2)
    assert conn.execute('SELECT COUNT(*) FROM auction_lot WHERE auction_id=2 AND status=\'open\'').fetchone()[0] == 2
    with pytest.raises(services.DomainError):
        services.open_auction(conn,2)


def test_close_rolls_back_all_changes_when_sale_insert_fails(database):
    _, conn = database
    services.place_bid(conn,101,3,7000000)
    before_bids = conn.execute('SELECT COUNT(*) FROM bid WHERE lot_id=101').fetchone()[0]
    # Simulate a late database failure after close_lot has created the collector.
    conn.execute("CREATE TRIGGER simulate_sale_failure BEFORE INSERT ON sale BEGIN SELECT RAISE(ABORT,'simulated sale failure'); END")
    conn.commit()
    with pytest.raises(services.DomainError, match='simulated sale failure'):
        services.close_lot(conn,101)
    assert conn.execute('SELECT COUNT(*) FROM collector WHERE bidder_id=3').fetchone()[0] == 0
    assert conn.execute('SELECT COUNT(*) FROM sale s JOIN bid b ON b.bid_id=s.bid_id WHERE b.lot_id=101').fetchone()[0] == 0
    assert conn.execute('SELECT status FROM auction_lot WHERE lot_id=101').fetchone()[0] == 'open'
    assert conn.execute('SELECT status FROM artwork WHERE artwork_id=4').fetchone()[0] == 'at_auction'
    assert conn.execute('SELECT status FROM auction WHERE auction_id=1').fetchone()[0] == 'open'
    assert conn.execute('SELECT COUNT(*) FROM bid WHERE lot_id=101').fetchone()[0] == before_bids


def test_junctions_foreign_keys_active_listing_and_lot_guards(database):
    _, conn = database
    for sql, params in [
        ('INSERT INTO artist_gallery VALUES(?,?,?,?,?)',(1,1,'2020-01-01',None,20)),
        ('INSERT INTO exhibition_artwork VALUES(?,?,?)',(1,4,'duplicate')),
        ('INSERT INTO artwork(artist_id,title) VALUES(?,?)',(None,'No artist')),
        ('INSERT INTO exhibition(gallery_id,curator_id,title,start_date,end_date) VALUES(?,?,?,?,?)',(1,None,'No curator','2026-01-01','2026-02-01')),
        ('INSERT INTO auction_lot(auction_id,artwork_id,lot_number,starting_price,reserve_price) VALUES(?,?,?,?,?)',(1,8,3,100,100)),
        ('DELETE FROM auction_lot WHERE lot_id=?',(101,)),
    ]:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(sql,params)
        conn.rollback()
    # The unique partial index is independently effective even if a work's
    # availability were changed by another SQL client.
    conn.execute("INSERT INTO auction_lot(lot_id,auction_id,artwork_id,lot_number,starting_price,reserve_price) VALUES(999,2,4,99,100,100)")
    conn.execute("UPDATE auction SET status='open' WHERE auction_id=2")
    conn.execute("UPDATE artwork SET status='available' WHERE artwork_id=4")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE auction_lot SET status='open' WHERE lot_id=999")
    conn.rollback()


def test_sale_correct_winner_amount_and_history_immutable(database):
    _, conn = database
    # A reserve-met highest bid with the wrong collector or amount must fail.
    services.place_bid(conn,101,3,7000000)
    conn.execute("INSERT INTO collector(bidder_id,name) VALUES(3,'Sara Khan')")
    conn.commit()
    high_bid = conn.execute('SELECT bid_id FROM bid WHERE lot_id=101 ORDER BY bid_amount DESC LIMIT 1').fetchone()[0]
    wrong_collector = conn.execute('SELECT collector_id FROM collector WHERE bidder_id=1').fetchone()[0]
    correct_collector = conn.execute('SELECT collector_id FROM collector WHERE bidder_id=3').fetchone()[0]
    for collector, price in [(wrong_collector,7000000),(correct_collector,6999999)]:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO sale(bid_id,collector_id,sale_price,sale_date) VALUES(?,?,?,date('now'))",(high_bid,collector,price))
        conn.rollback()
    result = services.close_lot(conn,101)
    for column, value in [('sale_price',1),('collector_id',wrong_collector),('bid_id',1)]:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(f'UPDATE sale SET {column}=? WHERE sale_id=?',(value,result['sale_id']))
        conn.rollback()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute('DELETE FROM sale WHERE sale_id=?',(result['sale_id'],))
    conn.rollback()
