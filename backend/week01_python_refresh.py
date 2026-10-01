students = [
{"id": "22000001", "name": "Nguyen Minh Anh", "major": "KHDL"},
{"id": "22000002", "name": "Tran Duc Long", "major": "KHDL"},
]
courses = [
{
"code": "INT2204",
"name": "Co so du lieu Web va he thong thong tin",
"capacity": 3,
"enrolled": 2,
},
{
"code": "INT2205",
"name": "Khai pha du lieu",
"capacity": 2,
"enrolled": 2,
},
]
enrollments = [
{"student_id": "22000001", "course_code": "INT2204"}]
for course in courses:
    remaining = course["capacity"] - course["enrolled"]
    print(course["code"], "- con", remaining, "cho")

def find_course(course_code):
    for course in courses:
        if course["code"] == course_code:
            return course
    return None

print(find_course("INT2204"))

def can_enroll(student_id, course_code):
    course = find_course(course_code)
    if course is None:
        return False, "Hoc phan khong ton tai"
    if course["enrolled"] >= course["capacity"]:
        return False, "Lop da du so luong"
    duplicated = any(
        item["student_id"] == student_id and item["course_code"] == course_code
        for item in enrollments
    )
    if duplicated:
        return False, "Sinh vien da dang ky hoc phan nay"
    return True, "Co the dang ky"
print(can_enroll("22000002", "INT2204"))
try:
    limit = int(input("Nhap so luong hoc phan muon hien thi: "))
    print(courses[:limit])
except ValueError:
    print("So luong phai la so nguyen")
    
    
    
def search_courses(keyword):
    normalized = keyword.strip().lower()
    
    results = []
    for course in courses:
        code = course["code"].lower()
        name = course["name"].lower()
        if normalized in code or normalized in name:
            results.append(course)
    return results
print(search_courses("web"))
def enroll_student(student_id, course_code):
    # 1. Kiểm tra sinh viên có tồn tại hay không
    student_exists = any(s["id"] == student_id for s in students)
    if not student_exists:
        return False, "Sinh vien khong ton tai"
    
    # 2. Sử dụng lại hàm can_enroll để kiểm tra học phần, sĩ số và trùng lặp
    ok, message = can_enroll(student_id, course_code)
    if not ok:
        return False, message
    
    # 3. Nếu thỏa mãn tất cả điều kiện, tiến hành đăng ký
    enrollments.append({"student_id": student_id, "course_code": course_code})
    
    # Tăng số lượng đã đăng ký (enrolled) của học phần lên 1
    course = find_course(course_code)
    course["enrolled"] += 1
    
    return True, "Dang ky thanh cong"

# --- Ví dụ sử dụng ---
print(enroll_student("22000002", "INT2204")) # Thành công
print(enroll_student("22000002", "INT2204")) # Thất bại (vì đã đăng ký rồi)
print(enroll_student("99999999", "INT2204")) # Thất bại (sinh viên không tồn tại)



# Tình huống 1: Đăng ký thành công
# (Sinh viên "22000002" chưa đăng ký INT2204, lớp INT2204 capacity=3, enrolled=2 còn 1 chỗ)
print("1. Đăng ký thành công:")
print(enroll_student("22000002", "INT2204"))

# Tình huống 2: Đăng ký trùng
# (Sinh viên "22000001" đã đăng ký INT2204 từ trước trong danh sách enrollments)
print("\n2. Đăng ký trùng:")
print(enroll_student("22000001", "INT2204"))

# Tình huống 3: Lớp đầy
# (Học phần INT2205 có capacity=2 và enrolled=2, đã hết chỗ)
print("\n3. Lớp đầy:")
print(enroll_student("22000001", "INT2205"))

# Tình huống 4: Mã học phần không tồn tại
print("\n4. Mã học phần không tồn tại:")
print(enroll_student("22000001", "INT9999"))

# Tình huống 5: Mã sinh viên không tồn tại
print("\n5. Mã sinh viên không tồn tại:")
print(enroll_student("99999999", "INT2204"))