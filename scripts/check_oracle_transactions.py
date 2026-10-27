"""Exercise Oracle locks, rejection, rollback and repeat closure using fictional new records."""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from atelier.db import Connection, IntegrityError
from atelier import services


def main():
    checks=[]
    conn=Connection()
    art=[]
    for n in (1,2):
        art.append(conn.execute("INSERT INTO artwork(artist_id,title,year_created,medium,image_path) VALUES(1,?,2026,'Oil on canvas','images/artwork-02.webp')",(f'Transaction demonstration {conn.next_id()} / {n}',)).lastrowid)
    auction=conn.execute('INSERT INTO auction(gallery_id,title,"DATE",venue) VALUES(1,?,TRUNC(SYSDATE),\'Atelier Mumbai\')',(f'Transaction demonstration {conn.next_id()}',)).lastrowid
    lots=[conn.execute('INSERT INTO auction_lot(auction_id,artwork_id,lot_number,starting_price,reserve_price) VALUES(?,?,?,?,?)',
                      (auction,art[i],i+1,5000000 if i==0 else 1000000,6000000 if i==0 else 2000000)).lastrowid for i in range(2)]
    buyer=conn.execute('INSERT INTO bidder(name,email,address) VALUES(?,?,?)',('Transaction Demo Bidder',f'transaction-{conn.next_id()}@atelier.example','Mumbai')).lastrowid
    conn.commit()
    services.open_auction(conn,auction)
    try:
        services.place_bid(conn,lots[0],1,4999999)
        raise AssertionError('Low bid accepted')
    except services.DomainError:
        checks.append('Bid below starting price rejected')
    barrier=Barrier(2)
    def place(bidder):
        c=Connection()
        try:
            barrier.wait(timeout=15)
            return ('accepted',services.place_bid(c,lots[0],bidder,6000000))
        except services.DomainError:
            return ('rejected',None)
        finally:
            c.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes=list(pool.map(place,(1,2)))
    assert sorted(o[0] for o in outcomes)==['accepted','rejected'],outcomes
    checks.append('Concurrent equal bids: exactly one accepted, one rejected')
    services.place_bid(conn,lots[0],buyer,7000000)
    original=conn.execute
    def fail_sale(sql,params=()):
        if sql.startswith('INSERT INTO sale'):
            raise RuntimeError('Intentional rollback demonstration')
        return original(sql,params)
    conn.execute=fail_sale
    try:
        services.close_lot(conn,lots[0])
        raise AssertionError('Injected failure was not reached')
    except RuntimeError:
        pass
    finally:
        conn.execute=original
    assert conn.execute('SELECT COUNT(*) FROM collector WHERE bidder_id=?',(buyer,)).fetchone()[0]==0
    assert conn.execute('SELECT status FROM auction_lot WHERE lot_id=?',(lots[0],)).fetchone()[0]=='open'
    checks.append('Failed close rolls back new collector, sale and lot/artwork status')
    barrier=Barrier(2)
    def close(_):
        c=Connection()
        try:
            barrier.wait(timeout=15)
            return services.close_lot(c,lots[0])
        finally:
            c.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        closed=list(pool.map(close,(1,2)))
    assert closed[0]==closed[1] and closed[0]['status']=='sold',closed
    sale=closed[0]['sale_id']
    assert conn.execute('SELECT COUNT(*) FROM sale s JOIN bid b ON b.bid_id=s.bid_id WHERE b.lot_id=?',(lots[0],)).fetchone()[0]==1
    checks.append('Concurrent closure is idempotent: one sale, same result to both callers')
    services.place_bid(conn,lots[1],1,1500000)
    reserve=services.close_lot(conn,lots[1])
    assert reserve=={'status':'unsold','sale_id':None},reserve
    checks.append('Reserve not met: unsold lot, no sale, artwork available')
    assert conn.execute('SELECT status FROM artwork WHERE artwork_id=?',(art[1],)).fetchone()[0]=='available'
    for sql,params in [("UPDATE bid SET bid_amount=bid_amount+1 WHERE lot_id=?",(lots[0],)),
                       ("DELETE FROM sale WHERE sale_id=?",(sale,)),
                       ("UPDATE sale SET sale_price=sale_price+1 WHERE sale_id=?",(sale,)),
                       ("INSERT INTO artwork(artist_id,title) VALUES(99999999,'Invalid parent')",())]:
        try:
            conn.execute(sql,params)
            conn.rollback()
            raise AssertionError('Protected mutation accepted: '+sql)
        except IntegrityError:
            conn.rollback()
    checks.append('Database rejects bid edits, sale deletion/price edits and missing foreign keys')
    conn.close()
    fresh=Connection()
    assert fresh.execute('SELECT COUNT(*) FROM sale WHERE sale_id=?',(sale,)).fetchone()[0]==1
    fresh.close()
    checks.append('Finalized sale persists across independent Oracle connections')
    output=dict(engine='Oracle',checks=checks,auction_id=auction,lot_ids=lots,sale_id=sale)
    (ROOT/'docs'/'assignment'/'TRANSACTION_VERIFICATION.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    print('\n'.join(checks))


if __name__=='__main__':
    main()
