# Assignment compliance

Scope: the supplied 20-mark SQL implementation and front-end connectivity activity. Vihaan, Kaashvi, Gaurav, Shanil and Ashutosh; basic SQL topics, as clarified by the user.

| Requirement | Implementation and evidence |
| --- | --- |
| Oracle SQL database | Entire running application uses Oracle XE through python-oracledb. No SQLite runtime fallback. |
| Database creation/provisioning | Existing XE instance; dedicated ATELIER_PROJECT user/schema. `oracle/00_create_user.sql`, `scripts/setup_oracle.py`. The application never uses a DBA login. |
| Table creation | `oracle/01_schema.sql`: 16 supplied domain tables plus two presentation tables. `oracle/05_accounts.sql`: login table. |
| Integrity constraints | PK, FK, NOT NULL, UNIQUE, CHECK, composite keys, function-based unique index, seven compiled/enabled Oracle triggers. |
| Data population | Fictional `oracle/02_seed.sql`; Python-generated password hashes. Existing 77 application rows migrated with matching counts, then Oracle-only demonstration records added. |
| DDL | Live CREATE TABLE, ALTER TABLE, CREATE INDEX, dictionary SELECT and DROP of a disposable table; stored outputs. |
| DML | Five modules, each with 1 INSERT, 1 UPDATE, 1 DELETE. Each affects exactly one owned demonstration row, with before/after outputs. |
| TCL | Live COMMIT, SAVEPOINT, ROLLBACK TO SAVEPOINT, full ROLLBACK, with three intermediate result sets. DDL is separate because Oracle auto-commits it. |
| Five SELECTs per person | 25 required SELECTs: search/filter, joins, aggregates, one-level IN subqueries and basic SQL functions in every module. |
| Basic lab topics | Filtering, LIKE/IN, NULL/NVL, joins, GROUP BY/HAVING, nested queries, EXISTS/NOT EXISTS, text/date/numeric functions. Extra UNION/INTERSECT/MINUS, ALL, views, indexes and sequences. |
| Suitable front end | Flask + Jinja + browser forms with actual Oracle connectivity. |
| Insert/Update/Delete/Search/Display | Ordinary staff management forms and the individual Oracle presentation modules. Actual Oracle form insert/edit/delete checks passed for artists, artworks, exhibitions, auctions and appraisals; invalid date order and missing CSRF were rejected (`FORM_VERIFICATION.json`). |
| Individual module ownership | Five member tabs, editable presenter names, 8-statement progress and per-module evidence. |
| Corresponding outputs | `ORACLE_EXECUTION_OUTPUTS.md`, `REPORT_CHAPTER.md`, and downloadable current-session output from the portal. These are real execution records. |
| Group report | Ready-to-incorporate report chapter, division of work, SQL scripts and actual outputs. Fill actual student names/registration numbers and place it in the college report template. |
| Smooth demonstration | Full eight-step sale walkthrough; schema explorer; actual Oracle trigger/Python source; main report pages. |

## Presentation route

Sign in as staff → **Staff desk → Oracle presentation studio**.

Each member selects their module, enters their name, and runs INSERT → UPDATE → DELETE, then the five SELECT queries. To display the new record before deleting it, run the simple search SELECT between INSERT and DELETE. Use **Download my outputs** to retain the executed SQL and results before signing out or clearing browser cookies.

Then present **DDL, TCL & coverage**, **Database explorer**, and **Full sale walkthrough**. All pages use the same Oracle database; the final sale appears in ordinary reports too.

The member names are assigned. Student registration numbers and any college-specific report formatting still need to be filled in by the group; no missing executable SQL feature is being claimed as completed by a mock result.

The named, simplified member sets were re-executed successfully: see `MEMBER_VERIFICATION.json`, `SIMPLE_QUERIES.md` and the five named SQL*Plus transcripts. The earlier `VERIFICATION.json` records the original migration run.
