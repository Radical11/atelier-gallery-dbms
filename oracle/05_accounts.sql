CREATE TABLE user_account (
  user_id NUMBER(10) PRIMARY KEY, email VARCHAR2(200 CHAR) NOT NULL UNIQUE,
  password_hash VARCHAR2(1000 CHAR) NOT NULL, role VARCHAR2(20) NOT NULL,
  bidder_id NUMBER(10) UNIQUE REFERENCES bidder(bidder_id),
  CONSTRAINT ck_user_role CHECK (role IN ('staff','bidder')),
  CONSTRAINT ck_user_identity CHECK ((role='staff' AND bidder_id IS NULL) OR (role='bidder' AND bidder_id IS NOT NULL))
);
