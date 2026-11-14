-- BUOC 1: Xem ket qua truy van thong ke.
SELECT COUNT(*) AS total_events
FROM enrollment_events
WHERE dataset = 'performance'
  AND class_section_id = 'PY-01'
  AND event_type = 'CREATED'
  AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
  AND occurred_at < TIMESTAMP '2026-01-01 00:00:00';


-- BUOC 2: Do truoc khi tao index moi.
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) AS total_events
FROM enrollment_events
WHERE dataset = 'performance'
  AND class_section_id = 'PY-01'
  AND event_type = 'CREATED'
  AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
  AND occurred_at < TIMESTAMP '2026-01-01 00:00:00';


-- BUOC 3: Tao index phu hop voi truy van.
CREATE INDEX idx_enrollment_events_dataset_section_type_time
ON enrollment_events
    (dataset, class_section_id, event_type, occurred_at);

ANALYZE enrollment_events;


-- BUOC 4: Do lai dung truy van sau khi tao index.
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) AS total_events
FROM enrollment_events
WHERE dataset = 'performance'
  AND class_section_id = 'PY-01'
  AND event_type = 'CREATED'
  AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
  AND occurred_at < TIMESTAMP '2026-01-01 00:00:00';


-- BUOC 5: Kiem tra lai ket qua sau khi tao index.
SELECT COUNT(*) AS total_events
FROM enrollment_events
WHERE dataset = 'performance'
  AND class_section_id = 'PY-01'
  AND event_type = 'CREATED'
  AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
  AND occurred_at < TIMESTAMP '2026-01-01 00:00:00';