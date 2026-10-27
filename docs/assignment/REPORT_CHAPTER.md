# Database Implementation Using SQL and Front-End Connectivity

## Art Gallery, Exhibition & Auction Management System

Group members: Vihaan, Kaashvi, Gaurav, Shanil and Ashutosh. Add the student registration numbers before submission.

### Implementation and database provisioning

The application uses Flask, Jinja, python-oracledb 3.0.0 and Oracle Database 11.2.0.2.0. All public pages, authentication, management forms, auctions, reports and presentation actions use Oracle. There is no SQLite runtime fallback.

Oracle XE was already installed and running on the demonstration laptop. The project provisions an isolated ATELIER_PROJECT schema inside that database rather than creating another XE instance. oracle/00_create_user.sql records schema/user creation and privileges; scripts/setup_oracle.py performs non-destructive local setup. oracle/01_schema.sql creates the tables, constraints, indexes, sequence and revenue view. oracle/02_seed.sql populates fictional records; oracle/03_rules.sql installs Oracle triggers; oracle/05_accounts.sql creates the application login table. The setup script hashes the four known demo passwords.

The application user has privileges only to create its own session, tables, views, triggers and sequences, with a bounded tablespace quota. The web server does not connect as SYS or SYSTEM. Actual schema credentials stay in ignored instance/oracle.json or environment variables.

### Relational design and integrity

The 16 domain tables retain the supplied entity attributes. user_account supports authenticated users. lab_workspace and lab_evidence store per-presentation progress and execution outputs, giving 19 tables in total.

Mandatory child relationships use NOT NULL foreign keys. Optional parent participation permits no child records. ARTIST_GALLERY and EXHIBITION_ARTWORK use composite primary keys for their many-to-many relationships. SALE.BID_ID is unique and non-null, implementing zero or one sale per bid and exactly one winning bid per sale. COLLECTOR.BIDDER_ID uniquely links the buyer identity. ART_EXPERT is referenced by APPRAISAL and AUTHENTICATION. GALLERY organizes both exhibitions and auctions. ARTWORK may have multiple historical lots, with a function-based unique index allowing at most one open listing.

Primary keys, foreign keys, UNIQUE, NOT NULL and CHECK constraints protect identities, dates, status, nonnegative money, commission bounds, certificates and lot numbers. Oracle DATE columns store actual calendar dates. Monetary NUMBER(18,0) columns store integer paise; the application validates decimal inputs before converting rupees to paise. Accepted bid amounts and finalized sale details are immutable. The final selling price is stored on SALE, and collector spending is derived from completed payments.

Artist, gallery, curator and expert facts are stored in their own entities. Junction attributes depend on their full composite key. Collector contact fields are retained from the supplied model, and may be considered a snapshot of buyer details; the bidder ID preserves identity. This deliberate retained duplication should not be described as an entirely redundancy-free design.

### Front-end connectivity and operations

Browser → Flask route → role/input/CSRF validation → pooled python-oracledb connection → parameterized Oracle SQL → commit or rollback → Jinja-rendered results. The installed Oracle 11.2 client is used in Thick mode. A bounded pool reuses sessions. Internal qmark convenience placeholders in form routes are converted to named Oracle binds; SQL presets use Oracle syntax directly.

The staff portal demonstrates Insert, Update, Delete, Search and Display. Individual modules mutate only a new, server-assigned demonstration record. Names and search values are bound parameters. Each execution stores the actual statement, binds, before/after results and row count in Oracle. Bidders cannot access staff pages. Password hashes, session signing, server-side role checks and CSRF tokens remain in use.

The eight-step sale walkthrough uses the same Oracle transaction services as the public website. SELECT FOR UPDATE serializes auction/lot writers; a failed operation rolls back all related writes. A winning sale is created only when the highest bid meets reserve, with the matching collector. Payments are simulated and only payment status is mutable.

### Individual division of work

| Presenter | Module | Required statements |
| --- | --- | --- |
| Vihaan | Artists & collection | 1 INSERT, 1 UPDATE, 1 DELETE, 5 SELECT |
| Kaashvi | Galleries & exhibitions | 1 INSERT, 1 UPDATE, 1 DELETE, 5 SELECT |
| Gaurav | Auctions & lots | 1 INSERT, 1 UPDATE, 1 DELETE, 5 SELECT |
| Shanil | Bidders & bids | 1 INSERT, 1 UPDATE, 1 DELETE, 5 SELECT |
| Ashutosh | Experts & appraisals | 1 INSERT, 1 UPDATE, 1 DELETE, 5 SELECT |

Each five-query set covers simple search/filtering, a two-table join, COUNT with GROUP BY, a one-level IN subquery, and a basic SQL function. The group also demonstrates set operations, views, indexes, sequences, DDL and TCL. The supplied clarification limits the lab-sheet expectation to basic SQL topics.

### Executed SQL and corresponding outputs

The following outputs were captured from real Oracle execution through the Flask application. Values describe fictional demonstration records. Empty results are retained as genuine outputs. Full structured evidence is available in ORACLE_EXECUTION_OUTPUTS.md.

## Vihaan: Artists & collection

### INSERT: Create a demonstration record

```sql
INSERT INTO artwork (artwork_id, artist_id, title)
VALUES (:record_id, 1, :value);
```

Bound values: `{"record_id": 100129, "value": "Study in Light"}`

Before:

_No rows returned._

Result:

| artwork_id | artist_id | title | year_created | medium | dimensions | description | status | image_path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100129 | 1 | Study in Light | NULL | NULL | NULL | NULL | available | NULL |

1 row affected. COMMIT completed.

### UPDATE: Update that record

```sql
UPDATE artwork
SET title = :value
WHERE artwork_id = :record_id;
```

Bound values: `{"record_id": 100129, "value": "Study in Light revised"}`

Before:

| artwork_id | artist_id | title | year_created | medium | dimensions | description | status | image_path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100129 | 1 | Study in Light | NULL | NULL | NULL | NULL | available | NULL |

Result:

| artwork_id | artist_id | title | year_created | medium | dimensions | description | status | image_path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100129 | 1 | Study in Light revised | NULL | NULL | NULL | NULL | available | NULL |

1 row affected. COMMIT completed.

### DELETE: Delete that demonstration record

```sql
DELETE FROM artwork
WHERE artwork_id = :record_id;
```

Bound values: `{"record_id": 100129}`

Before:

| artwork_id | artist_id | title | year_created | medium | dimensions | description | status | image_path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100129 | 1 | Study in Light revised | NULL | NULL | NULL | NULL | available | NULL |

Result:

_No rows returned._

1 row affected. COMMIT completed.

### SELECT: Search artworks by title

```sql
SELECT artwork_id, title, medium
FROM artwork
WHERE title LIKE :search;
```

Bound values: `{"search": "%%"}`

Result:

| artwork_id | title | medium |
| --- | --- | --- |
| 1 | Monsoon Reverie | Oil on canvas |
| 2 | A Quiet Morning | Acrylic on canvas |
| 3 | Blue Distance | Oil on linen |
| 4 | The Golden Hour | Mixed media |
| 5 | Garden of Echoes | Acrylic on canvas |
| 6 | Between Tides | Oil on canvas |
| 7 | Window to the City | Watercolour |
| 8 | Soft Horizons | Oil on linen |
| 9 | A Place to Begin | Mixed media |
| 10 | Wild Geometry | Acrylic on canvas |
| 11 | Evening Passage | Oil on canvas |
| 12 | The Light Within | Watercolour |
| 100093 | Transaction demonstration 100092 / 1 | Oil on canvas |
| 100075 | Presentation Study 100075 | Oil on canvas |
| 100095 | Transaction demonstration 100094 / 2 | Oil on canvas |

### SELECT: Show each artwork and its artist

```sql
SELECT w.title, a.name
FROM artwork w
JOIN artist a ON w.artist_id = a.artist_id;
```

Bound values: `{}`

Result:

| title | name |
| --- | --- |
| Monsoon Reverie | Amara Sen |
| A Place to Begin | Amara Sen |
| Transaction demonstration 100092 / 1 | Amara Sen |
| Presentation Study 100075 | Amara Sen |
| Transaction demonstration 100094 / 2 | Amara Sen |
| A Quiet Morning | Kavita Rao |
| Window to the City | Kavita Rao |
| Blue Distance | Isabelle Laurent |
| Soft Horizons | Isabelle Laurent |
| The Golden Hour | Noah Kim |
| The Light Within | Noah Kim |
| Garden of Echoes | Leila Haddad |
| Wild Geometry | Leila Haddad |
| Between Tides | Mateo Alvarez |
| Evening Passage | Mateo Alvarez |

### SELECT: Count artworks for each artist

```sql
SELECT artist_id, COUNT(*) AS total_artworks
FROM artwork
GROUP BY artist_id;
```

Bound values: `{}`

Result:

| artist_id | total_artworks |
| --- | --- |
| 1 | 5 |
| 2 | 2 |
| 3 | 2 |
| 4 | 2 |
| 5 | 2 |
| 6 | 2 |

### SELECT: Find artworks by Indian artists

```sql
SELECT title
FROM artwork
WHERE artist_id IN (
    SELECT artist_id FROM artist WHERE nationality = 'Indian'
);
```

Bound values: `{}`

Result:

| title |
| --- |
| Monsoon Reverie |
| A Place to Begin |
| Transaction demonstration 100092 / 1 |
| Presentation Study 100075 |
| Transaction demonstration 100094 / 2 |
| A Quiet Morning |
| Window to the City |

### SELECT: Show artwork titles in capital letters

```sql
SELECT UPPER(title) AS title_in_capitals
FROM artwork;
```

Bound values: `{}`

Result:

| title_in_capitals |
| --- |
| MONSOON REVERIE |
| A QUIET MORNING |
| BLUE DISTANCE |
| THE GOLDEN HOUR |
| GARDEN OF ECHOES |
| BETWEEN TIDES |
| WINDOW TO THE CITY |
| SOFT HORIZONS |
| A PLACE TO BEGIN |
| WILD GEOMETRY |
| EVENING PASSAGE |
| THE LIGHT WITHIN |
| TRANSACTION DEMONSTRATION 100092 / 1 |
| PRESENTATION STUDY 100075 |
| TRANSACTION DEMONSTRATION 100094 / 2 |

## Kaashvi: Galleries & exhibitions

### INSERT: Create a demonstration record

```sql
INSERT INTO exhibition
    (exhibition_id, gallery_id, curator_id, title, start_date, end_date)
VALUES (:record_id, 1, 1, :value, DATE '2026-11-01', DATE '2026-12-31');
```

Bound values: `{"record_id": 100138, "value": "Light and Memory"}`

Before:

_No rows returned._

Result:

| exhibition_id | gallery_id | curator_id | title | start_date | end_date | theme |
| --- | --- | --- | --- | --- | --- | --- |
| 100138 | 1 | 1 | Light and Memory | 2026-11-01 | 2026-12-31 | NULL |

1 row affected. COMMIT completed.

### UPDATE: Update that record

```sql
UPDATE exhibition
SET title = :value
WHERE exhibition_id = :record_id;
```

Bound values: `{"record_id": 100138, "value": "Light and Memory revised"}`

Before:

| exhibition_id | gallery_id | curator_id | title | start_date | end_date | theme |
| --- | --- | --- | --- | --- | --- | --- |
| 100138 | 1 | 1 | Light and Memory | 2026-11-01 | 2026-12-31 | NULL |

Result:

| exhibition_id | gallery_id | curator_id | title | start_date | end_date | theme |
| --- | --- | --- | --- | --- | --- | --- |
| 100138 | 1 | 1 | Light and Memory revised | 2026-11-01 | 2026-12-31 | NULL |

1 row affected. COMMIT completed.

### DELETE: Delete that demonstration record

```sql
DELETE FROM exhibition
WHERE exhibition_id = :record_id;
```

Bound values: `{"record_id": 100138}`

Before:

| exhibition_id | gallery_id | curator_id | title | start_date | end_date | theme |
| --- | --- | --- | --- | --- | --- | --- |
| 100138 | 1 | 1 | Light and Memory revised | 2026-11-01 | 2026-12-31 | NULL |

Result:

_No rows returned._

1 row affected. COMMIT completed.

### SELECT: Search exhibitions by title

```sql
SELECT exhibition_id, title, start_date, end_date
FROM exhibition
WHERE title LIKE :search;
```

Bound values: `{"search": "%%"}`

Result:

| exhibition_id | title | start_date | end_date |
| --- | --- | --- | --- |
| 100116 | Light and Memory | 2026-11-01 | 2026-12-31 |
| 1 | Colour and Memory | 2026-10-01 | 2026-12-20 |
| 2 | Quiet Places | 2026-11-01 | 2027-01-15 |
| 3 | New Perspectives | 2027-02-01 | 2027-03-31 |

### SELECT: Show each exhibition and its gallery

```sql
SELECT e.title, g.name
FROM exhibition e
JOIN gallery g ON e.gallery_id = g.gallery_id;
```

Bound values: `{}`

Result:

| title | name |
| --- | --- |
| Light and Memory | Atelier Mumbai |
| Colour and Memory | Atelier Mumbai |
| New Perspectives | Atelier Mumbai |
| Quiet Places | Atelier Delhi |

### SELECT: Count exhibitions for each gallery

```sql
SELECT gallery_id, COUNT(*) AS total_exhibitions
FROM exhibition
GROUP BY gallery_id;
```

Bound values: `{}`

Result:

| gallery_id | total_exhibitions |
| --- | --- |
| 1 | 3 |
| 2 | 1 |

### SELECT: Find exhibitions in Mumbai galleries

```sql
SELECT title
FROM exhibition
WHERE gallery_id IN (
    SELECT gallery_id FROM gallery WHERE city = 'Mumbai'
);
```

Bound values: `{}`

Result:

| title |
| --- |
| Light and Memory |
| Colour and Memory |
| New Perspectives |

### SELECT: Format exhibition opening dates

```sql
SELECT title, TO_CHAR(start_date, 'DD-MM-YYYY') AS opening_date
FROM exhibition;
```

Bound values: `{}`

Result:

| title | opening_date |
| --- | --- |
| Light and Memory | 01-11-2026 |
| Colour and Memory | 01-10-2026 |
| Quiet Places | 01-11-2026 |
| New Perspectives | 01-02-2027 |

## Gaurav: Auctions & lots

### INSERT: Create a demonstration record

```sql
INSERT INTO auction (auction_id, gallery_id, title, "DATE")
VALUES (:record_id, 1, :value, DATE '2026-12-15');
```

Bound values: `{"record_id": 100147, "value": "Student Auction"}`

Before:

_No rows returned._

Result:

| auction_id | gallery_id | title | date | venue | description | status |
| --- | --- | --- | --- | --- | --- | --- |
| 100147 | 1 | Student Auction | 2026-12-15 | NULL | NULL | draft |

1 row affected. COMMIT completed.

### UPDATE: Update that record

```sql
UPDATE auction
SET title = :value
WHERE auction_id = :record_id;
```

Bound values: `{"record_id": 100147, "value": "Student Auction revised"}`

Before:

| auction_id | gallery_id | title | date | venue | description | status |
| --- | --- | --- | --- | --- | --- | --- |
| 100147 | 1 | Student Auction | 2026-12-15 | NULL | NULL | draft |

Result:

| auction_id | gallery_id | title | date | venue | description | status |
| --- | --- | --- | --- | --- | --- | --- |
| 100147 | 1 | Student Auction revised | 2026-12-15 | NULL | NULL | draft |

1 row affected. COMMIT completed.

### DELETE: Delete that demonstration record

```sql
DELETE FROM auction
WHERE auction_id = :record_id;
```

Bound values: `{"record_id": 100147}`

Before:

| auction_id | gallery_id | title | date | venue | description | status |
| --- | --- | --- | --- | --- | --- | --- |
| 100147 | 1 | Student Auction revised | 2026-12-15 | NULL | NULL | draft |

Result:

_No rows returned._

1 row affected. COMMIT completed.

### SELECT: Search auctions by title

```sql
SELECT auction_id, title, status
FROM auction
WHERE title LIKE :search;
```

Bound values: `{"search": "%%"}`

Result:

| auction_id | title | status |
| --- | --- | --- |
| 1 | Autumn Contemporary | open |
| 2 | Winter Preview | draft |
| 3 | Recent Acquisitions | closed |
| 100018 | Student Auction Preview — revised | draft |
| 100097 | Transaction demonstration 100096 | closed |
| 100081 | Presentation Auction 100075 | closed |

### SELECT: Show the lots in each auction

```sql
SELECT a.title, l.lot_number
FROM auction a
JOIN auction_lot l ON a.auction_id = l.auction_id;
```

Bound values: `{}`

Result:

| title | lot_number |
| --- | --- |
| Autumn Contemporary | 1 |
| Autumn Contemporary | 2 |
| Winter Preview | 1 |
| Winter Preview | 2 |
| Recent Acquisitions | 1 |
| Recent Acquisitions | 2 |
| Recent Acquisitions | 3 |
| Presentation Auction 100075 | 1 |
| Transaction demonstration 100096 | 1 |
| Transaction demonstration 100096 | 2 |

### SELECT: Count lots for each auction

```sql
SELECT auction_id, COUNT(*) AS total_lots
FROM auction_lot
GROUP BY auction_id;
```

Bound values: `{}`

Result:

| auction_id | total_lots |
| --- | --- |
| 1 | 2 |
| 2 | 2 |
| 3 | 3 |
| 100081 | 1 |
| 100097 | 2 |

### SELECT: Find lots belonging to open auctions

```sql
SELECT lot_id, lot_number
FROM auction_lot
WHERE auction_id IN (
    SELECT auction_id FROM auction WHERE status = 'open'
);
```

Bound values: `{}`

Result:

| lot_id | lot_number |
| --- | --- |
| 101 | 1 |
| 102 | 2 |

### SELECT: Show starting prices in rupees

```sql
SELECT lot_id, ROUND(starting_price / 100, 2) AS starting_price_inr
FROM auction_lot;
```

Bound values: `{}`

Result:

| lot_id | starting_price_inr |
| --- | --- |
| 101 | 50000 |
| 102 | 30000 |
| 201 | 45000 |
| 202 | 25000 |
| 301 | 40000 |
| 302 | 30000 |
| 303 | 20000 |
| 100082 | 50000 |
| 100098 | 50000 |
| 100099 | 10000 |

## Shanil: Bidders & bids

### INSERT: Create a demonstration record

```sql
INSERT INTO bidder (bidder_id, name, email)
VALUES (:record_id, :value, :email);
```

Bound values: `{"record_id": 100156, "value": "Demo Bidder", "email": "demo-100156@atelier.example"}`

Before:

_No rows returned._

Result:

| bidder_id | name | email | phone | address |
| --- | --- | --- | --- | --- |
| 100156 | Demo Bidder | demo-100156@atelier.example | NULL | NULL |

1 row affected. COMMIT completed.

### UPDATE: Update that record

```sql
UPDATE bidder
SET name = :value
WHERE bidder_id = :record_id;
```

Bound values: `{"record_id": 100156, "value": "Demo Bidder revised"}`

Before:

| bidder_id | name | email | phone | address |
| --- | --- | --- | --- | --- |
| 100156 | Demo Bidder | demo-100156@atelier.example | NULL | NULL |

Result:

| bidder_id | name | email | phone | address |
| --- | --- | --- | --- | --- |
| 100156 | Demo Bidder revised | demo-100156@atelier.example | NULL | NULL |

1 row affected. COMMIT completed.

### DELETE: Delete that demonstration record

```sql
DELETE FROM bidder
WHERE bidder_id = :record_id;
```

Bound values: `{"record_id": 100156}`

Before:

| bidder_id | name | email | phone | address |
| --- | --- | --- | --- | --- |
| 100156 | Demo Bidder revised | demo-100156@atelier.example | NULL | NULL |

Result:

_No rows returned._

1 row affected. COMMIT completed.

### SELECT: Search bidders by name

```sql
SELECT bidder_id, name, email
FROM bidder
WHERE name LIKE :search;
```

Bound values: `{"search": "%%"}`

Result:

| bidder_id | name | email |
| --- | --- | --- |
| 1 | Maya Sharma | maya@atelier.example |
| 2 | Arjun Patel | arjun@atelier.example |
| 3 | Sara Khan | sara@atelier.example |
| 100101 | Transaction Demo Bidder | transaction-100100@atelier.example |

### SELECT: Show bids with bidder names

```sql
SELECT r.name, b.bid_amount / 100 AS amount_inr
FROM bidder r
JOIN bid b ON r.bidder_id = b.bidder_id;
```

Bound values: `{}`

Result:

| name | amount_inr |
| --- | --- |
| Maya Sharma | 50000 |
| Maya Sharma | 35000 |
| Maya Sharma | 55000 |
| Maya Sharma | 30000 |
| Maya Sharma | 20000 |
| Maya Sharma | 50000000 |
| Maya Sharma | 65000 |
| Maya Sharma | 15000 |
| Maya Sharma | 60000 |
| Arjun Patel | 55000 |
| Arjun Patel | 30000 |
| Arjun Patel | 40000 |
| Arjun Patel | 45000 |
| Arjun Patel | 25000 |
| Sara Khan | 70000 |
| Transaction Demo Bidder | 70000 |

### SELECT: Count bids for each bidder

```sql
SELECT bidder_id, COUNT(*) AS total_bids
FROM bid
GROUP BY bidder_id;
```

Bound values: `{}`

Result:

| bidder_id | total_bids |
| --- | --- |
| 1 | 9 |
| 2 | 5 |
| 3 | 1 |
| 100101 | 1 |

### SELECT: Find bidders who placed a bid

```sql
SELECT name
FROM bidder
WHERE bidder_id IN (
    SELECT bidder_id FROM bid
);
```

Bound values: `{}`

Result:

| name |
| --- |
| Maya Sharma |
| Arjun Patel |
| Sara Khan |
| Transaction Demo Bidder |

### SELECT: Show bidder emails in lowercase

```sql
SELECT name, LOWER(email) AS email
FROM bidder;
```

Bound values: `{}`

Result:

| name | email |
| --- | --- |
| Maya Sharma | maya@atelier.example |
| Arjun Patel | arjun@atelier.example |
| Sara Khan | sara@atelier.example |
| Transaction Demo Bidder | transaction-100100@atelier.example |

## Ashutosh: Experts & appraisals

### INSERT: Create a demonstration record

```sql
INSERT INTO art_expert (expert_id, name)
VALUES (:record_id, :value);
```

Bound values: `{"record_id": 100165, "value": "Demo Expert"}`

Before:

_No rows returned._

Result:

| expert_id | name | specialization | email | phone |
| --- | --- | --- | --- | --- |
| 100165 | Demo Expert | NULL | NULL | NULL |

1 row affected. COMMIT completed.

### UPDATE: Update that record

```sql
UPDATE art_expert
SET name = :value
WHERE expert_id = :record_id;
```

Bound values: `{"record_id": 100165, "value": "Demo Expert revised"}`

Before:

| expert_id | name | specialization | email | phone |
| --- | --- | --- | --- | --- |
| 100165 | Demo Expert | NULL | NULL | NULL |

Result:

| expert_id | name | specialization | email | phone |
| --- | --- | --- | --- | --- |
| 100165 | Demo Expert revised | NULL | NULL | NULL |

1 row affected. COMMIT completed.

### DELETE: Delete that demonstration record

```sql
DELETE FROM art_expert
WHERE expert_id = :record_id;
```

Bound values: `{"record_id": 100165}`

Before:

| expert_id | name | specialization | email | phone |
| --- | --- | --- | --- | --- |
| 100165 | Demo Expert revised | NULL | NULL | NULL |

Result:

_No rows returned._

1 row affected. COMMIT completed.

### SELECT: Search experts by name

```sql
SELECT expert_id, name, specialization
FROM art_expert
WHERE name LIKE :search;
```

Bound values: `{"search": "%%"}`

Result:

| expert_id | name | specialization |
| --- | --- | --- |
| 1 | Dr. Anika Desai | Modern painting |
| 2 | Daniel Roy | Contemporary art |

### SELECT: Show appraisals with expert names

```sql
SELECT e.name, p.estimated_value / 100 AS value_inr
FROM art_expert e
JOIN appraisal p ON e.expert_id = p.expert_id;
```

Bound values: `{}`

Result:

| name | value_inr |
| --- | --- |
| Dr. Anika Desai | 65000 |
| Dr. Anika Desai | 80000 |
| Daniel Roy | 80000 |

### SELECT: Count appraisals for each expert

```sql
SELECT expert_id, COUNT(*) AS total_appraisals
FROM appraisal
GROUP BY expert_id;
```

Bound values: `{}`

Result:

| expert_id | total_appraisals |
| --- | --- |
| 1 | 2 |
| 2 | 1 |

### SELECT: Find experts who performed an appraisal

```sql
SELECT name
FROM art_expert
WHERE expert_id IN (
    SELECT expert_id FROM appraisal
);
```

Bound values: `{}`

Result:

| name |
| --- |
| Dr. Anika Desai |
| Daniel Roy |

### SELECT: Show expert names in capital letters

```sql
SELECT UPPER(name) AS expert_name
FROM art_expert;
```

Bound values: `{}`

Result:

| expert_name |
| --- |
| DR. ANIKA DESAI |
| DANIEL ROY |

## Group DDL, TCL and additional SELECT evidence

### DDL demonstration

```sql
CREATE TABLE LAB_DDL_100066 (example_id NUMBER PRIMARY KEY,note VARCHAR2(100));
ALTER TABLE LAB_DDL_100066 ADD created_on DATE DEFAULT SYSDATE;
CREATE INDEX LAB_DDL_100066_IX ON LAB_DDL_100066(note);
SELECT column_name,data_type FROM user_tab_columns WHERE table_name='LAB_DDL_100066' ORDER BY column_id;
DROP TABLE LAB_DDL_100066 PURGE;
```

Statement output 1:

| column_name | data_type |
| --- | --- |
| EXAMPLE_ID | NUMBER |
| NOTE | VARCHAR2 |
| CREATED_ON | DATE |

### TCL demonstration

```sql
INSERT INTO curator(curator_id,name) VALUES(:id,'TCL demonstration');
COMMIT;
SAVEPOINT before_change;
UPDATE curator SET name='Temporary value' WHERE curator_id=:id;
SELECT curator_id,name FROM curator WHERE curator_id=:id;
ROLLBACK TO before_change;
SELECT curator_id,name FROM curator WHERE curator_id=:id;
DELETE FROM curator WHERE curator_id=:id;
ROLLBACK;
SELECT curator_id,name FROM curator WHERE curator_id=:id;
DELETE FROM curator WHERE curator_id=:id;
COMMIT;
```

Statement output 1:

| curator_id | name |
| --- | --- |
| 100068 | Temporary value |

Statement output 2:

| curator_id | name |
| --- | --- |
| 100068 | TCL demonstration |

Statement output 3:

| curator_id | name |
| --- | --- |
| 100068 | TCL demonstration |

### UNION: people who participate in the art system

```sql
SELECT name FROM artist UNION SELECT name FROM art_expert ORDER BY name;
```

Statement output 1:

| name |
| --- |
| Amara Sen |
| Daniel Roy |
| Dr. Anika Desai |
| Isabelle Laurent |
| Kavita Rao |
| Leila Haddad |
| Mateo Alvarez |
| Noah Kim |

### INTERSECT: artworks with both assessments

```sql
SELECT artwork_id FROM appraisal INTERSECT SELECT artwork_id FROM authentication;
```

Statement output 1:

| artwork_id |
| --- |
| 1 |
| 4 |

### MINUS: artworks without authentication

```sql
SELECT artwork_id FROM artwork MINUS SELECT artwork_id FROM authentication;
```

Statement output 1:

| artwork_id |
| --- |
| 2 |
| 3 |
| 5 |
| 6 |
| 7 |
| 8 |
| 9 |
| 10 |
| 11 |
| 12 |

### View: completed gallery revenue

```sql
SELECT gallery_id,name,paid_sales,revenue_inr FROM gallery_revenue ORDER BY gallery_id;
```

Statement output 1:

| gallery_id | name | paid_sales | revenue_inr |
| --- | --- | --- | --- |
| 1 | Atelier Mumbai | 1 | 55000 |
| 2 | Atelier Delhi | 0 | 0 |

### ALL: appraisals at least as large as every appraisal

```sql
SELECT appraisal_id,estimated_value/100 AS estimate_inr FROM appraisal WHERE estimated_value >= ALL (SELECT estimated_value FROM appraisal);
```

Statement output 1:

| appraisal_id | estimate_inr |
| --- | --- |
| 2 | 80000 |

## Complete presentation walkthrough

### Create an artwork

Executed SQL and per-statement parameters are retained in the structured evidence export.

| artwork_id | title | status |
| --- | --- | --- |
| 100075 | Presentation Study 100075 | available |

### Assign it to an exhibition

Executed SQL and per-statement parameters are retained in the structured evidence export.

| artwork_id | title | status |
| --- | --- | --- |
| 100075 | Presentation Study 100075 | available |

### Record expert assessments

Executed SQL and per-statement parameters are retained in the structured evidence export.

| artwork_id | title | status |
| --- | --- | --- |
| 100075 | Presentation Study 100075 | available |

### Create and open an auction

Executed SQL and per-statement parameters are retained in the structured evidence export.

| artwork_id | title | status |
| --- | --- | --- |
| 100075 | Presentation Study 100075 | at_auction |

| lot_id | status | highest_bid_inr |
| --- | --- | --- |
| 100082 | open | NULL |

### Maya bids ₹65,000

Executed SQL and per-statement parameters are retained in the structured evidence export.

| artwork_id | title | status |
| --- | --- | --- |
| 100075 | Presentation Study 100075 | at_auction |

| lot_id | status | highest_bid_inr |
| --- | --- | --- |
| 100082 | open | 65000 |

### Sara bids ₹70,000

Executed SQL and per-statement parameters are retained in the structured evidence export.

| artwork_id | title | status |
| --- | --- | --- |
| 100075 | Presentation Study 100075 | at_auction |

| lot_id | status | highest_bid_inr |
| --- | --- | --- |
| 100082 | open | 70000 |

### Close the lot and record the sale

Executed SQL and per-statement parameters are retained in the structured evidence export.

| artwork_id | title | status |
| --- | --- | --- |
| 100075 | Presentation Study 100075 | sold |

| lot_id | status | highest_bid_inr |
| --- | --- | --- |
| 100082 | sold | 70000 |

| sale_id | sale_inr | payment_status |
| --- | --- | --- |
| 100089 | 70000 | pending |

| gallery_id | name | paid_sales | revenue_inr |
| --- | --- | --- | --- |
| 1 | Atelier Mumbai | 1 | 55000 |
| 2 | Atelier Delhi | 0 | 0 |

### Complete payment and show revenue

Executed SQL and per-statement parameters are retained in the structured evidence export.

| artwork_id | title | status |
| --- | --- | --- |
| 100075 | Presentation Study 100075 | sold |

| lot_id | status | highest_bid_inr |
| --- | --- | --- |
| 100082 | sold | 70000 |

| sale_id | sale_inr | payment_status |
| --- | --- | --- |
| 100089 | 70000 | completed |

| gallery_id | name | paid_sales | revenue_inr |
| --- | --- | --- | --- |
| 1 | Atelier Mumbai | 2 | 125000 |
| 2 | Atelier Delhi | 0 | 0 |

## Verification and limitations

Four demo accounts authenticated with their assigned permissions. Public pages, all domain management pages, six reports, all 40 individual statements, seven supplements and the eight-step sale workflow executed successfully on Oracle.

- Bid below starting price rejected.
- Concurrent equal bids: exactly one accepted, one rejected.
- Failed close rolls back new collector, sale and lot/artwork status.
- Concurrent closure is idempotent: one sale, same result to both callers.
- Reserve not met: unsold lot, no sale, artwork available.
- Database rejects bid edits, sale deletion/price edits and missing foreign keys.
- Finalized sale persists across independent Oracle connections.

The original SQLite file remains an unchanged migration backup, not the running database. Initial counts matched across all 17 application tables during migration. Normal startup does not reset or reseed Oracle. The earlier SQLite-specific tests are archived as historical material, and are not presented as Oracle verification.

The project demonstrates simulated auctions and payments locally. The report chapter and SQL outputs should be incorporated into the institution’s final report template, with the student registration numbers.

## References

- [Oracle Database 11g SQL Language Reference](https://docs.oracle.com/cd/E11882_01/server.112/e41084.pdf)
- [python-oracledb 3.0 installation and client compatibility](https://python-oracledb.readthedocs.io/en/v3.0.0/user_guide/installation.html)
- [Oracle transaction control and DDL commits](https://docs.oracle.com/en/database/oracle/oracle-database/21/tdddg/dml-and-transactions.html)
