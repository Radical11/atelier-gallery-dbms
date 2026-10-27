"""Atelier — a local art gallery and auction DBMS demonstration."""
import os
import secrets
from pathlib import Path

import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect, CSRFError


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    secret_path = Path(app.instance_path) / '.secret'
    secret = os.environ.get('ATELIER_SECRET_KEY')
    if not secret:
        if not secret_path.exists():
            secret_path.write_text(secrets.token_hex(32), encoding='utf-8')
        secret = secret_path.read_text(encoding='utf-8').strip()
    app.config.from_mapping(
        SECRET_KEY=secret,
        DATABASE_ENGINE='oracle',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        MAX_CONTENT_LENGTH=1_000_000,
        WTF_CSRF_TIME_LIMIT=3600,
    )
    if test_config:
        app.config.update(test_config)
    CSRFProtect(app)
    from . import db
    db.init_app(app)
    from .web import bp, money
    app.register_blueprint(bp)
    from .presentation import bp as presentation_bp
    app.register_blueprint(presentation_bp)
    app.jinja_env.filters['money'] = money
    @app.cli.command('oracle-check')
    def oracle_check():
        """Check the configured Oracle connection without changing records."""
        with app.app_context():
            conn = db.get_db()
            row = conn.execute("SELECT USER AS schema_name FROM dual").fetchone()
            click.echo(f"Oracle {conn.raw.version} / {row['schema_name']}")

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('403.html'), 403

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_template('error.html', title='Please refresh this page',
                               message='Your form session expired. Refresh the page and submit it again.'), 400

    return app
