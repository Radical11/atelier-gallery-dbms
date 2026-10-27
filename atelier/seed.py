"""Oracle seed helper. Normal startup never reseeds the database."""
from pathlib import Path
from .oracle_db import statements


def seed_db(conn):
    if conn.execute('SELECT COUNT(*) FROM artist').fetchone()[0]:
        return
    path = Path(__file__).resolve().parent.parent / 'oracle' / '02_seed.sql'
    with conn.raw.cursor() as cursor:
        for sql in statements(path):
            cursor.execute(sql)
    conn.commit()
