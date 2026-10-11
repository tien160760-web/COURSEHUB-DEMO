-- CHI DUNG CHO DATABASE DEMO COURSEHUB CA NHAN.
-- Lenh nay xoa view va 6 bang cung toan bo du lieu trong cac bang.
-- Xac nhan current_database() truoc khi chay; khong dung tren du lieu can giu.

BEGIN;
DROP VIEW IF EXISTS v_section_summary;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS class_sections;
DROP TABLE IF EXISTS lecturers;
DROP TABLE IF EXISTS semesters;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;
COMMIT;