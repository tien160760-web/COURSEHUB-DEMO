-- BUOC 1: Kiem tra trang thai ban dau.
SELECT
    (SELECT COUNT(*)
     FROM enrollments
     WHERE class_section_id = 'RACE-01') AS enrollment_count,
    (SELECT COUNT(*)
     FROM enrollment_events
     WHERE class_section_id = 'RACE-01'
       AND dataset = 'demo') AS event_count;


-- BUOC 2: Them dang ky trong transaction
BEGIN;

INSERT INTO enrollments (student_id, class_section_id)
VALUES ('22000004', 'RACE-01');
SELECT student_id, class_section_id
FROM enrollments
WHERE student_id = '22000004'
  AND class_section_id = 'RACE-01';


-- BUOC 3: Co y ghi lich su sai de gay loi.
INSERT INTO enrollment_events
    (student_id, class_section_id, event_type, source, dataset)
VALUES
    ('22000004', 'RACE-01', 'INVALID', 'rollback-test', 'demo');


-- BUOC 4: Chay rieng sau khi BUOC 3 bao loi.
ROLLBACK;


-- BUOC 5: Kiem tra trang thai sau rollback.
SELECT
    (SELECT COUNT(*)
     FROM enrollments
     WHERE class_section_id = 'RACE-01') AS enrollment_count,
    (SELECT COUNT(*)
     FROM enrollment_events
     WHERE class_section_id = 'RACE-01'
       AND dataset = 'demo') AS event_count;

SELECT student_id, class_section_id
FROM enrollments
WHERE student_id = '22000004'
  AND class_section_id = 'RACE-01';