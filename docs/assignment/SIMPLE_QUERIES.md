# Simple SQL queries for the five presenters

Each person has the same pattern: INSERT, UPDATE, DELETE, search, two-table JOIN, COUNT/GROUP BY, one IN subquery, and one basic function. The join supplies the assignment’s more complex SELECT; the nested query and function are retained because the brief asks for them.

## How to use the examples

Open Staff desk → Oracle presentation studio and choose your name. Run INSERT → UPDATE → DELETE, then the five SELECT buttons. To see your new record, run the search SELECT before DELETE too.

` :record_id ` is the ID generated for your demonstration row. ` :value ` is the title or name entered in the form; ` :email ` is a unique fictional email for Shanil’s bidder. ` :search ` contains `%` for all rows or `%word%` to find a word. These are bound values, so you do not need to memorize a particular numeric ID.

The INSERT examples include only mandatory fields. Other details may remain NULL or use their defaults. Existing artist/gallery/curator ID 1 is used as the parent. Oracle dates use `DATE 'YYYY-MM-DD'`. Monetary columns store paise, so divide by 100 to display rupees. Search uses LIKE and is case-sensitive.

| Presenter | Module |
| --- | --- |
| Vihaan | Artists & collection |
| Kaashvi | Galleries & exhibitions |
| Gaurav | Auctions & lots |
| Shanil | Bidders & bids |
| Ashutosh | Experts & appraisals |

## Vihaan — Artists & collection

### 1. Create a demonstration record

```sql
INSERT INTO artwork (artwork_id, artist_id, title)
VALUES (:record_id, 1, :value);
```

Add one new record.

### 2. Update that record

```sql
UPDATE artwork
SET title = :value
WHERE artwork_id = :record_id;
```

Change only that record’s title or name.

### 3. Delete that demonstration record

```sql
DELETE FROM artwork
WHERE artwork_id = :record_id;
```

Remove only that unreferenced demonstration record.

### 4. Search artworks by title

```sql
SELECT artwork_id, title, medium
FROM artwork
WHERE title LIKE :search;
```

LIKE finds names or titles matching the search value.

### 5. Show each artwork and its artist

```sql
SELECT w.title, a.name
FROM artwork w
JOIN artist a ON w.artist_id = a.artist_id;
```

JOIN combines two tables using their matching ID columns.

### 6. Count artworks for each artist

```sql
SELECT artist_id, COUNT(*) AS total_artworks
FROM artwork
GROUP BY artist_id;
```

GROUP BY creates one group per parent ID; COUNT(*) counts the rows in that group.

### 7. Find artworks by Indian artists

```sql
SELECT title
FROM artwork
WHERE artist_id IN (
    SELECT artist_id FROM artist WHERE nationality = 'Indian'
);
```

The inner SELECT finds IDs; the outer SELECT displays records whose ID appears in that list.

### 8. Show artwork titles in capital letters

```sql
SELECT UPPER(title) AS title_in_capitals
FROM artwork;
```

A built-in function formats or transforms the displayed result without changing stored data.


## Kaashvi — Galleries & exhibitions

### 1. Create a demonstration record

```sql
INSERT INTO exhibition
    (exhibition_id, gallery_id, curator_id, title, start_date, end_date)
VALUES (:record_id, 1, 1, :value, DATE '2026-11-01', DATE '2026-12-31');
```

Add one new record.

### 2. Update that record

```sql
UPDATE exhibition
SET title = :value
WHERE exhibition_id = :record_id;
```

Change only that record’s title or name.

### 3. Delete that demonstration record

```sql
DELETE FROM exhibition
WHERE exhibition_id = :record_id;
```

Remove only that unreferenced demonstration record.

### 4. Search exhibitions by title

```sql
SELECT exhibition_id, title, start_date, end_date
FROM exhibition
WHERE title LIKE :search;
```

LIKE finds names or titles matching the search value.

### 5. Show each exhibition and its gallery

```sql
SELECT e.title, g.name
FROM exhibition e
JOIN gallery g ON e.gallery_id = g.gallery_id;
```

JOIN combines two tables using their matching ID columns.

### 6. Count exhibitions for each gallery

```sql
SELECT gallery_id, COUNT(*) AS total_exhibitions
FROM exhibition
GROUP BY gallery_id;
```

GROUP BY creates one group per parent ID; COUNT(*) counts the rows in that group.

### 7. Find exhibitions in Mumbai galleries

```sql
SELECT title
FROM exhibition
WHERE gallery_id IN (
    SELECT gallery_id FROM gallery WHERE city = 'Mumbai'
);
```

The inner SELECT finds IDs; the outer SELECT displays records whose ID appears in that list.

### 8. Format exhibition opening dates

```sql
SELECT title, TO_CHAR(start_date, 'DD-MM-YYYY') AS opening_date
FROM exhibition;
```

A built-in function formats or transforms the displayed result without changing stored data.


## Gaurav — Auctions & lots

### 1. Create a demonstration record

```sql
INSERT INTO auction (auction_id, gallery_id, title, "DATE")
VALUES (:record_id, 1, :value, DATE '2026-12-15');
```

Add one new record.

### 2. Update that record

```sql
UPDATE auction
SET title = :value
WHERE auction_id = :record_id;
```

Change only that record’s title or name.

### 3. Delete that demonstration record

```sql
DELETE FROM auction
WHERE auction_id = :record_id;
```

Remove only that unreferenced demonstration record.

### 4. Search auctions by title

```sql
SELECT auction_id, title, status
FROM auction
WHERE title LIKE :search;
```

LIKE finds names or titles matching the search value.

### 5. Show the lots in each auction

```sql
SELECT a.title, l.lot_number
FROM auction a
JOIN auction_lot l ON a.auction_id = l.auction_id;
```

JOIN combines two tables using their matching ID columns.

### 6. Count lots for each auction

```sql
SELECT auction_id, COUNT(*) AS total_lots
FROM auction_lot
GROUP BY auction_id;
```

GROUP BY creates one group per parent ID; COUNT(*) counts the rows in that group.

### 7. Find lots belonging to open auctions

```sql
SELECT lot_id, lot_number
FROM auction_lot
WHERE auction_id IN (
    SELECT auction_id FROM auction WHERE status = 'open'
);
```

The inner SELECT finds IDs; the outer SELECT displays records whose ID appears in that list.

### 8. Show starting prices in rupees

```sql
SELECT lot_id, ROUND(starting_price / 100, 2) AS starting_price_inr
FROM auction_lot;
```

A built-in function formats or transforms the displayed result without changing stored data.


## Shanil — Bidders & bids

### 1. Create a demonstration record

```sql
INSERT INTO bidder (bidder_id, name, email)
VALUES (:record_id, :value, :email);
```

Add one new record.

### 2. Update that record

```sql
UPDATE bidder
SET name = :value
WHERE bidder_id = :record_id;
```

Change only that record’s title or name.

### 3. Delete that demonstration record

```sql
DELETE FROM bidder
WHERE bidder_id = :record_id;
```

Remove only that unreferenced demonstration record.

### 4. Search bidders by name

```sql
SELECT bidder_id, name, email
FROM bidder
WHERE name LIKE :search;
```

LIKE finds names or titles matching the search value.

### 5. Show bids with bidder names

```sql
SELECT r.name, b.bid_amount / 100 AS amount_inr
FROM bidder r
JOIN bid b ON r.bidder_id = b.bidder_id;
```

JOIN combines two tables using their matching ID columns.

### 6. Count bids for each bidder

```sql
SELECT bidder_id, COUNT(*) AS total_bids
FROM bid
GROUP BY bidder_id;
```

GROUP BY creates one group per parent ID; COUNT(*) counts the rows in that group.

### 7. Find bidders who placed a bid

```sql
SELECT name
FROM bidder
WHERE bidder_id IN (
    SELECT bidder_id FROM bid
);
```

The inner SELECT finds IDs; the outer SELECT displays records whose ID appears in that list.

### 8. Show bidder emails in lowercase

```sql
SELECT name, LOWER(email) AS email
FROM bidder;
```

A built-in function formats or transforms the displayed result without changing stored data.


## Ashutosh — Experts & appraisals

### 1. Create a demonstration record

```sql
INSERT INTO art_expert (expert_id, name)
VALUES (:record_id, :value);
```

Add one new record.

### 2. Update that record

```sql
UPDATE art_expert
SET name = :value
WHERE expert_id = :record_id;
```

Change only that record’s title or name.

### 3. Delete that demonstration record

```sql
DELETE FROM art_expert
WHERE expert_id = :record_id;
```

Remove only that unreferenced demonstration record.

### 4. Search experts by name

```sql
SELECT expert_id, name, specialization
FROM art_expert
WHERE name LIKE :search;
```

LIKE finds names or titles matching the search value.

### 5. Show appraisals with expert names

```sql
SELECT e.name, p.estimated_value / 100 AS value_inr
FROM art_expert e
JOIN appraisal p ON e.expert_id = p.expert_id;
```

JOIN combines two tables using their matching ID columns.

### 6. Count appraisals for each expert

```sql
SELECT expert_id, COUNT(*) AS total_appraisals
FROM appraisal
GROUP BY expert_id;
```

GROUP BY creates one group per parent ID; COUNT(*) counts the rows in that group.

### 7. Find experts who performed an appraisal

```sql
SELECT name
FROM art_expert
WHERE expert_id IN (
    SELECT expert_id FROM appraisal
);
```

The inner SELECT finds IDs; the outer SELECT displays records whose ID appears in that list.

### 8. Show expert names in capital letters

```sql
SELECT UPPER(name) AS expert_name
FROM art_expert;
```

A built-in function formats or transforms the displayed result without changing stored data.
