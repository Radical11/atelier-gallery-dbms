-- SQL*Plus alternative to scripts/setup_oracle.py. Run as a local administrator.
-- On this laptop XE already exists: provision a dedicated USER/SCHEMA within XE.
-- CREATE DATABASE would create a different instance; it is not required per project.
-- No existing practice users are altered. NEVER run these as the web application's login.
SET VERIFY OFF
ACCEPT atelier_password CHAR PROMPT 'Choose a NEW ATELIER_PROJECT schema password: ' HIDE
CREATE USER ATELIER_PROJECT IDENTIFIED BY "&atelier_password"
  DEFAULT TABLESPACE USERS TEMPORARY TABLESPACE TEMP QUOTA 200M ON USERS;
GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE TRIGGER, CREATE SEQUENCE TO ATELIER_PROJECT;
UNDEFINE atelier_password
