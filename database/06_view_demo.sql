
-- Buoc 1: bat dau giao dich.
BEGIN;

-- Buoc 2: them dang ky thu cua Hoang Nam vao WEB-01.
INSERT INTO enrollments (student_id, class_section_id)
VALUES ('22000004', 'WEB-01');

-- Buoc 3: xem view trong giao dich (WEB-01 co 3 dang ky, con 0 cho).
SELECT class_id, capacity, enrolled, remaining
FROM v_section_summary
WHERE class_id = 'WEB-01';

-- Buoc 4: hoan tac dang ky thu.
ROLLBACK;

-- Buoc 5: chay lai de xac nhan WEB-01 tro ve 2 dang ky, con 1 cho.
SELECT class_id, capacity, enrolled, remaining
FROM v_section_summary
WHERE class_id = 'WEB-01';