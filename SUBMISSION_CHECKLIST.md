# Checklist nộp Mission 2

## Repository

- [x] README mô tả giả thuyết, kiến trúc, cách chạy và giới hạn.
- [x] Dữ liệu hoàn toàn giả lập.
- [x] Không cần API key hoặc dịch vụ trả phí để chạy.
- [x] `.gitignore` loại cache và artifact tạm.
- [x] Có ít nhất 5 test cases; hiện có 8 automated tests.
- [x] Khởi tạo Git repository và commit phiên bản nộp.
- [x] Tạo GitHub repository ở chế độ Public.
- [x] Bổ sung URL GitHub vào README hoặc form nộp bài.

## Bản chạy thử

- [x] Có hướng dẫn chạy local bằng một lệnh: `python app.py`.
- [x] Không cần cài dependency ngoài Python 3.11+.
- [x] Đã smoke-test API và kiểm tra luồng thật trên trình duyệt.
- [x] Deploy online tại <https://mindu2kk.github.io/appota/>.

## Video tối đa 5 phút

- [x] Có kịch bản khoảng 4 phút 30 giây trong `VIDEO_SCRIPT.md`.
- [ ] Quay màn hình theo đúng thứ tự: bài toán → lựa chọn → demo khác context →
  ACL/conflict → tests → giới hạn.
- [ ] Kiểm tra video không hiển thị thông tin cá nhân, credential hoặc tab riêng.
- [ ] Upload và kiểm tra quyền xem link bằng cửa sổ ẩn danh.

## Kiểm tra cuối trước khi public

```powershell
python -m unittest discover -s tests -v
git status
git diff --check
```

Không commit file `.env`, token, cookie, credential, dữ liệu nội bộ hoặc artifact
trình duyệt trong `.playwright-cli/`.
