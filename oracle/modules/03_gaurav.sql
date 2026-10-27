-- Gaurav: Auctions & lots
-- Three DML operations and five short SELECT queries.
-- Connect as ATELIER_PROJECT; only the newly generated demo row is updated/deleted.
SET PAGESIZE 100
SET LINESIZE 200
SET FEEDBACK ON
VARIABLE record_id NUMBER
VARIABLE value VARCHAR2(200)
VARIABLE email VARCHAR2(200)
VARIABLE search VARCHAR2(200)
BEGIN
  SELECT lab_id_seq.NEXTVAL INTO :record_id FROM dual;
  :email := 'demo-' || TO_CHAR(:record_id) || '@atelier.example';
  :search := '%';
END;
/

-- 1. Create a demonstration record
BEGIN :value := 'Student Auction'; END;
/
INSERT INTO auction (auction_id, gallery_id, title, "DATE")
VALUES (:record_id, 1, :value, DATE '2026-12-15');
COMMIT;
SELECT * FROM auction WHERE auction_id=:record_id;

-- 2. Update that record
BEGIN :value := 'Student Auction revised'; END;
/
UPDATE auction
SET title = :value
WHERE auction_id = :record_id;
COMMIT;
SELECT * FROM auction WHERE auction_id=:record_id;

-- 3. Delete that demonstration record
DELETE FROM auction
WHERE auction_id = :record_id;
COMMIT;
SELECT * FROM auction WHERE auction_id=:record_id;

-- 4. Search auctions by title
SELECT auction_id, title, status
FROM auction
WHERE title LIKE :search;

-- 5. Show the lots in each auction
SELECT a.title, l.lot_number
FROM auction a
JOIN auction_lot l ON a.auction_id = l.auction_id;

-- 6. Count lots for each auction
SELECT auction_id, COUNT(*) AS total_lots
FROM auction_lot
GROUP BY auction_id;

-- 7. Find lots belonging to open auctions
SELECT lot_id, lot_number
FROM auction_lot
WHERE auction_id IN (
    SELECT auction_id FROM auction WHERE status = 'open'
);

-- 8. Show starting prices in rupees
SELECT lot_id, ROUND(starting_price / 100, 2) AS starting_price_inr
FROM auction_lot;
