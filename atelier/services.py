import sqlite3
from contextlib import contextmanager


class DomainError(ValueError):
    """An operation violates an auction rule."""


@contextmanager
def _transaction(conn):
    if conn.in_transaction:
        raise DomainError('Finish the current transaction before this operation')
    try:
        conn.execute('BEGIN IMMEDIATE')
        yield
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        raise DomainError(str(exc)) from exc
    except Exception:
        conn.rollback()
        raise


def open_auction(conn, auction_id):
    with _transaction(conn):
        auction = conn.execute('SELECT status FROM auction WHERE auction_id=?', (auction_id,)).fetchone()
        if auction is None:
            raise DomainError('Auction not found')
        if auction['status'] != 'draft':
            raise DomainError('Only a draft auction can be opened')
        lots = conn.execute('SELECT l.lot_id, l.artwork_id, l.status, w.status AS artwork_status FROM auction_lot l JOIN artwork w ON w.artwork_id=l.artwork_id WHERE l.auction_id=?', (auction_id,)).fetchall()
        if not lots:
            raise DomainError('Add at least one lot before opening the auction')
        for lot in lots:
            if lot['status'] != 'draft' or lot['artwork_status'] != 'available' or conn.execute("SELECT 1 FROM auction_lot WHERE artwork_id=? AND status='open'", (lot['artwork_id'],)).fetchone():
                raise DomainError('Every artwork must be available and not listed in another open lot')
        conn.execute("UPDATE auction SET status='open' WHERE auction_id=?", (auction_id,))
        for lot in lots:
            conn.execute("UPDATE auction_lot SET status='open' WHERE lot_id=?", (lot['lot_id'],))
            conn.execute("UPDATE artwork SET status='at_auction' WHERE artwork_id=?", (lot['artwork_id'],))


def place_bid(conn, lot_id, bidder_id, amount):
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise DomainError('Bid amount must be a non-negative integer in paise')
    with _transaction(conn):
        row = conn.execute('SELECT l.status, l.starting_price, a.status AS auction_status FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=?', (lot_id,)).fetchone()
        if not row or row['status'] != 'open' or row['auction_status'] != 'open':
            raise DomainError('This lot is not open for bidding')
        if not conn.execute('SELECT 1 FROM bidder WHERE bidder_id=?', (bidder_id,)).fetchone():
            raise DomainError('Bidder not found')
        highest = conn.execute('SELECT MAX(bid_amount) FROM bid WHERE lot_id=?', (lot_id,)).fetchone()[0]
        if amount < row['starting_price']:
            raise DomainError('Bid must meet the starting price')
        if highest is not None and amount <= highest:
            raise DomainError('Bid must exceed the current highest bid')
        return conn.execute('INSERT INTO bid(lot_id,bidder_id,bid_amount) VALUES (?,?,?)', (lot_id,bidder_id,amount)).lastrowid


def close_lot(conn, lot_id):
    with _transaction(conn):
        lot = conn.execute('SELECT l.*, a.status AS auction_status FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=?', (lot_id,)).fetchone()
        if lot is None:
            raise DomainError('Lot not found')
        if lot['status'] in ('sold','unsold'):
            sale = conn.execute('SELECT s.sale_id FROM sale s JOIN bid b ON b.bid_id=s.bid_id WHERE b.lot_id=?', (lot_id,)).fetchone()
            return {'status': lot['status'], 'sale_id': sale['sale_id'] if sale else None}
        if lot['status'] != 'open' or lot['auction_status'] != 'open':
            raise DomainError('Only an open lot can be closed')
        winner = conn.execute('SELECT * FROM bid WHERE lot_id=? ORDER BY bid_amount DESC, bid_id DESC LIMIT 1', (lot_id,)).fetchone()
        sale_id = None
        status = 'unsold'
        if winner and winner['bid_amount'] >= lot['reserve_price']:
            conn.execute('INSERT INTO collector(bidder_id,name,email,phone,address) SELECT bidder_id,name,email,phone,address FROM bidder WHERE bidder_id=? ON CONFLICT(bidder_id) DO NOTHING', (winner['bidder_id'],))
            collector = conn.execute('SELECT collector_id FROM collector WHERE bidder_id=?', (winner['bidder_id'],)).fetchone()
            sale_id = conn.execute("INSERT INTO sale(bid_id,collector_id,sale_price,sale_date,payment_status) VALUES(?,?,?,date('now'),'pending')", (winner['bid_id'],collector['collector_id'],winner['bid_amount'])).lastrowid
            status = 'sold'
        conn.execute('UPDATE auction_lot SET status=? WHERE lot_id=?', (status, lot_id))
        conn.execute('UPDATE artwork SET status=? WHERE artwork_id=?', ('sold' if status=='sold' else 'available', lot['artwork_id']))
        if not conn.execute("SELECT 1 FROM auction_lot WHERE auction_id=? AND status IN ('open','draft')", (lot['auction_id'],)).fetchone():
            conn.execute("UPDATE auction SET status='closed' WHERE auction_id=?", (lot['auction_id'],))
        return {'status': status, 'sale_id': sale_id}


def update_payment(conn, sale_id, status):
    if status not in ('pending', 'completed'):
        raise DomainError('Payment status must be pending or completed')
    with _transaction(conn):
        if not conn.execute('SELECT 1 FROM sale WHERE sale_id=?', (sale_id,)).fetchone():
            raise DomainError('Sale not found')
        conn.execute('UPDATE sale SET payment_status=? WHERE sale_id=?', (status,sale_id))
