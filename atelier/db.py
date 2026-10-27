import sqlite3
from pathlib import Path
from flask import current_app, g


def connect(path):
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA busy_timeout = 10000')
    return conn


def get_db():
    if 'db' not in g:
        g.db = connect(current_app.config['DATABASE'])
    return g.db


def init_db(connection):
    connection.executescript(Path(__file__).with_name('schema.sql').read_text(encoding='utf-8'))


def init_app(app):
    @app.teardown_appcontext
    def close_db(error):
        conn = g.pop('db', None)
        if conn is not None:
            conn.close()
