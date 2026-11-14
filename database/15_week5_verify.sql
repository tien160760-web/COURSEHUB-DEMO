-- Kiem tra sinh vien dang ky 
SELECT class_id, capacity, enrolled, remaining
FROM v_section_summary
WHERE class_id = 'WEB-01';

-- Kiem tra nhat ky 
SELECT student_id, class_section_id
FROM enrollments
WHERE student_id = '22000004'
  AND class_section_id = 'WEB-01';

-- Kiem tra nhat ky sau khi huy dang ky
  SELECT id, student_id, class_section_id, event_type, occurred_at
FROM enrollment_events
WHERE dataset = 'demo'
  AND student_id = '22000004'
  AND class_section_id = 'WEB-01'
ORDER BY id DESC
LIMIT 10;