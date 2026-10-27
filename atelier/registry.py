"""Allow-listed management metadata. Identifiers never come from arbitrary SQL input."""
from datetime import date
from decimal import Decimal, InvalidOperation

TABLES = {
    'artwork': 'Artworks', 'artist': 'Artists', 'gallery': 'Galleries',
    'curator': 'Curators', 'exhibition': 'Exhibitions',
    'exhibition_artwork': 'Exhibition artworks', 'artist_gallery': 'Artist representation',
    'auction': 'Auctions', 'auction_lot': 'Auction lots', 'bidder': 'Bidders',
    'bid': 'Bids', 'sale': 'Sales', 'collector': 'Collectors',
    'art_expert': 'Art experts', 'appraisal': 'Appraisals',
    'authentication': 'Artwork authentication',
}
MONEY = {'starting_price', 'reserve_price', 'bid_amount', 'sale_price', 'estimated_value'}
READONLY = {'bid', 'sale'}
FK = {
    'artist_id': ('artist', 'artist_id', 'name'),
    'gallery_id': ('gallery', 'gallery_id', 'name'),
    'curator_id': ('curator', 'curator_id', 'name'),
    'exhibition_id': ('exhibition', 'exhibition_id', 'title'),
    'artwork_id': ('artwork', 'artwork_id', 'title'),
    'auction_id': ('auction', 'auction_id', 'title'),
    'bidder_id': ('bidder', 'bidder_id', 'name'),
    'collector_id': ('collector', 'collector_id', 'name'),
    'expert_id': ('art_expert', 'expert_id', 'name'),
}
OPTIONS = {'result': ['Authentic', 'Inconclusive', 'Not authentic']}


def label(name):
    return name.replace('_id', ' ID').replace('_', ' ').capitalize().replace(' id', ' ID')


def paise(value):
    try:
        number = Decimal(str(value))
        if not number.is_finite() or number < 0 or number > Decimal('999999999999.99'):
            raise ValueError('Enter a nonnegative amount below ₹1 trillion.')
        if number.as_tuple().exponent < -2:
            raise ValueError('Amounts can have at most two decimal places.')
        return int(number * 100)
    except (InvalidOperation, TypeError):
        raise ValueError('Enter a valid amount in rupees.') from None


def table_info(conn, table):
    if table not in TABLES:
        raise KeyError(table)
    return [dict(r) for r in conn.execute(f'PRAGMA table_info({table})')]


def primary_keys(conn, table):
    return [r['name'] for r in sorted(table_info(conn, table), key=lambda r: r['pk']) if r['pk']]


def editable_fields(conn, table, row=None, form=None):
    metadata = table_info(conn, table)
    primary = primary_keys(conn, table)
    result = []
    for col in metadata:
        name = col['name']
        if name in ('status', 'bid_time') or (name in primary and (row is not None or len(primary) == 1)):
            continue
        raw = row[name] if row is not None else ''
        value = (f'{raw / 100:.2f}' if raw is not None and name in MONEY else raw) if raw != '' else ''
        if form is not None:
            value = form.get(name, '')
        field = dict(name=name, label=label(name), type='text', required=bool(col['notnull'] or col['pk']),
                     value='' if value is None else value, options=[], step=None)
        if name in FK:
            target, key, title = FK[name]
            field['type'] = 'select'
            field['options'] = [dict(value=str(r[key]), label=f"{r[title]} · #{r[key]}") for r in conn.execute(f'SELECT {key}, {title} FROM {target} ORDER BY {title}')]
        elif name == 'image_path':
            field['type'] = 'select'
            field['options'] = [dict(value=f'images/artwork-{i:02}.webp', label=f'Original collection · {i:02}') for i in range(1, 13)]
        elif name in OPTIONS:
            field['type'] = 'select'
            field['options'] = [dict(value=o, label=o.replace('_', ' ').capitalize()) for o in OPTIONS[name]]
        elif name in MONEY:
            field.update(type='number', step='0.01')
        elif name == 'commission_percentage':
            field.update(type='number', step='0.01')
        elif col['type'].upper() == 'INTEGER':
            field.update(type='number', step='1')
        elif name.endswith('_date') or name == 'date':
            field['type'] = 'date'
        elif name == 'email':
            field['type'] = 'email'
        elif name in ('description', 'biography', 'notes', 'address'):
            field['type'] = 'textarea'
        result.append(field)
    return result


def parse_fields(fields, form):
    result = {}
    for field in fields:
        name = field['name']
        text = form.get(name, '').strip()
        if not text:
            if field['required']:
                raise ValueError(f"{field['label']} is required.")
            result[name] = None
            continue
        if len(text) > 10000:
            raise ValueError(f"{field['label']} is too long.")
        if field['type'] == 'select' and text not in [str(o['value']) for o in field['options']]:
            raise ValueError(f"Choose a valid {field['label'].lower()}.")
        if name in MONEY:
            result[name] = paise(text)
        elif field['type'] == 'number':
            try:
                result[name] = float(text) if name == 'commission_percentage' else int(text)
            except ValueError:
                raise ValueError(f"Enter a valid number for {field['label'].lower()}.") from None
            if name == 'commission_percentage' and not 0 <= result[name] <= 100:
                raise ValueError('Commission must be between 0 and 100%.')
        elif field['type'] == 'date':
            try:
                result[name] = date.fromisoformat(text).isoformat()
            except ValueError:
                raise ValueError(f"Enter a valid date for {field['label'].lower()}.") from None
        elif field['type'] == 'email':
            if '@' not in text or '.' not in text.split('@')[-1]:
                raise ValueError('Enter a valid email address.')
            result[name] = text
        else:
            result[name] = text
    return result
