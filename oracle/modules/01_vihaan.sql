-- Vihaan: Artists & collection
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
BEGIN :value := 'Study in Light'; END;
/
INSERT INTO artwork (artwork_id, artist_id, title)
VALUES (:record_id, 1, :value);
COMMIT;
SELECT * FROM artwork WHERE artwork_id=:record_id;

-- 2. Update that record
BEGIN :value := 'Study in Light revised'; END;
/
UPDATE artwork
SET title = :value
WHERE artwork_id = :record_id;
COMMIT;
SELECT * FROM artwork WHERE artwork_id=:record_id;

-- 3. Delete that demonstration record
DELETE FROM artwork
WHERE artwork_id = :record_id;
COMMIT;
SELECT * FROM artwork WHERE artwork_id=:record_id;

-- 4. Search artworks by title
SELECT artwork_id, title, medium
FROM artwork
WHERE title LIKE :search;

-- 5. Show each artwork and its artist
SELECT w.title, a.name
FROM artwork w
JOIN artist a ON w.artist_id = a.artist_id;

-- 6. Count artworks for each artist
SELECT artist_id, COUNT(*) AS total_artworks
FROM artwork
GROUP BY artist_id;

-- 7. Find artworks by Indian artists
SELECT title
FROM artwork
WHERE artist_id IN (
    SELECT artist_id FROM artist WHERE nationality = 'Indian'
);

-- 8. Show artwork titles in capital letters
SELECT UPPER(title) AS title_in_capitals
FROM artwork;
