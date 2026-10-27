"""Oracle-only application connection and DB-API convenience methods."""
from datetime import date, datetime
from decimal import Decimal
import re
from flask import g
from . import oracle_db


class IntegrityError(ValueError):
    pass


class OperationalError(RuntimeError):
    pass


class Row(dict):
    def __getitem__(self, key):
        return list(self.values())[key] if isinstance(key, int) else super().__getitem__(key)


def value(item):
    if isinstance(item, datetime):
        return item.date().isoformat() if item.time().isoformat() == '00:00:00' else item.isoformat(' ', timespec='seconds')
    if isinstance(item, date):
        return item.isoformat()
    if isinstance(item, Decimal):
        return int(item) if item == item.to_integral_value() else float(item)
    return item


class Result:
    def __init__(self, rows=(), description=None, rowcount=0, lastrowid=None):
        self.rows = list(rows)
        self.description = description
        self.rowcount = rowcount
        self.lastrowid = lastrowid

    def __iter__(self):
        return iter(self.rows)

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None

    def fetchall(self):
        rows, self.rows = self.rows, []
        return rows


PK = {'artist':'artist_id','artwork':'artwork_id','gallery':'gallery_id','curator':'curator_id',
      'exhibition':'exhibition_id','auction':'auction_id','auction_lot':'lot_id','bidder':'bidder_id',
      'bid':'bid_id','collector':'collector_id','sale':'sale_id','art_expert':'expert_id',
      'appraisal':'appraisal_id','authentication':'authentication_id','user_account':'user_id'}


class Connection:
    def __init__(self):
        self.config = oracle_db.configuration()
        self.driver = oracle_db.driver(self.config)
        self.raw = oracle_db.acquire()
        with self.raw.cursor() as cur:
            cur.execute("ALTER SESSION SET NLS_DATE_FORMAT='YYYY-MM-DD'")
            cur.execute("ALTER SESSION SET NLS_TIMESTAMP_FORMAT='YYYY-MM-DD HH24:MI:SS'")

    def next_id(self):
        return self.execute('SELECT lab_id_seq.NEXTVAL FROM dual').fetchone()[0]

    def execute(self, sql, params=()):
        sql = sql.strip().rstrip(';')
        last_id = None
        match = re.match(r'INSERT INTO (\w+)\s*\(([^)]+)\)\s*VALUES\s*\((.*)\)$', sql, re.I | re.S)
        if match and match[1].lower() in PK:
            key = PK[match[1].lower()]
            if key not in [c.strip().lower() for c in match[2].split(',')]:
                last_id = self.next_id()
                sql = f'INSERT INTO {match[1]} ({key},{match[2]}) VALUES (?,{match[3]})'
                params = (last_id, *params)
        if not isinstance(params, dict):
            index = 0
            def bind(_):
                nonlocal index
                result = f':b{index}'
                index += 1
                return result
            sql = re.sub(r'\?', bind, sql)
            params = {f'b{i}': v for i, v in enumerate(params)}
        try:
            with self.raw.cursor() as cur:
                if hasattr(self, 'trace'):
                    self.trace.append(dict(sql=sql,binds=params))
                cur.execute(sql, params)
                if cur.description:
                    columns = [col[0].lower() for col in cur.description]
                    records = [Row(zip(columns, (value(v) for v in row))) for row in cur.fetchall()]
                    return Result(records, [(c,) for c in columns], len(records))
                return Result(rowcount=cur.rowcount, lastrowid=last_id)
        except self.driver.DatabaseError as error:
            detail = error.args[0]
            if detail.code in (1,1400,1438,2290,2291,2292,12899) or 20000 <= detail.code <= 20999:
                raise IntegrityError(detail.message.strip()) from error
            raise OperationalError(detail.message.strip()) from error

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()

    def close(self):
        self.raw.rollback()
        self.raw.close()

    def __enter__(self):
        return self

    def __exit__(self, kind, error, traceback):
        self.rollback() if kind else self.commit()


def get_db():
    if 'db' not in g:
        g.db = Connection()
    return g.db


def init_app(app):
    @app.teardown_appcontext
    def close_db(error):
        conn = g.pop('db', None)
        if conn is not None:
            conn.close()
