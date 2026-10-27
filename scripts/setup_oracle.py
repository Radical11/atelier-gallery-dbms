"""Create a new isolated schema using local OS DBA authentication; never reset it."""
import json
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from atelier.oracle_db import CONFIG, connection, statements


def main():
    if not CONFIG.exists():
        sqlplus = shutil.which('sqlplus')
        if not sqlplus:
            raise SystemExit('SQL*Plus is required for local setup. Alternatively configure Oracle environment variables.')
        config = dict(user='ATELIER_PROJECT', password='A' + secrets.token_hex(12),
                      dsn='localhost:1521/xe', client_dir=str(Path(sqlplus).parent))
        # Refuse to take ownership of, reset, or modify an existing schema.
        bootstrap = f"""WHENEVER SQLERROR EXIT SQL.SQLCODE
SET ECHO OFF FEEDBACK OFF
DECLARE existing NUMBER;
BEGIN
 SELECT COUNT(*) INTO existing FROM dba_users WHERE username='ATELIER_PROJECT';
 IF existing>0 THEN RAISE_APPLICATION_ERROR(-20100,'ATELIER_PROJECT already exists; configure its credentials manually'); END IF;
 EXECUTE IMMEDIATE 'CREATE USER ATELIER_PROJECT IDENTIFIED BY "{config['password']}" DEFAULT TABLESPACE USERS TEMPORARY TABLESPACE TEMP QUOTA 200M ON USERS';
 EXECUTE IMMEDIATE 'GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE TRIGGER, CREATE SEQUENCE TO ATELIER_PROJECT';
END;
/
EXIT
"""
        result = subprocess.run([sqlplus, '-L', '-S', '/ as sysdba'], input=bootstrap,
                                capture_output=True, text=True, timeout=40)
        if result.returncode:
            raise SystemExit('Dedicated schema creation failed: ' + result.stdout.replace(config['password'], '[redacted]'))
        CONFIG.parent.mkdir(exist_ok=True)
        CONFIG.write_text(json.dumps(config, indent=2), encoding='utf-8')
        print('Created dedicated ATELIER_PROJECT schema. Local credentials saved to ignored instance/oracle.json.')
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM user_tables')
            count = cur.fetchone()[0]
            if count == 0:
                for script in ('01_schema.sql', '02_seed.sql', '03_rules.sql'):
                    for sql in statements(ROOT / 'oracle' / script):
                        cur.execute(sql)
                    conn.commit()
                    print('Installed', script)
            elif count not in (18,19):
                raise SystemExit('Existing schema has an unexpected table count. No reset performed; inspect it manually.')
            cur.execute("SELECT COUNT(*) FROM user_tables WHERE table_name='USER_ACCOUNT'")
            if not cur.fetchone()[0]:
                from werkzeug.security import generate_password_hash
                for sql in statements(ROOT / 'oracle' / '05_accounts.sql'):
                    cur.execute(sql)
                accounts=[(1,'admin@atelier.example','AdminDemo!2026','staff',None),
                          (2,'maya@atelier.example','BidderDemo!2026','bidder',1),
                          (3,'arjun@atelier.example','BidderDemo!2026','bidder',2),
                          (4,'sara@atelier.example','BidderDemo!2026','bidder',3)]
                cur.executemany('INSERT INTO user_account VALUES(:1,:2,:3,:4,:5)',
                    [(i,email,generate_password_hash(password),role,bidder) for i,email,password,role,bidder in accounts])
                conn.commit()
                print('Created four hashed demo login accounts in Oracle.')
            cur.execute("SELECT name,line,text FROM user_errors ORDER BY name,sequence")
            errors = cur.fetchall()
            if errors:
                raise SystemExit('Oracle compilation errors: ' + repr(errors))
            cur.execute('SELECT USER, COUNT(*) FROM artist')
            print('Oracle connected:', cur.fetchone(), 'server', conn.version)
    print('Ready: Staff desk -> Oracle assignment. The application uses Oracle; existing SQLite SQL/data remain a backup.')


if __name__ == '__main__':
    main()
