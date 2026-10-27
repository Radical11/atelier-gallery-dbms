"""One-time copy into the newly provisioned Oracle schema. Source is read-only."""
import hashlib
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from atelier.oracle_db import connection, statements

ORDER = ['artist','artwork','gallery','curator','exhibition','auction','auction_lot','bidder',
         'bid','collector','sale','art_expert','appraisal','authentication','artist_gallery','exhibition_artwork','user_account']


def main():
    source = ROOT/'instance'/'atelier.sqlite'
    marker = ROOT/'instance'/'oracle-migration.json'
    checksum = hashlib.sha256(source.read_bytes()).hexdigest()
    if marker.exists():
        print('Migration already recorded. Oracle data preserved; SQLite is no longer active.')
        return
    with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as old:
        old.row_factory=sqlite3.Row
        fixture={table:[dict(r) for r in old.execute('SELECT * FROM '+table)] for table in ORDER}
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM user_tables WHERE table_name='USER_ACCOUNT'")
            if not cur.fetchone()[0]:
                for sql in statements(ROOT/'oracle'/'05_accounts.sql'):
                    cur.execute(sql)
            cur.execute('SELECT COUNT(*) FROM lab_evidence')
            if cur.fetchone()[0]:
                raise SystemExit('Oracle has presentation activity. Refusing to replace it.')
            cur.execute('SELECT COUNT(*) FROM artwork WHERE artwork_id>=100000')
            if cur.fetchone()[0]:
                raise SystemExit('Oracle has application activity. Refusing to replace it.')
            cur.execute('SELECT trigger_name FROM user_triggers')
            triggers=[r[0] for r in cur.fetchall()]
            try:
                for name in triggers:
                    cur.execute('ALTER TRIGGER '+name+' DISABLE')
                for table in reversed(ORDER):
                    cur.execute('DELETE FROM '+table)
                for table in ORDER:
                    records=fixture[table]
                    if not records:
                        continue
                    columns=list(records[0])
                    names=','.join('"DATE"' if c=='date' else c for c in columns)
                    params=','.join(':'+str(i+1) for i in range(len(columns)))
                    values=[]
                    for record in records:
                        row=[]
                        for col in columns:
                            val=record[col]
                            if val is not None and (col.endswith('_date') or col=='date'):
                                val=datetime.strptime(val,'%Y-%m-%d')
                            elif val is not None and col=='bid_time':
                                val=datetime.fromisoformat(val)
                            row.append(val)
                        values.append(row)
                    cur.executemany(f'INSERT INTO {table} ({names}) VALUES ({params})',values)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                for name in triggers:
                    cur.execute('ALTER TRIGGER '+name+' ENABLE')
            counts={}
            for table in ORDER:
                cur.execute('SELECT COUNT(*) FROM '+table)
                counts[table]=cur.fetchone()[0]
                assert counts[table]==len(fixture[table]), table
            cur.execute("SELECT COUNT(*) FROM user_objects WHERE status<>'VALID'")
            assert cur.fetchone()[0]==0,'Invalid Oracle objects'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==checksum,'Source changed'
    marker.write_text(json.dumps(dict(source_sha256=checksum,counts=counts),indent=2),encoding='utf-8')
    print('Migrated',sum(counts.values()),'rows across',len(counts),'tables; all counts match. SQLite source unchanged.')


if __name__=='__main__':
    main()
