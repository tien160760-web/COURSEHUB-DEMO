from __future__ import annotations
from .schemas import EnrollmentCreate, SectionCapacityUpdate

import logging

from fastapi import FastAPI, HTTPException, Query, Response, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .database import engine
from .schemas import EnrollmentCreate
from typing import Literal
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CourseHub API",
    version="0.4.0",
    description="API thuc hanh Buoi 5 - Quan ly dang ky hoc phan",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "CourseHub API dang hoat dong"}


# Kiểm tra các API có kết nối với dữ liệu không
@app.get("/health")
def health_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.exception("Khong ket noi duoc co so du lieu")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Khong ket noi duoc co so du lieu",
        ) from exc
    return {"status": "ok", "database": "connected"}


# API này dùng để liệt kê danh sách các khóa học. Nó hỗ trợ tìm kiếm theo từ khóa (q) trong mã khóa học hoặc tên khóa học.
# Nếu không có từ khóa nào được cung cấp, nó sẽ trả về tất cả các khóa học. Kết quả được sắp xếp theo mã khóa học.
@app.get("/courses")
def list_courses(
    q: str | None = Query(default=None, min_length=1),
) -> list[dict[str, object]]:
    sql = """
        SELECT code, name, credits
        FROM courses
    """
    parameters: dict[str, object] = {}

    if q is not None:
        keyword = q.strip().lower()
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tu khoa tim kiem khong duoc rong",
            )
        sql += """
            WHERE LOWER(code) LIKE :keyword
                OR LOWER(name) LIKE :keyword
        """
        parameters["keyword"] = f"%{keyword}%"
    sql += " ORDER BY code"

    with engine.connect() as connection:
        rows = connection.execute(text(sql), parameters).mappings().all()

    return [dict(row) for row in rows]


# Lấy thông tin của một khóa học dựa trên mã khóa học.
# Nếu khóa học không tồn tại, trả về lỗi 404.
@app.get("/courses/{course_code}")
def get_course(course_code: str) -> dict[str, object]:
    sql = """
        SELECT code, name, credits
        FROM courses
        WHERE code = :course_code
    """
    with engine.connect() as connection:
        row = (
            connection.execute(
                text(sql),
                {"course_code": course_code.upper()},
            )
            .mappings()
            .first()
        )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay hoc phan",
        )
    return dict(row)


# Liệt kê các danh sách lớp học phần.
# Nếu tham số available_only được đặt là True,
# chỉ liệt kê các lớp học phần còn chỗ trống.
# Kết quả được sắp xếp theo mã lớp học phần.
@app.get("/sections")
def list_sections(
    available_only: bool = False,
) -> list[dict[str, object]]:
    sql = """
        SELECT class_id, course_code, capacity, enrolled, remaining
        FROM v_section_summary
    """
    if available_only:
        sql += " WHERE remaining > 0"

    sql += " ORDER BY class_id"

    with engine.connect() as connection:
        rows = connection.execute(text(sql)).mappings().all()
    return [dict(row) for row in rows]


# Liệt kê tất cả các lớp học phần mà một sinh viên đã đăng ký.
# Nếu sinh viên không tồn tại, trả về lỗi 404.
@app.get("/students/{student_id}/enrollments")
def list_student_enrollments(student_id: str) -> list[dict[str, object]]:
    student_sql = "SELECT id FROM students WHERE id = :student_id"
    enrollment_sql = """
        SELECT e.student_id,
                s.name AS student_name,
                cs.id AS class_section_id,
                c.code AS course_code,
                c.name AS course_name,
                e.registered_at
        FROM enrollments AS e
        JOIN students AS s ON s.id = e.student_id
        JOIN class_sections AS cs ON cs.id = e.class_section_id
        JOIN courses AS c ON c.code = cs.course_code
        WHERE e.student_id = :student_id
        ORDER BY cs.id
    """

    with engine.connect() as connection:
        student = connection.execute(
            text(student_sql),
            {"student_id": student_id},
        ).first()
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay sinh vien",
            )
        rows = (
            connection.execute(
                text(enrollment_sql),
                {"student_id": student_id},
            )
            .mappings()
            .all()
        )
    return [dict(row) for row in rows]


# Đăng ký một sinh viên vào một lớp học phần.
# Nếu sinh viên hoặc lớp học phần không tồn tại,
# hoặc nếu sinh viên đã đăng ký lớp học phần đó,
# hoặc nếu lớp học phần đã đầy, trả về lỗi 409.
@app.post(
    "/enrollments",
    status_code=status.HTTP_201_CREATED,
)
def create_enrollment(payload: EnrollmentCreate) -> dict[str, str]:
    student_sql = "SELECT id FROM students WHERE id = :student_id"
    lock_section_sql = """
        SELECT id, capacity
        FROM class_sections
        WHERE id = :class_section_id
        FOR UPDATE
    """
    duplicate_sql = """
        SELECT 1
        FROM enrollments
        WHERE student_id = :student_id
          AND class_section_id = :class_section_id
    """
    count_sql = """
        SELECT COUNT(*)
        FROM enrollments
        WHERE class_section_id = :class_section_id
    """
    insert_sql = """
        INSERT INTO enrollments (student_id, class_section_id)
        VALUES (:student_id, :class_section_id)
    """
    event_sql = """
        INSERT INTO enrollment_events
            (student_id, class_section_id, event_type, source, dataset)
        VALUES
            (:student_id, :class_section_id, 'CREATED', 'api', 'demo')
    """
    parameters = {
        "student_id": payload.student_id,
        "class_section_id": payload.class_section_id,
    }
    try:
        with engine.begin() as connection:
            student = connection.execute(
                text(student_sql),
                {"student_id": payload.student_id},
            ).first()
            if student is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Khong tim thay sinh vien",
                )

            section = (
                connection.execute(
                    text(lock_section_sql),
                    {"class_section_id": payload.class_section_id},
                )
                .mappings()
                .first()
            )
            if section is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Khong tim thay lop hoc phan",
                )
            duplicated = connection.execute(text(duplicate_sql), parameters).first()
            if duplicated is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Sinh vien da dang ky lop nay",
                )

            enrolled = connection.execute(
                text(count_sql),
                {"class_section_id": payload.class_section_id},
            ).scalar_one()
            if int(enrolled) >= int(section["capacity"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Lop hoc phan da het cho",
                )

            connection.execute(text(insert_sql), parameters)
            connection.execute(text(event_sql), parameters)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dang ky xung dot voi du lieu hien tai",
        ) from exc

    return {
        "message": "Dang ky thanh cong",
        "student_id": payload.student_id,
        "class_section_id": payload.class_section_id,
    }
    # Hủy đăng ký một sinh viên khỏi một lớp học phần.
    # Nếu sinh viên hoặc lớp học phần không tồn tại,
    # hoặc nếu sinh viên chưa đăng ký lớp học phần đó, trả về lỗi 404.


@app.delete(
    "/enrollments/{student_id}/{class_section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_enrollment(student_id: str, class_section_id: str) -> Response:
    lock_section_sql = """
        SELECT id
        FROM class_sections
        WHERE id = :class_section_id
        FOR UPDATE
    """
    delete_sql = """
        DELETE FROM enrollments
        WHERE student_id = :student_id
          AND class_section_id = :class_section_id
        RETURNING student_id
    """
    event_sql = """
        INSERT INTO enrollment_events
            (student_id, class_section_id, event_type, source, dataset)
        VALUES
            (:student_id, :class_section_id, 'CANCELLED', 'api', 'demo')
    """
    parameters = {
        "student_id": student_id,
        "class_section_id": class_section_id,
    }

    with engine.begin() as connection:
        section = connection.execute(
            text(lock_section_sql),
            {"class_section_id": class_section_id},
        ).first()
        if section is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay lop hoc phan",
            )

        deleted = connection.execute(text(delete_sql), parameters).first()
        if deleted is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay dang ky can huy",
            )

        connection.execute(text(event_sql), parameters)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/lecturers")
def list_lecturers() -> list[dict[str, object]]:
    sql = """
        SELECT id, name
        FROM lecturers
        ORDER BY id
    """
    with engine.connect() as connection:
        rows = connection.execute(text(sql)).mappings().all()
    return [dict(row) for row in rows]


# chi tiết một lớp học phần
@app.get("/sections/{section_id}")
def get_section_detail(section_id: str) -> dict[str, object]:
    sql = """
        SELECT v.class_id,
               v.course_code,
               c.name AS course_name,
               cs.semester_code,
               sm.name AS semester_name,
               cs.lecturer_id,
               l.name AS lecturer_name,
               v.capacity,
               v.enrolled,
               v.remaining
        FROM v_section_summary AS v
        JOIN class_sections AS cs ON cs.id = v.class_id
        JOIN courses AS c ON c.code = cs.course_code
        JOIN semesters AS sm ON sm.code = cs.semester_code
        JOIN lecturers AS l ON l.id = cs.lecturer_id
        WHERE v.class_id = :section_id
    """
    with engine.connect() as connection:
        row = (
            connection.execute(
                text(sql),
                {"section_id": section_id.upper()},
            )
            .mappings()
            .first()
        )

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay lop hoc phan",
        )
    return dict(row)


@app.get("/enrollment-events")
def list_enrollment_events(
    student_id: str | None = Query(
        default=None,
        min_length=8,
        max_length=8,
    ),
    event_type: Literal["CREATED", "CANCELLED"] | None = Query(
        default=None,
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[dict[str, object]]:
    sql = """
        SELECT id, student_id, class_section_id,
               event_type, source, dataset, occurred_at
        FROM enrollment_events
        WHERE 1 = 1
    """

    parameters: dict[str, object] = {
        "skip": skip,
        "limit": limit,
    }

    if student_id is not None:
        sql += """
            AND student_id = :student_id
        """
        parameters["student_id"] = student_id

    if event_type is not None:
        sql += """
            AND event_type = :event_type
        """
        parameters["event_type"] = event_type

    sql += """
        ORDER BY occurred_at DESC, id DESC
        LIMIT :limit OFFSET :skip
    """

    with engine.connect() as connection:
        rows = (
            connection.execute(
                text(sql),
                parameters,
            )
            .mappings()
            .all()
        )

    return [dict(row) for row in rows]
