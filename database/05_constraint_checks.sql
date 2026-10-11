
-- Đăng ký trùng lớp 
INSERT INTO enrollments (student_id, class_section_id)
VALUES ('22000001', 'WEB-01');

-- Đăng ký sinh viên không tồn tại
INSERT INTO enrollments (student_id, class_section_id)
VALUES ('22999999', 'WEB-01');

-- Đổi sức chưa thành 0
UPDATE class_sections
SET capacity = 0
WHERE id = 'WEB-01';

-- Bỏ trống số tín chỉ
UPDATE courses
SET credits = NULL
WHERE code = 'INT2204';

-- Dùng email của sinh viên khác
UPDATE students
SET email = 'anh@example.com'
WHERE id = '22000002';

-- Nhập họ tên chỉ cần dấu cách 
UPDATE students
SET name = ' '
WHERE id = '22000004';