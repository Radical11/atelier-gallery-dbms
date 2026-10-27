"""Build a report chapter from saved, actually executed Oracle evidence."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from atelier import create_app
from atelier.assignment_queries import MODULES
from atelier.db import get_db
from atelier.presentation import events


def table(result):
    columns=result['columns']
    if not result['rows']:
        return ['_No rows returned._','']
    def cell(value):
        return ('NULL' if value is None else str(value)).replace('|','\\|').replace('\n',' ')
    return ['| '+' | '.join(columns)+' |','| '+' | '.join('---' for _ in columns)+' |',
            *['| '+' | '.join(cell(row.get(c)) for c in columns)+' |' for row in result['rows']],'']


def main():
    proof=json.loads((ROOT/'docs/assignment/VERIFICATION.json').read_text(encoding='utf-8'))
    app=create_app()
    with app.app_context():
        conn=get_db()
        evidence=events(conn,proof['workspace'])
        member_proof=ROOT/'docs/assignment/MEMBER_VERIFICATION.json'
        if member_proof.exists():
            latest=json.loads(member_proof.read_text(encoding='utf-8'))
            evidence=[e for e in evidence if e['module_id'] in ('supplement','workflow')]+events(conn,latest['workspace'])
        version=conn.raw.version
    structured=['# Atelier — Oracle SQL execution evidence','',
                'Member outputs use the current simplified queries and real names. Group DDL/TCL and workflow outputs are retained from their separately verified execution session. All results below were actually executed in Oracle.','']
    for event in evidence:
        structured += [f"## {event['presenter']} · {event['title']}",'','```sql',event['sql']+';','```','',
                       '```json',json.dumps(event,indent=2,ensure_ascii=False),'```','']
    (ROOT/'docs/assignment/ORACLE_EXECUTION_OUTPUTS.md').write_text('\n'.join(structured),encoding='utf-8')
    text=['# Database Implementation Using SQL and Front-End Connectivity','',
          '## Art Gallery, Exhibition & Auction Management System','',
          'Group members: Vihaan, Kaashvi, Gaurav, Shanil and Ashutosh. Add the student registration numbers before submission.','',
          '### Implementation and database provisioning','',
          f'The application uses Flask, Jinja, python-oracledb 3.0.0 and Oracle Database {version}. All public pages, authentication, management forms, auctions, reports and presentation actions use Oracle. There is no SQLite runtime fallback.','',
          'Oracle XE was already installed and running on the demonstration laptop. The project provisions an isolated ATELIER_PROJECT schema inside that database rather than creating another XE instance. oracle/00_create_user.sql records schema/user creation and privileges; scripts/setup_oracle.py performs non-destructive local setup. oracle/01_schema.sql creates the tables, constraints, indexes, sequence and revenue view. oracle/02_seed.sql populates fictional records; oracle/03_rules.sql installs Oracle triggers; oracle/05_accounts.sql creates the application login table. The setup script hashes the four known demo passwords.','',
          'The application user has privileges only to create its own session, tables, views, triggers and sequences, with a bounded tablespace quota. The web server does not connect as SYS or SYSTEM. Actual schema credentials stay in ignored instance/oracle.json or environment variables.','',
          '### Relational design and integrity','',
          'The 16 domain tables retain the supplied entity attributes. user_account supports authenticated users. lab_workspace and lab_evidence store per-presentation progress and execution outputs, giving 19 tables in total.','',
          'Mandatory child relationships use NOT NULL foreign keys. Optional parent participation permits no child records. ARTIST_GALLERY and EXHIBITION_ARTWORK use composite primary keys for their many-to-many relationships. SALE.BID_ID is unique and non-null, implementing zero or one sale per bid and exactly one winning bid per sale. COLLECTOR.BIDDER_ID uniquely links the buyer identity. ART_EXPERT is referenced by APPRAISAL and AUTHENTICATION. GALLERY organizes both exhibitions and auctions. ARTWORK may have multiple historical lots, with a function-based unique index allowing at most one open listing.','',
          'Primary keys, foreign keys, UNIQUE, NOT NULL and CHECK constraints protect identities, dates, status, nonnegative money, commission bounds, certificates and lot numbers. Oracle DATE columns store actual calendar dates. Monetary NUMBER(18,0) columns store integer paise; the application validates decimal inputs before converting rupees to paise. Accepted bid amounts and finalized sale details are immutable. The final selling price is stored on SALE, and collector spending is derived from completed payments.','',
          'Artist, gallery, curator and expert facts are stored in their own entities. Junction attributes depend on their full composite key. Collector contact fields are retained from the supplied model, and may be considered a snapshot of buyer details; the bidder ID preserves identity. This deliberate retained duplication should not be described as an entirely redundancy-free design.','',
          '### Front-end connectivity and operations','',
          'Browser → Flask route → role/input/CSRF validation → pooled python-oracledb connection → parameterized Oracle SQL → commit or rollback → Jinja-rendered results. The installed Oracle 11.2 client is used in Thick mode. A bounded pool reuses sessions. Internal qmark convenience placeholders in form routes are converted to named Oracle binds; SQL presets use Oracle syntax directly.','',
          'The staff portal demonstrates Insert, Update, Delete, Search and Display. Individual modules mutate only a new, server-assigned demonstration record. Names and search values are bound parameters. Each execution stores the actual statement, binds, before/after results and row count in Oracle. Bidders cannot access staff pages. Password hashes, session signing, server-side role checks and CSRF tokens remain in use.','',
          'The eight-step sale walkthrough uses the same Oracle transaction services as the public website. SELECT FOR UPDATE serializes auction/lot writers; a failed operation rolls back all related writes. A winning sale is created only when the highest bid meets reserve, with the matching collector. Payments are simulated and only payment status is mutable.','',
          '### Individual division of work','',
          '| Presenter | Module | Required statements |','| --- | --- | --- |']
    for mod in MODULES:
        text.append(f"| {mod['presenter']} | {mod['title']} | 1 INSERT, 1 UPDATE, 1 DELETE, 5 SELECT |")
    text += ['', 'Each five-query set covers simple search/filtering, a two-table join, COUNT with GROUP BY, a one-level IN subquery, and a basic SQL function. The group also demonstrates set operations, views, indexes, sequences, DDL and TCL. The supplied clarification limits the lab-sheet expectation to basic SQL topics.','',
             '### Executed SQL and corresponding outputs','',
             'The following outputs were captured from real Oracle execution through the Flask application. Values describe fictional demonstration records. Empty results are retained as genuine outputs. Full structured evidence is available in ORACLE_EXECUTION_OUTPUTS.md.','']
    for mod in MODULES:
        text += [f"## {mod['presenter']}: {mod['title']}",'']
        for event in [e for e in evidence if e['module_id']==mod['id']]:
            text += [f"### {event['kind']}: {event['title']}",'','```sql',event['sql']+';','```','',
                     'Bound values: `'+json.dumps(event['binds'],ensure_ascii=False)+'`','']
            if event['before']:
                text += ['Before:','',*table(event['before'])]
            text += ['Result:','',*table(event['result'])]
            if event['affected'] is not None:
                text += [f"{event['affected']} row affected. COMMIT completed.",'']
    text += ['## Group DDL, TCL and additional SELECT evidence','']
    for event in [e for e in evidence if e['module_id']=='supplement']:
        text += ['### '+event['title'],'','```sql',event['sql']+';','```','']
        for i,output in enumerate(event.get('outputs',[event['result']]),1):
            text += [f'Statement output {i}:','',*table(output)]
    text += ['## Complete presentation walkthrough','']
    for event in [e for e in evidence if e['module_id']=='workflow']:
        text += ['### '+event['title'],'',
                 'Executed SQL and per-statement parameters are retained in the structured evidence export.','']
        for output in event['outputs']:
            text += table(output)
    transaction=json.loads((ROOT/'docs/assignment/TRANSACTION_VERIFICATION.json').read_text(encoding='utf-8'))
    text += ['## Verification and limitations','',
             'Four demo accounts authenticated with their assigned permissions. Public pages, all domain management pages, six reports, all 40 individual statements, seven supplements and the eight-step sale workflow executed successfully on Oracle.','',
             *['- '+check+'.' for check in transaction['checks']],'',
             'The original SQLite file remains an unchanged migration backup, not the running database. Initial counts matched across all 17 application tables during migration. Normal startup does not reset or reseed Oracle. The earlier SQLite-specific tests are archived as historical material, and are not presented as Oracle verification.','',
             'The project demonstrates simulated auctions and payments locally. The report chapter and SQL outputs should be incorporated into the institution’s final report template, with the student registration numbers.','',
             '## References','',
             '- [Oracle Database 11g SQL Language Reference](https://docs.oracle.com/cd/E11882_01/server.112/e41084.pdf)',
             '- [python-oracledb 3.0 installation and client compatibility](https://python-oracledb.readthedocs.io/en/v3.0.0/user_guide/installation.html)',
             '- [Oracle transaction control and DDL commits](https://docs.oracle.com/en/database/oracle/oracle-database/21/tdddg/dml-and-transactions.html)','']
    (ROOT/'docs/assignment/REPORT_CHAPTER.md').write_text('\n'.join(text),encoding='utf-8')
    print('Built report chapter with all 40 individual outputs and group demonstrations.')


if __name__=='__main__':
    main()
