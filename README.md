# Atelier - Art Gallery, Exhibition & Auction Management System

A local final-year DBMS demonstration using **Flask + Jinja + Oracle Database**. All live website features, login accounts, staff forms, auctions, reports and presentation demonstrations use Oracle. There is no SQLite fallback.

The museum-style interface uses original fictional art, a quiet editorial hero and subtle artwork hover effects. Assets are bundled locally.

## Run on Windows

This laptop already has Oracle Database **11g XE 11.2.0.2.0** and its 64-bit client installed. OracleServiceXE and OracleXETNSListener must be running. Python 3.11-3.13 is supported by the pinned driver used here.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\setup_oracle.py
.\.venv\Scripts\python.exe run.py
```

Then open **http://127.0.0.1:5000**. On later runs, double-click **start.cmd** or run `./start.ps1`. Stop with Ctrl+C. Startup preserves Oracle data; it never resets or reseeds it.

Setup uses local OS DBA authentication once to create the isolated **ATELIER_PROJECT** schema in the existing XE database. It never changes other Oracle users. The app uses that project's ordinary schema login, never SYS/SYSTEM. Setup is repeatable and preserves existing records. The schema has a 200 MB quota and only its own CREATE SESSION/TABLE/VIEW/TRIGGER/SEQUENCE privileges.

Local database credentials are generated into ignored `instance/oracle.json`. Do not publish this file. Alternatively set `ATELIER_ORACLE_USER`, `ATELIER_ORACLE_PASSWORD`, `ATELIER_ORACLE_DSN` and, for Oracle 11g, `ATELIER_ORACLE_CLIENT_DIR`. This laptop's client directory is `C:\oraclexe\app\oracle\product\11.2.0\server\bin`. The DSN is `localhost:1521/xe`.

The installed Oracle 11g client requires python-oracledb 3.0.0 in Thick mode. Modern Thin mode alone cannot connect to Oracle 11g. See the [driver compatibility documentation](https://python-oracledb.readthedocs.io/en/v3.0.0/user_guide/installation.html).

Check connectivity without changing records:

```powershell
.\.venv\Scripts\python.exe -m flask --app run oracle-check
```

## Working demo accounts

| Role | Email | Password |
| --- | --- | --- |
| Staff | admin@atelier.example | AdminDemo!2026 |
| Bidder | maya@atelier.example | BidderDemo!2026 |
| Bidder | arjun@atelier.example | BidderDemo!2026 |
| Bidder | sara@atelier.example | BidderDemo!2026 |

The intentionally public local-demo credentials use real password-hash verification in Oracle. Demo-account buttons fill the login form; staff and bidder roles are checked server-side. There is no public registration. All commercial activity and payments are fictional.

## Present the assignment

Sign in as staff, then open **Staff desk -> Oracle presentation studio**.

| Member | Module | Required operations |
| --- | --- | --- |
| Vihaan | Artists & collection | 1 INSERT, 1 UPDATE, 1 DELETE, 5 SELECT |
| Kaashvi | Galleries & exhibitions | 1 INSERT, 1 UPDATE, 1 DELETE, 5 SELECT |
| Gaurav | Auctions & lots | 1 INSERT, 1 UPDATE, 1 DELETE, 5 SELECT |
| Shanil | Bidders & bids | 1 INSERT, 1 UPDATE, 1 DELETE, 5 SELECT |
| Ashutosh | Experts & appraisals | 1 INSERT, 1 UPDATE, 1 DELETE, 5 SELECT |

Each person can enter their name. Run INSERT -> UPDATE -> DELETE for their new demonstration record. SELECTs may run at any time, and show simple search, joins, aggregation, one-level IN subqueries and basic SQL functions. The portal displays SQL, bound values, affected rows and real Oracle results. It saves evidence in Oracle and offers **Download my outputs**. Only the module's own demonstration record can be mutated by these presets. Accepted bids and final sales remain protected.

Other studio views:

- **Full sale walkthrough:** eight atomic Oracle steps: artwork -> exhibition -> expert checks -> auction listing -> two competing bids -> sale -> completed payment. The completed sale appears in normal website reports.
- **Database explorer:** actual Oracle DDL, constraints and record previews for all 16 domain tables. Account hashes are excluded.
- **Rules & transactions:** compiled Oracle trigger source and the actual Python auction services.
- **DDL, TCL & coverage:** live CREATE/ALTER/INDEX/DROP, COMMIT/SAVEPOINT/ROLLBACK, set operations, ALL and a revenue view.

The walkthrough creates clearly named fictional presentation records in the main Oracle schema. It is not a hidden SQLite sandbox. A step, progress and execution evidence commit together. Repeated submissions are rejected. Individual workspaces are associated with the signed browser session, so download the outputs before signing out or clearing cookies. Existing evidence remains stored in Oracle; the prior session token is required to retrieve that session's export.

## Submission material

- [Compliance matrix](docs/assignment/COMPLIANCE.md)
- [Report chapter with all 40 individual SQL statements and actual output tables](docs/assignment/REPORT_CHAPTER.md)
- [Full structured execution evidence, including the complete sale workflow](docs/assignment/ORACLE_EXECUTION_OUTPUTS.md)
- [Simplified member query verification](docs/assignment/MEMBER_VERIFICATION.json)
- [Original full migration verification](docs/assignment/VERIFICATION.json)
- [Concurrency, reserve and rollback verification](docs/assignment/TRANSACTION_VERIFICATION.json)
- [Staff form and validation verification](docs/assignment/FORM_VERIFICATION.json)
- [Simple query guide for all five members](docs/assignment/SIMPLE_QUERIES.md)
- [Five SQL*Plus module scripts](oracle/modules)
- [Actual SQL*Plus terminal outputs for all five members](docs/assignment/sqlplus-outputs)

Fill in the student registration numbers and incorporate the chapter into the college's final project report. The supplied requirement and basic SQL topics are covered; a grade or acceptance by the examiner is not guaranteed.

## Active database SQL

| File | Purpose |
| --- | --- |
| `oracle/00_create_user.sql` | Manual SQL*Plus provisioning alternative |
| `oracle/01_schema.sql` | 16 domain tables, 2 presentation tables, keys/checks/indexes/sequence/revenue view |
| `oracle/02_seed.sql` | Fictional baseline data, integer paise and Oracle DATE/TIMESTAMP literals |
| `oracle/03_rules.sql` | Seven Oracle triggers for bid/sale history and auction/lot state |
| `oracle/04_ddl_tcl.sql` | Separate representative DDL and TCL examples |
| `oracle/05_accounts.sql` | Login table; Python setup inserts hashed demo credentials |
| `oracle/modules/*.sql` | Each person's three DML and five SELECT statements |

There are **19 Oracle tables**: the 16 specified domain tables, `user_account`, `lab_workspace` and `lab_evidence`. Auction's supplied Date attribute is the quoted Oracle column `"DATE"` because DATE is a reserved type keyword. Oracle NUMBER/DATE/VARCHAR2 types replace SQLite-specific types; the entities and relationships are preserved.

### Relationships, normalization and integrity

- Mandatory foreign keys implement total child participation. Optional parent participation permits zero children. Referenced records cannot be deleted.
- Artist-gallery and exhibition-artwork relationships use composite primary keys. The artwork-lot relationship is 1:N over time. A function-based unique index permits only one open listing per artwork.
- A sale has exactly one unique winning bid and a matching collector identity. A bid may have no sale. Final selling price exists on SALE, not AUCTION_LOT.
- Artists, curators, galleries and experts are separate entities. Assessment rows reference expert IDs rather than repeating names. Collector contact attributes are retained as required by the supplied model; the unique bidder link preserves identity. Do not claim that this retained snapshot duplication is a perfectly redundancy-free design.
- Money uses integer paise in NUMBER(18,0) columns. The application validates precision and bounds before binding monetary input. Dates use Oracle DATE and ordering checks; commissions are bounded from 0 to 100.
- Oracle triggers enforce bid thresholds, immutable accepted history, reserve/collector/price consistency and auction/lot transitions. Compound triggers avoid querying mutating bid/sale tables from row-level triggers.
- Auction operations use SELECT FOR UPDATE followed by COMMIT or ROLLBACK. A bounded session pool reuses up to six connections. A failed close cannot leave a partial collector, sale or status update. Repeated closure returns the original outcome.
- Flask-WTF CSRF protection, hashed passwords, signed HttpOnly/SameSite cookies, server-side roles and parameterized SQL remain in use. Management table identifiers are allow-listed. No arbitrary SQL console is exposed.

## Codebase

- `atelier/__init__.py`: app factory, CSRF, blueprint setup and Oracle health command.
- `atelier/oracle_db.py`: local configuration, compatible Oracle client initialization and connection pool.
- `atelier/db.py`: Oracle-only rows/results, binds, date formatting, generated sequence IDs and request teardown.
- `atelier/web.py`: public pages, login, role checks, CRUD forms and report routes.
- `atelier/services.py`: opening auctions, serialized bids, transactional closure and payment updates.
- `atelier/registry.py`: allow-listed forms derived from Oracle's data dictionary.
- `atelier/queries.py`: six Oracle SELECT reports.
- `atelier/assignment_queries.py`: five member modules and supplemental SQL presets.
- `atelier/presentation.py`: actual SQL execution, progress, evidence export, schema inspection and eight-step workflow.
- `atelier/templates` and `atelier/static`: museum-style Jinja UI, local images, restrained hover effects.

The browser layout and art remain local and offline after dependencies are installed. Hover lift respects the effects toggle and reduced motion; dragging and the separate artwork inspector remain removed. The unused earlier Three.js experiment is retained in the source but is not loaded by the homepage. Its license is in `docs/THIRD_PARTY.md`.

## Migration and persistence

The one-time migration copied **77 rows across all 17 application tables**, including password hashes, into Oracle, with exact count checks. `scripts/migrate_sqlite_once.py` opened the source read-only and verified its SHA-256 remained unchanged. It refuses to replace an Oracle schema that has presentation activity and records completion in an ignored local marker. Do not rerun migration as a reset tool.

`instance/atelier.sqlite` is an unchanged historical backup, not an active database. Original SQLite SQL and legacy source/tests are preserved under `atelier/schema.sql`, `docs/SQL_EXPLAINED.sql` and `docs/legacy-sqlite/`. They are not used by the application. The active Oracle data lives in the local XE instance; the provided scripts recreate the fictional baseline on another compatible Oracle installation.

## Verification

The completed Oracle checks and captured outputs are already included. To deliberately run another fictional presentation and refresh evidence:

```powershell
.\.venv\Scripts\python.exe scripts\verify_oracle.py
.\.venv\Scripts\python.exe scripts\check_oracle_transactions.py
.\.venv\Scripts\python.exe scripts\build_assignment_report.py
```

These commands create clearly named fictional demonstration history in Oracle. They never reset data. Verification covers real account authentication/roles, public/staff pages, all 40 individual statements, DDL/TCL and extra SELECTs, the entire sale workflow, invalid bids, concurrent equal bids, concurrent closure, reserve failure, injected rollback and persistence across independent connections. The archived SQLite tests are not Oracle evidence.
