-- Educational examples run only inside the isolated assignment schema.
-- DDL is separate: Oracle implicitly commits around DDL.
CREATE TABLE lab_ddl_example (example_id NUMBER PRIMARY KEY, note VARCHAR2(100 CHAR));
ALTER TABLE lab_ddl_example ADD created_on DATE DEFAULT SYSDATE;
CREATE INDEX lab_ddl_note_idx ON lab_ddl_example(note);
SELECT column_name,data_type FROM user_tab_columns WHERE table_name='LAB_DDL_EXAMPLE' ORDER BY column_id;
DROP TABLE lab_ddl_example PURGE;
-- TCL. No DDL appears between SAVEPOINT and ROLLBACK TO.
INSERT INTO curator(curator_id,name,email) VALUES (999999,'TCL demonstration','tcl@atelier.example');
COMMIT;
SAVEPOINT before_change;
UPDATE curator SET name='Temporary value' WHERE curator_id=999999;
SELECT curator_id,name FROM curator WHERE curator_id=999999;
ROLLBACK TO before_change;
SELECT curator_id,name FROM curator WHERE curator_id=999999;
DELETE FROM curator WHERE curator_id=999999;
ROLLBACK;
SELECT curator_id,name FROM curator WHERE curator_id=999999;
DELETE FROM curator WHERE curator_id=999999;
COMMIT;
