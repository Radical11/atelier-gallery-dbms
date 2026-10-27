"""Public browsing, authenticated demonstration actions and the staff data desk."""
from functools import wraps
import sqlite3

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db
from . import services
from .queries import QUERIES
from .registry import TABLES, MONEY, READONLY, editable_fields, label, paise, parse_fields, primary_keys, table_info

bp = Blueprint('web', __name__)


def money(value):
    if value is None:
        return '—'
    # Indian digit grouping keeps large auction prices familiar in the INR demo.
    value = int(value)
    sign = '-' if value < 0 else ''
    whole, fraction = divmod(abs(value), 100)
    digits = str(whole)
    tail, head = digits[-3:], digits[:-3]
    groups = []
    while head:
        groups.insert(0, head[-2:])
        head = head[:-2]
    amount = ','.join(groups + [tail])
    return f'{sign}₹{amount}' + (f'.{fraction:02}' if fraction else '')


def rows(sql, params=()):
    return [dict(r) for r in get_db().execute(sql, params)]


def one(sql, params=()):
    row = get_db().execute(sql, params).fetchone()
    if row is None:
        abort(404)
    return dict(row)


@bp.before_app_request
def load_user():
    g.user = None
    uid = session.get('user_id')
    if uid:
        row = get_db().execute('''SELECT u.user_id, u.email, u.role, u.bidder_id,
            COALESCE(b.name, 'Gallery team') AS name
            FROM user_account u LEFT JOIN bidder b ON b.bidder_id=u.bidder_id WHERE u.user_id=?''', (uid,)).fetchone()
        if row:
            g.user = dict(row)


@bp.app_context_processor
def shared_context():
    return dict(current_user=g.get('user'), tables=[dict(name=k, label=v) for k,v in TABLES.items()])


def require_role(role=None):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not g.user:
                return redirect(url_for('web.login', next=request.path))
            if role and g.user['role'] != role:
                abort(403)
            return view(*args, **kwargs)
        return wrapper
    return decorator


ART = '''SELECT w.*, a.name AS artist_name, a.nationality AS artist_nationality
         FROM artwork w JOIN artist a ON a.artist_id=w.artist_id'''
EXHIBITIONS = '''SELECT e.*, g.name AS gallery_name, g.city, c.name AS curator_name,
    (SELECT COUNT(*) FROM exhibition_artwork ea WHERE ea.exhibition_id=e.exhibition_id) AS artwork_count,
    COALESCE((SELECT w.image_path FROM exhibition_artwork ea JOIN artwork w ON w.artwork_id=ea.artwork_id
    WHERE ea.exhibition_id=e.exhibition_id ORDER BY ea.display_position LIMIT 1), 'images/artwork-04.webp') AS image_path
    FROM exhibition e JOIN gallery g ON g.gallery_id=e.gallery_id JOIN curator c ON c.curator_id=e.curator_id'''
AUCTIONS = '''SELECT a.*, g.name AS gallery_name,
    (SELECT COUNT(*) FROM auction_lot l WHERE l.auction_id=a.auction_id) AS lot_count,
    COALESCE((SELECT w.image_path FROM auction_lot l JOIN artwork w ON w.artwork_id=l.artwork_id
    WHERE l.auction_id=a.auction_id ORDER BY l.lot_number LIMIT 1), 'images/artwork-03.webp') AS image_path
    FROM auction a JOIN gallery g ON g.gallery_id=a.gallery_id'''


@bp.route('/')
def home():
    return render_template('home.html', featured=rows(ART+' ORDER BY w.artwork_id LIMIT 6'),
        exhibitions=rows(EXHIBITIONS+' ORDER BY e.exhibition_id LIMIT 3'),
        auctions=rows(AUCTIONS+" ORDER BY CASE a.status WHEN 'open' THEN 0 WHEN 'draft' THEN 1 ELSE 2 END LIMIT 3"),
        stats={key:get_db().execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] for key,table in
               [('artworks','artwork'),('artists','artist'),('exhibitions','exhibition'),('auctions','auction')]})


@bp.route('/collection')
def collection():
    filters = {k:request.args.get(k,'').strip() for k in ('q','artist','medium','status')}
    conditions, params = [], []
    if filters['q']:
        conditions.append('(w.title LIKE ? OR a.name LIKE ? OR w.description LIKE ?)')
        params += ['%'+filters['q']+'%'] * 3
    for name in ('artist','medium','status'):
        if filters[name]:
            conditions.append(f'w.{"artist_id" if name=="artist" else name} = ?')
            params.append(filters[name])
    sql = ART + (' WHERE '+' AND '.join(conditions) if conditions else '') + ' ORDER BY w.artwork_id'
    return render_template('collection.html', artworks=rows(sql,params), filters=filters,
        artists=rows('SELECT artist_id,name FROM artist ORDER BY name'),
        media=[r['medium'] for r in rows('SELECT DISTINCT medium FROM artwork ORDER BY medium')])


@bp.route('/collection/<int:artwork_id>')
def artwork_detail(artwork_id):
    artwork = one(ART+' WHERE w.artwork_id=?',(artwork_id,))
    artwork.update(one('SELECT biography, birth_date, death_date, nationality FROM artist WHERE artist_id=?',(artwork['artist_id'],)))
    return render_template('artwork.html', artwork=artwork,
        exhibitions=rows(EXHIBITIONS+''' JOIN exhibition_artwork ea2 ON ea2.exhibition_id=e.exhibition_id
            WHERE ea2.artwork_id=? ORDER BY e.start_date DESC''',(artwork_id,)),
        appraisals=rows('''SELECT p.*, e.name AS expert_name FROM appraisal p JOIN art_expert e ON e.expert_id=p.expert_id
            WHERE p.artwork_id=? ORDER BY p.appraisal_date DESC''',(artwork_id,)),
        authentications=rows('''SELECT t.*, e.name AS expert_name FROM authentication t JOIN art_expert e ON e.expert_id=t.expert_id
            WHERE t.artwork_id=? ORDER BY t.authentication_date DESC''',(artwork_id,)),
        lots=rows('''SELECT l.*, a.title AS auction_title,a.status AS auction_status,
            (SELECT MAX(b.bid_amount) FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid
            FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.artwork_id=?''',(artwork_id,)))


@bp.route('/exhibitions')
def exhibitions():
    return render_template('exhibitions.html',exhibitions=rows(EXHIBITIONS+' ORDER BY e.start_date DESC'))


@bp.route('/exhibitions/<int:exhibition_id>')
def exhibition_detail(exhibition_id):
    return render_template('exhibition.html',exhibition=one(EXHIBITIONS+' WHERE e.exhibition_id=?',(exhibition_id,)),
        artworks=rows(ART+''' JOIN exhibition_artwork ea ON ea.artwork_id=w.artwork_id
            WHERE ea.exhibition_id=? ORDER BY ea.display_position''',(exhibition_id,)))


@bp.route('/auctions')
def auctions():
    return render_template('auctions.html',auctions=rows(AUCTIONS+" ORDER BY CASE a.status WHEN 'open' THEN 0 WHEN 'draft' THEN 1 ELSE 2 END,a.auction_id"))


@bp.route('/auctions/<int:auction_id>')
def auction_detail(auction_id):
    auction = one(AUCTIONS+' WHERE a.auction_id=?',(auction_id,))
    lots = rows('''SELECT l.*, w.title, w.title AS artwork_title,w.image_path,w.medium,w.year_created,a.name AS artist_name,
        (SELECT MAX(b.bid_amount) FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid,
        (SELECT COUNT(*) FROM bid b WHERE b.lot_id=l.lot_id) AS bid_count,
        COALESCE((SELECT MAX(b.bid_amount)+1 FROM bid b WHERE b.lot_id=l.lot_id),l.starting_price) AS min_bid
        FROM auction_lot l JOIN artwork w ON w.artwork_id=l.artwork_id JOIN artist a ON a.artist_id=w.artist_id
        WHERE l.auction_id=? ORDER BY l.lot_number''',(auction_id,))
    bids = {l['lot_id']:rows('''SELECT b.*, r.name AS bidder_name FROM bid b JOIN bidder r ON r.bidder_id=b.bidder_id
            WHERE b.lot_id=? ORDER BY b.bid_amount DESC,b.bid_id DESC''',(l['lot_id'],)) for l in lots}
    return render_template('auction.html',auction=auction,lots=lots,bids=bids,
        my_bidder_id=g.user['bidder_id'] if g.user else None)


@bp.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email','').strip().lower()
        password=request.form.get('password','')
        user=get_db().execute('SELECT * FROM user_account WHERE email=?',(email,)).fetchone()
        if user and check_password_hash(user['password_hash'],password):
            session.clear()
            session['user_id']=user['user_id']
            target=request.args.get('next','')
            if not target.startswith('/') or target.startswith('//') or '\\' in target:
                target=url_for('web.admin' if user['role']=='staff' else 'web.account')
            return redirect(target)
        flash('The email or password is incorrect. Try a demo account below.','error')
        return render_template('login.html'),401
    return render_template('login.html')


@bp.post('/logout')
def logout():
    session.clear()
    flash('You have signed out.','success')
    return redirect(url_for('web.home'))


@bp.route('/account')
@require_role('bidder')
def account():
    bidder_id=g.user['bidder_id']
    return render_template('account.html',bidder=one('SELECT * FROM bidder WHERE bidder_id=?',(bidder_id,)),
        bids=rows('''SELECT b.*, w.title AS artwork_title,w.image_path,a.title AS auction_title,a.auction_id,
            l.lot_number,l.status AS lot_status,
            (SELECT MAX(b2.bid_amount) FROM bid b2 WHERE b2.lot_id=l.lot_id) AS highest_bid
            FROM bid b JOIN auction_lot l ON l.lot_id=b.lot_id JOIN artwork w ON w.artwork_id=l.artwork_id
            JOIN auction a ON a.auction_id=l.auction_id WHERE b.bidder_id=? ORDER BY b.bid_id DESC''',(bidder_id,)),
        sales=rows('''SELECT s.*, w.title AS artwork_title,w.image_path,a.title AS auction_title,a.auction_id
            FROM sale s JOIN bid b ON b.bid_id=s.bid_id JOIN auction_lot l ON l.lot_id=b.lot_id
            JOIN artwork w ON w.artwork_id=l.artwork_id JOIN auction a ON a.auction_id=l.auction_id
            WHERE b.bidder_id=? ORDER BY s.sale_id DESC''',(bidder_id,)))


@bp.post('/lots/<int:lot_id>/bid')
@require_role('bidder')
def bid(lot_id):
    lot=one('SELECT auction_id FROM auction_lot WHERE lot_id=?',(lot_id,))
    try:
        services.place_bid(get_db(),lot_id,g.user['bidder_id'],paise(request.form.get('amount','')))
        flash('Your bid has been placed. You are now the highest bidder.','success')
    except (ValueError,services.DomainError,sqlite3.IntegrityError) as error:
        flash(str(error),'error')
    except sqlite3.OperationalError:
        flash('The bidding room is busy. Refresh and try your bid again.','error')
    return redirect(url_for('web.auction_detail',auction_id=lot['auction_id'])+f'#lot-{lot_id}')


@bp.post('/staff/auctions/<int:auction_id>/open')
@require_role('staff')
def open_auction(auction_id):
    one('SELECT auction_id FROM auction WHERE auction_id=?',(auction_id,))
    try:
        services.open_auction(get_db(),auction_id)
        flash('The auction is open for bidding.','success')
    except (services.DomainError,sqlite3.IntegrityError) as error:
        flash(str(error),'error')
    return redirect(url_for('web.auction_detail',auction_id=auction_id))


@bp.post('/staff/lots/<int:lot_id>/close')
@require_role('staff')
def close_lot(lot_id):
    lot=one('SELECT auction_id FROM auction_lot WHERE lot_id=?',(lot_id,))
    try:
        result=services.close_lot(get_db(),lot_id)
        flash('Lot sold. Its winning bid and collector are recorded.' if result['status']=='sold'
              else 'Lot closed unsold. No qualifying reserve bid was received.','success')
    except (services.DomainError,sqlite3.IntegrityError) as error:
        flash(str(error),'error')
    return redirect(url_for('web.auction_detail',auction_id=lot['auction_id'])+f'#lot-{lot_id}')


@bp.post('/staff/sales/<int:sale_id>/payment')
@require_role('staff')
def payment(sale_id):
    one('SELECT sale_id FROM sale WHERE sale_id=?',(sale_id,))
    try:
        services.update_payment(get_db(),sale_id,request.form.get('status',''))
        flash('Payment status updated. Collector and revenue reports now reflect it.','success')
    except (services.DomainError,sqlite3.IntegrityError) as error:
        flash(str(error),'error')
    return redirect(url_for('web.admin_table',table='sale'))


@bp.route('/staff')
@require_role('staff')
def admin():
    return render_template('admin/index.html',counts=[dict(label=v,table=k,value=get_db().execute(f'SELECT COUNT(*) FROM {k}').fetchone()[0]) for k,v in TABLES.items()],
        recent_sales=rows('''SELECT s.*,w.title AS artwork_title,c.name AS collector_name,a.title AS auction_title
            FROM sale s JOIN bid b ON b.bid_id=s.bid_id JOIN auction_lot l ON l.lot_id=b.lot_id
            JOIN artwork w ON w.artwork_id=l.artwork_id JOIN collector c ON c.collector_id=s.collector_id
            JOIN auction a ON a.auction_id=l.auction_id ORDER BY s.sale_id DESC LIMIT 5'''),
        auctions=rows(AUCTIONS+' ORDER BY a.auction_id'))


def checked_table(table):
    if table not in TABLES:
        abort(404)
    return table


def key_for(row,pk):
    return '~'.join(str(row[k]) for k in pk)


def find_record(table,key):
    pk=primary_keys(get_db(),table)
    parts=key.split('~')
    if len(parts)!=len(pk) or any(not p.isdigit() for p in parts):
        abort(404)
    where=' AND '.join(f'{k}=?' for k in pk)
    return one(f'SELECT * FROM {table} WHERE {where}',parts),where,parts


@bp.route('/staff/data/<table>')
@require_role('staff')
def admin_table(table):
    checked_table(table)
    data=rows(f'SELECT * FROM {table} ORDER BY 1 DESC')
    columns=[c['name'] for c in table_info(get_db(),table)]
    pk=primary_keys(get_db(),table)
    display=[]
    for row in data:
        item=dict(values=[money(row[c]) if c in MONEY else ('—' if row[c] is None else str(row[c])) for c in columns],key=key_for(row,pk))
        if table=='sale':
            item.update(sale_id=row['sale_id'],payment_status=row['payment_status'])
        display.append(item)
    return render_template('admin/table.html',table=table,label=TABLES[table],columns=[label(c) for c in columns],
        rows=data,display_rows=display,fields=editable_fields(get_db(),table),pk=pk,readonly=table in READONLY,
        key_for=lambda r:key_for(r,pk))


def friendly_integrity(error):
    message=str(error)
    if 'FOREIGN KEY' in message:
        return 'This record is referenced elsewhere. Keep it to preserve its relationships and history.'
    if 'UNIQUE constraint' in message:
        return 'That combination already exists. Check the linked records, lot number, email, or certificate number.'
    if 'CHECK constraint' in message:
        return 'A database rule rejected this value. Check dates, amounts, status, and required relationships.'
    return message


def manage_form(table,key=None):
    checked_table(table)
    if table in READONLY:
        abort(403)
    conn=get_db()
    row,where,parts=find_record(table,key) if key else (None,None,None)
    fields=editable_fields(conn,table,row)
    error=None
    if request.method=='POST':
        try:
            values=parse_fields(fields,request.form)
            if table=='auction_lot':
                target=conn.execute('SELECT status FROM auction WHERE auction_id=?',(values.get('auction_id',row['auction_id'] if row else None),)).fetchone()
                if target is None or target['status']!='draft' or (row and row['status']!='draft'):
                    raise ValueError('Lots can only be created or edited in a draft auction.')
            if table=='auction' and row and row['status']!='draft':
                raise ValueError('An open or closed auction is part of the bidding history and cannot be edited.')
            if table=='collector' and row:
                if values.get('bidder_id')!=str(row['bidder_id']):
                    raise ValueError('A collector’s bidder identity cannot be reassigned.')
            with conn:
                if row:
                    assignments=','.join(f'{k}=?' for k in values)
                    conn.execute(f'UPDATE {table} SET {assignments} WHERE {where}',list(values.values())+parts)
                else:
                    names=','.join(values)
                    placeholders=','.join('?' for _ in values)
                    conn.execute(f'INSERT INTO {table} ({names}) VALUES ({placeholders})',list(values.values()))
            flash(f'{TABLES[table]} record saved.','success')
            return redirect(url_for('web.admin_table',table=table))
        except (ValueError,sqlite3.IntegrityError,sqlite3.OperationalError) as exc:
            error=friendly_integrity(exc) if isinstance(exc,sqlite3.IntegrityError) else str(exc)
            flash(error,'error')
            fields=editable_fields(conn,table,row,request.form)
    return render_template('admin/form.html',title=('Edit ' if row else 'Add ')+TABLES[table].lower(),
        table=table,fields=fields,editing=bool(row),error=error), (400 if error else 200)


@bp.route('/staff/data/<table>/new',methods=['GET','POST'])
@require_role('staff')
def admin_create(table):
    return manage_form(table)


@bp.route('/staff/data/<table>/<key>/edit',methods=['GET','POST'])
@require_role('staff')
def admin_edit(table,key):
    return manage_form(table,key)


@bp.post('/staff/data/<table>/<key>/delete')
@require_role('staff')
def admin_delete(table,key):
    checked_table(table)
    if table in READONLY:
        abort(403)
    row,where,parts=find_record(table,key)
    try:
        if table in ('auction','auction_lot') and row['status']!='draft':
            raise ValueError('Keep open and closed auction records to preserve their history.')
        with get_db():
            get_db().execute(f'DELETE FROM {table} WHERE {where}',parts)
        flash('Record deleted.','success')
    except (ValueError,sqlite3.IntegrityError) as error:
        flash(friendly_integrity(error) if isinstance(error,sqlite3.IntegrityError) else str(error),'error')
    return redirect(url_for('web.admin_table',table=table))


@bp.route('/staff/reports')
@require_role('staff')
def reports():
    query_id=request.args.get('query','collection')
    selected=next((q for q in QUERIES if q['id']==query_id),None)
    if selected is None:
        abort(404)
    cursor=get_db().execute(selected['sql'])
    data=[dict(r) for r in cursor]
    return render_template('reports.html',queries=QUERIES,selected=selected,
        columns=[c[0] for c in cursor.description],rows=data,count=len(data))
