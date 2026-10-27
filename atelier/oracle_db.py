"""Dedicated assignment schema; never substitutes SQLite for Oracle results."""
import json
import os
import threading
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / 'instance' / 'oracle.json'
_lock = threading.Lock()
_ready = False
_pool = None


def configuration():
    config = json.loads(CONFIG.read_text(encoding='utf-8')) if CONFIG.exists() else {}
    for key in ('user', 'password', 'dsn', 'client_dir'):
        if os.environ.get('ATELIER_ORACLE_' + key.upper()):
            config[key] = os.environ['ATELIER_ORACLE_' + key.upper()]
    if not all(config.get(key) for key in ('user', 'password', 'dsn')):
        raise RuntimeError('Oracle is not configured. Run scripts/setup_oracle.py first.')
    return config


def driver(config):
    global _ready
    import oracledb
    with _lock:
        if not _ready:
            if config.get('client_dir'):
                oracledb.init_oracle_client(lib_dir=config['client_dir'])
            _ready = True
    return oracledb


def acquire():
    """Bound concurrent sessions and reuse them instead of spawning XE processes per request."""
    global _pool
    config = configuration()
    oracle = driver(config)
    with _lock:
        if _pool is None:
            _pool = oracle.create_pool(user=config['user'],password=config['password'],dsn=config['dsn'],
                                       min=1,max=6,increment=1,getmode=oracle.POOL_GETMODE_WAIT)
    return _pool.acquire()


@contextmanager
def connection():
    config = configuration()
    oracle = driver(config)
    conn = oracle.connect(user=config['user'], password=config['password'], dsn=config['dsn'])
    try:
        if conn.thin or oracle.clientversion()[0] >= 18:
            conn.call_timeout = 15000
        yield conn
    finally:
        conn.rollback()
        conn.close()


def select(conn, sql, binds=None, limit=200):
    with conn.cursor() as cursor:
        cursor.execute(sql.rstrip().rstrip(';'), binds or {})
        columns = [item[0].lower() for item in cursor.description]
        data = cursor.fetchmany(limit + 1)
        return dict(columns=columns, rows=[dict(zip(columns, row)) for row in data[:limit]],
                    truncated=len(data) > limit)


def statements(path):
    """SQL*Plus-compatible scripts: semicolon SQL, slash-terminated PL/SQL."""
    buffer = []
    plsql = False
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('--'):
            continue
        if not buffer:
            plsql = stripped.upper().startswith(('CREATE OR REPLACE TRIGGER', 'CREATE OR REPLACE PROCEDURE',
                                                 'CREATE OR REPLACE PACKAGE', 'DECLARE', 'BEGIN'))
        if stripped == '/':
            if buffer:
                yield '\n'.join(buffer)
                buffer = []
            continue
        buffer.append(line)
        if not plsql and stripped.endswith(';'):
            yield '\n'.join(buffer).rstrip().rstrip(';')
            buffer = []
    if buffer:
        raise ValueError(f'Unterminated SQL in {path}')
