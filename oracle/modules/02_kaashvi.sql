-- Kaashvi: Galleries & exhibitions
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
BEGIN :value := 'Light and Memory'; END;
/
INSERT INTO exhibition
    (exhibition_id, gallery_id, curator_id, title, start_date, end_date)
VALUES (:record_id, 1, 1, :value, DATE '2026-11-01', DATE '2026-12-31');
COMMIT;
SELECT * FROM exhibition WHERE exhibition_id=:record_id;

-- 2. Update that record
BEGIN :value := 'Light and Memory revised'; END;
/
UPDATE exhibition
SET title = :value
WHERE exhibition_id = :record_id;
COMMIT;
SELECT * FROM exhibition WHERE exhibition_id=:record_id;

-- 3. Delete that demonstration record
DELETE FROM exhibition
WHERE exhibition_id = :record_id;
COMMIT;
SELECT * FROM exhibition WHERE exhibition_id=:record_id;

-- 4. Search exhibitions by title
SELECT exhibition_id, title, start_date, end_date
FROM exhibition
WHERE title LIKE :search;

-- 5. Show each exhibition and its gallery
SELECT e.title, g.name
FROM exhibition e
JOIN gallery g ON e.gallery_id = g.gallery_id;

-- 6. Count exhibitions for each gallery
SELECT gallery_id, COUNT(*) AS total_exhibitions
FROM exhibition
GROUP BY gallery_id;

-- 7. Find exhibitions in Mumbai galleries
SELECT title
FROM exhibition
WHERE gallery_id IN (
    SELECT gallery_id FROM gallery WHERE city = 'Mumbai'
);

-- 8. Format exhibition opening dates
SELECT title, TO_CHAR(start_date, 'DD-MM-YYYY') AS opening_date
FROM exhibition;
