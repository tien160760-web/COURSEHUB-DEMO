# Ghi chú thực hành Buổi 5

## Cách chạy

Backend — tại thư mục gốc:
python -m uvicorn backend.app.main:app --reload

Frontend — tại thư mục frontend:
npm install
npm run dev

## Kết quả kiểm tra

- Tải danh sách lớp từ API: Đạt — hiển thị dữ liệu từ Backend.
- Đăng ký WEB-01, POST 201: Đạt — đăng ký thành công, danh sách được cập nhật.
- Hủy WEB-01, DELETE 204: Đạt — đăng ký được xóa, số chỗ được cập nhật.
- Đối chiếu enrollments và enrollment_events: Đạt — bản ghi và sự kiện CREATED/CANCELLED đúng với thao tác.
- Mã sinh viên dưới 8 chữ số: Đạt — hiển thị lỗi trước khi đổi sinh viên.
- Sinh viên 99999999, HTTP 404: Đạt — hiển thị lỗi, không cho thao tác trên dữ liệu cũ.
- Tắt Backend rồi khôi phục: Đạt — báo lỗi kết nối và tải lại được khi Backend chạy lại.
- Hai cửa sổ thử RACE-01, HTTP 409: Đạt — cửa sổ thứ hai bị từ chối, không vượt sức chứa.
- Giao diện ở chiều rộng 390 px: Đạt — bố cục một cột, bảng cuộn ngang riêng.
- npm run build: Đạt — biên dịch thành công và tạo thư mục dist.
- Chạy thử npm run preview: Đạt — bản build hiển thị và tải dữ liệu được.
- npm test: Đạt — 8 test thành công, 0 lỗi.