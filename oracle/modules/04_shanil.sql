-- Shanil: Bidders & bids
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
BEGIN :value := 'Demo Bidder'; END;
/
INSERT INTO bidder (bidder_id, name, email)
VALUES (:record_id, :value, :email);
COMMIT;
SELECT * FROM bidder WHERE bidder_id=:record_id;

-- 2. Update that record
BEGIN :value := 'Demo Bidder revised'; END;
/
UPDATE bidder
SET name = :value
WHERE bidder_id = :record_id;
COMMIT;
SELECT * FROM bidder WHERE bidder_id=:record_id;

-- 3. Delete that demonstration record
DELETE FROM bidder
WHERE bidder_id = :record_id;
COMMIT;
SELECT * FROM bidder WHERE bidder_id=:record_id;

-- 4. Search bidders by name
SELECT bidder_id, name, email
FROM bidder
WHERE name LIKE :search;

-- 5. Show bids with bidder names
SELECT r.name, b.bid_amount / 100 AS amount_inr
FROM bidder r
JOIN bid b ON r.bidder_id = b.bidder_id;

-- 6. Count bids for each bidder
SELECT bidder_id, COUNT(*) AS total_bids
FROM bid
GROUP BY bidder_id;

-- 7. Find bidders who placed a bid
SELECT name
FROM bidder
WHERE bidder_id IN (
    SELECT bidder_id FROM bid
);

-- 8. Show bidder emails in lowercase
SELECT name, LOWER(email) AS email
FROM bidder;
