-- Ashutosh: Experts & appraisals
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
BEGIN :value := 'Demo Expert'; END;
/
INSERT INTO art_expert (expert_id, name)
VALUES (:record_id, :value);
COMMIT;
SELECT * FROM art_expert WHERE expert_id=:record_id;

-- 2. Update that record
BEGIN :value := 'Demo Expert revised'; END;
/
UPDATE art_expert
SET name = :value
WHERE expert_id = :record_id;
COMMIT;
SELECT * FROM art_expert WHERE expert_id=:record_id;

-- 3. Delete that demonstration record
DELETE FROM art_expert
WHERE expert_id = :record_id;
COMMIT;
SELECT * FROM art_expert WHERE expert_id=:record_id;

-- 4. Search experts by name
SELECT expert_id, name, specialization
FROM art_expert
WHERE name LIKE :search;

-- 5. Show appraisals with expert names
SELECT e.name, p.estimated_value / 100 AS value_inr
FROM art_expert e
JOIN appraisal p ON e.expert_id = p.expert_id;

-- 6. Count appraisals for each expert
SELECT expert_id, COUNT(*) AS total_appraisals
FROM appraisal
GROUP BY expert_id;

-- 7. Find experts who performed an appraisal
SELECT name
FROM art_expert
WHERE expert_id IN (
    SELECT expert_id FROM appraisal
);

-- 8. Show expert names in capital letters
SELECT UPPER(name) AS expert_name
FROM art_expert;
