"""Write the five short query handouts from the same presets the portal runs."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from atelier.assignment_queries import MODULES


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--capture',action='store_true',help='Execute each script in Oracle SQL*Plus and capture outputs.')
    capture=parser.parse_args().capture
    directory=ROOT/'oracle/modules'
    directory.mkdir(exist_ok=True)
    guide=['# Simple SQL queries for the five presenters','',
           'Each person has the same pattern: INSERT, UPDATE, DELETE, search, two-table JOIN, COUNT/GROUP BY, one IN subquery, and one basic function. The join supplies the assignment’s more complex SELECT; the nested query and function are retained because the brief asks for them.','',
           '## How to use the examples','',
           'Open Staff desk → Oracle presentation studio and choose your name. Run INSERT → UPDATE → DELETE, then the five SELECT buttons. To see your new record, run the search SELECT before DELETE too.','',
           '` :record_id ` is the ID generated for your demonstration row. ` :value ` is the title or name entered in the form; ` :email ` is a unique fictional email for Shanil’s bidder. ` :search ` contains `%` for all rows or `%word%` to find a word. These are bound values, so you do not need to memorize a particular numeric ID.','',
           'The INSERT examples include only mandatory fields. Other details may remain NULL or use their defaults. Existing artist/gallery/curator ID 1 is used as the parent. Oracle dates use `DATE \'YYYY-MM-DD\'`. Monetary columns store paise, so divide by 100 to display rupees. Search uses LIKE and is case-sensitive.','',
           '| Presenter | Module |','| --- | --- |']
    for mod in MODULES:
        guide.append(f"| {mod['presenter']} | {mod['title']} |")
    meanings=['Add one new record.','Change only that record’s title or name.','Remove only that unreferenced demonstration record.',
              'LIKE finds names or titles matching the search value.','JOIN combines two tables using their matching ID columns.',
              'GROUP BY creates one group per parent ID; COUNT(*) counts the rows in that group.',
              'The inner SELECT finds IDs; the outer SELECT displays records whose ID appears in that list.',
              'A built-in function formats or transforms the displayed result without changing stored data.']
    for mod in MODULES:
        path=directory/f"0{mod['number']}_{mod['presenter'].lower()}.sql"
        lines=[f"-- {mod['presenter']}: {mod['title']}",'-- Three DML operations and five short SELECT queries.',
               '-- Connect as ATELIER_PROJECT; only the newly generated demo row is updated/deleted.',
               'SET PAGESIZE 100','SET LINESIZE 200','SET FEEDBACK ON','VARIABLE record_id NUMBER',
               'VARIABLE value VARCHAR2(200)','VARIABLE email VARCHAR2(200)','VARIABLE search VARCHAR2(200)',
               'BEGIN','  SELECT lab_id_seq.NEXTVAL INTO :record_id FROM dual;',
               "  :email := 'demo-' || TO_CHAR(:record_id) || '@atelier.example';","  :search := '%';",'END;','/']
        guide += ['',f"## {mod['presenter']} — {mod['title']}",'']
        for i,query in enumerate(mod['queries']):
            lines += ['',f"-- {i+1}. {query['title']}"]
            if query['id'] in ('insert','update'):
                val=mod['changed'] if query['id']=='update' else mod['initial']
                lines += ["BEGIN :value := '"+val.replace("'","''")+"'; END;",'/']
            lines += [query['sql']+';']
            if query['kind']!='SELECT':
                lines += ['COMMIT;',f"SELECT * FROM {mod['table']} WHERE {mod['pk']}=:record_id;"]
            guide += [f"### {i+1}. {query['title']}",'','```sql',query['sql']+';','```','',meanings[i],'']
        path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        if capture:
            from atelier.oracle_db import configuration
            cfg=configuration()
            commands=('WHENEVER SQLERROR EXIT SQL.SQLCODE\nSET ECHO OFF\nCONNECT '+cfg['user']+'/"'+cfg['password']+'"@'+cfg['dsn']+
                      '\nSET DEFINE OFF\nSET ECHO ON\n@"'+str(path)+'"\nEXIT\n')
            proc=subprocess.run(['sqlplus','-L','-S','/nolog'],input=commands.encode('utf-8'),capture_output=True,
                                env=dict(os.environ,NLS_LANG='AMERICAN_AMERICA.AL32UTF8'),timeout=30)
            output=proc.stdout.decode('utf-8',errors='replace').replace(cfg['password'],'[redacted]').replace('\r\n','\n').replace('\r','')
            output='\n'.join(line.rstrip() for line in output.splitlines()).rstrip()+'\n'
            if proc.returncode or 'ORA-' in output or 'SP2-' in output:
                raise RuntimeError(mod['presenter']+' SQL*Plus execution failed: '+output[-1000:])
            out=ROOT/'docs/assignment/sqlplus-outputs';out.mkdir(exist_ok=True)
            (out/(path.stem+'.txt')).write_text(output,encoding='utf-8',newline='\n')
            print(mod['presenter']+': all 8 statements executed in Oracle SQL*Plus')
    (ROOT/'docs/assignment/SIMPLE_QUERIES.md').write_text('\n'.join(guide).rstrip()+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
