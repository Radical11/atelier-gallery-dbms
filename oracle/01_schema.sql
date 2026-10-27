-- Oracle 11g XE compatible. Run ONLY in the dedicated ATELIER_PROJECT schema.
-- Original atelier/schema.sql and the SQLite database are unchanged.
CREATE TABLE artist (
  artist_id NUMBER(10) PRIMARY KEY, name VARCHAR2(200 CHAR) NOT NULL,
  birth_date DATE, death_date DATE, nationality VARCHAR2(100 CHAR), biography VARCHAR2(1000 CHAR),
  CONSTRAINT ck_artist_dates CHECK (death_date IS NULL OR birth_date IS NULL OR death_date >= birth_date)
);
CREATE TABLE artwork (
  artwork_id NUMBER(10) PRIMARY KEY, artist_id NUMBER(10) NOT NULL REFERENCES artist(artist_id),
  title VARCHAR2(200 CHAR) NOT NULL, year_created NUMBER(4), medium VARCHAR2(100 CHAR),
  dimensions VARCHAR2(100 CHAR), description VARCHAR2(1000 CHAR),
  status VARCHAR2(20) DEFAULT 'available' NOT NULL,
  image_path VARCHAR2(200 CHAR), CONSTRAINT ck_artwork_status CHECK (status IN ('available','at_auction','sold'))
);
CREATE TABLE gallery (
  gallery_id NUMBER(10) PRIMARY KEY, name VARCHAR2(200 CHAR) NOT NULL,
  address VARCHAR2(300 CHAR), city VARCHAR2(100 CHAR), country VARCHAR2(100 CHAR), contact_info VARCHAR2(200 CHAR)
);
CREATE TABLE curator (
  curator_id NUMBER(10) PRIMARY KEY, name VARCHAR2(200 CHAR) NOT NULL,
  email VARCHAR2(200 CHAR), phone VARCHAR2(50 CHAR)
);
CREATE TABLE exhibition (
  exhibition_id NUMBER(10) PRIMARY KEY, gallery_id NUMBER(10) NOT NULL REFERENCES gallery(gallery_id),
  curator_id NUMBER(10) NOT NULL REFERENCES curator(curator_id), title VARCHAR2(200 CHAR) NOT NULL,
  start_date DATE NOT NULL, end_date DATE NOT NULL, theme VARCHAR2(300 CHAR),
  CONSTRAINT ck_exhibition_dates CHECK (end_date >= start_date)
);
CREATE TABLE auction (
  auction_id NUMBER(10) PRIMARY KEY, gallery_id NUMBER(10) NOT NULL REFERENCES gallery(gallery_id),
  title VARCHAR2(200 CHAR) NOT NULL, "DATE" DATE NOT NULL, venue VARCHAR2(200 CHAR),
  description VARCHAR2(1000 CHAR), status VARCHAR2(20) DEFAULT 'draft' NOT NULL,
  CONSTRAINT ck_auction_status CHECK (status IN ('draft','open','closed'))
);
CREATE TABLE auction_lot (
  lot_id NUMBER(10) PRIMARY KEY, auction_id NUMBER(10) NOT NULL REFERENCES auction(auction_id),
  artwork_id NUMBER(10) NOT NULL REFERENCES artwork(artwork_id), lot_number NUMBER(10) NOT NULL,
  starting_price NUMBER(18,0) NOT NULL, reserve_price NUMBER(18,0) NOT NULL,
  status VARCHAR2(20) DEFAULT 'draft' NOT NULL,
  CONSTRAINT ck_lot_number CHECK (lot_number > 0),
  CONSTRAINT ck_lot_prices CHECK (starting_price >= 0 AND reserve_price >= 0),
  CONSTRAINT ck_lot_status CHECK (status IN ('draft','open','sold','unsold')),
  CONSTRAINT uq_lot_artwork UNIQUE (auction_id, artwork_id),
  CONSTRAINT uq_lot_number UNIQUE (auction_id, lot_number)
);
-- Oracle equivalent of SQLite's partial unique index: non-open rows index NULL.
CREATE UNIQUE INDEX one_active_artwork_lot ON auction_lot (CASE WHEN status='open' THEN artwork_id END);
CREATE TABLE bidder (
  bidder_id NUMBER(10) PRIMARY KEY, name VARCHAR2(200 CHAR) NOT NULL,
  email VARCHAR2(200 CHAR) NOT NULL UNIQUE, phone VARCHAR2(50 CHAR), address VARCHAR2(300 CHAR)
);
CREATE TABLE bid (
  bid_id NUMBER(10) PRIMARY KEY, lot_id NUMBER(10) NOT NULL REFERENCES auction_lot(lot_id),
  bidder_id NUMBER(10) NOT NULL REFERENCES bidder(bidder_id), bid_amount NUMBER(18,0) NOT NULL,
  bid_time TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL, CONSTRAINT ck_bid_amount CHECK (bid_amount >= 0)
);
CREATE TABLE collector (
  collector_id NUMBER(10) PRIMARY KEY, bidder_id NUMBER(10) NOT NULL UNIQUE REFERENCES bidder(bidder_id),
  name VARCHAR2(200 CHAR) NOT NULL, email VARCHAR2(200 CHAR), phone VARCHAR2(50 CHAR), address VARCHAR2(300 CHAR)
);
CREATE TABLE sale (
  sale_id NUMBER(10) PRIMARY KEY, bid_id NUMBER(10) NOT NULL UNIQUE REFERENCES bid(bid_id),
  collector_id NUMBER(10) NOT NULL REFERENCES collector(collector_id), sale_price NUMBER(18,0) NOT NULL,
  sale_date DATE NOT NULL, payment_status VARCHAR2(20) DEFAULT 'pending' NOT NULL,
  CONSTRAINT ck_sale_price CHECK (sale_price >= 0),
  CONSTRAINT ck_payment_status CHECK (payment_status IN ('pending','completed'))
);
CREATE TABLE art_expert (
  expert_id NUMBER(10) PRIMARY KEY, name VARCHAR2(200 CHAR) NOT NULL,
  specialization VARCHAR2(200 CHAR), email VARCHAR2(200 CHAR), phone VARCHAR2(50 CHAR)
);
CREATE TABLE appraisal (
  appraisal_id NUMBER(10) PRIMARY KEY, artwork_id NUMBER(10) NOT NULL REFERENCES artwork(artwork_id),
  expert_id NUMBER(10) NOT NULL REFERENCES art_expert(expert_id), appraisal_date DATE NOT NULL,
  estimated_value NUMBER(18,0) NOT NULL, notes VARCHAR2(1000 CHAR),
  CONSTRAINT ck_appraisal_value CHECK (estimated_value >= 0)
);
CREATE TABLE authentication (
  authentication_id NUMBER(10) PRIMARY KEY, artwork_id NUMBER(10) NOT NULL REFERENCES artwork(artwork_id),
  expert_id NUMBER(10) NOT NULL REFERENCES art_expert(expert_id), certificate_no VARCHAR2(100 CHAR) NOT NULL UNIQUE,
  authentication_date DATE NOT NULL, result VARCHAR2(100 CHAR) NOT NULL, notes VARCHAR2(1000 CHAR)
);
CREATE TABLE artist_gallery (
  artist_id NUMBER(10) NOT NULL REFERENCES artist(artist_id), gallery_id NUMBER(10) NOT NULL REFERENCES gallery(gallery_id),
  start_date DATE NOT NULL, end_date DATE, commission_percentage NUMBER(5,2) NOT NULL,
  PRIMARY KEY (artist_id,gallery_id),
  CONSTRAINT ck_representation_dates CHECK (end_date IS NULL OR end_date >= start_date),
  CONSTRAINT ck_commission CHECK (commission_percentage BETWEEN 0 AND 100)
);
CREATE TABLE exhibition_artwork (
  exhibition_id NUMBER(10) NOT NULL REFERENCES exhibition(exhibition_id),
  artwork_id NUMBER(10) NOT NULL REFERENCES artwork(artwork_id), display_position VARCHAR2(200 CHAR),
  PRIMARY KEY (exhibition_id,artwork_id)
);
CREATE INDEX idx_artwork_artist ON artwork(artist_id);
CREATE INDEX idx_exhibition_gallery ON exhibition(gallery_id);
CREATE INDEX idx_exhibition_curator ON exhibition(curator_id);
CREATE INDEX idx_ag_gallery ON artist_gallery(gallery_id);
CREATE INDEX idx_ea_artwork ON exhibition_artwork(artwork_id);
CREATE INDEX idx_auction_gallery ON auction(gallery_id);
CREATE INDEX idx_lot_artwork ON auction_lot(artwork_id);
CREATE INDEX idx_bid_lot_amount ON bid(lot_id,bid_amount DESC);
CREATE INDEX idx_bid_bidder ON bid(bidder_id);
CREATE INDEX idx_sale_collector ON sale(collector_id);
CREATE INDEX idx_appraisal_artwork ON appraisal(artwork_id,appraisal_date DESC);
CREATE INDEX idx_appraisal_expert ON appraisal(expert_id);
CREATE INDEX idx_auth_artwork ON authentication(artwork_id,authentication_date DESC);
CREATE INDEX idx_auth_expert ON authentication(expert_id);
-- Presentation infrastructure, separate from the 16 domain tables.
CREATE SEQUENCE lab_id_seq START WITH 100000 INCREMENT BY 1 NOCACHE;
CREATE TABLE lab_workspace (
  workspace_id VARCHAR2(32) NOT NULL, module_id VARCHAR2(30) NOT NULL,
  record_id NUMBER(10) NOT NULL UNIQUE, stage NUMBER(1) DEFAULT 0 NOT NULL,
  presenter VARCHAR2(100 CHAR), PRIMARY KEY (workspace_id,module_id)
);
CREATE TABLE lab_evidence (
  evidence_id NUMBER(10) PRIMARY KEY, workspace_id VARCHAR2(32) NOT NULL,
  module_id VARCHAR2(30) NOT NULL, query_id VARCHAR2(30) NOT NULL,
  executed_at TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  payload CLOB NOT NULL
);
CREATE INDEX idx_lab_evidence_workspace ON lab_evidence(workspace_id,module_id,evidence_id);
CREATE VIEW gallery_revenue AS
SELECT g.gallery_id, g.name, COUNT(s.sale_id) paid_sales,
       ROUND(NVL(SUM(s.sale_price),0)/100,2) revenue_inr
FROM gallery g
LEFT JOIN auction a ON a.gallery_id=g.gallery_id
LEFT JOIN auction_lot l ON l.auction_id=a.auction_id
LEFT JOIN bid b ON b.lot_id=l.lot_id
LEFT JOIN sale s ON s.bid_id=b.bid_id AND s.payment_status='completed'
GROUP BY g.gallery_id,g.name;
