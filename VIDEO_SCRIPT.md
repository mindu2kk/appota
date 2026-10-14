# Kịch bản video Mission 2 — tối đa 5 phút

Mục tiêu thời lượng: khoảng 4 phút 30 giây. Không cần đọc từng dòng; dùng nội dung
dưới đây làm talking points và thao tác trực tiếp trên màn hình.

## 0:00–0:35 — Bài toán

“Appota có tri thức ở nhiều cấp: Tập đoàn, Công ty, Phòng ban và Nhóm. Tìm được
tài liệu liên quan là chưa đủ; câu trả lời còn phải đúng đơn vị, đúng quyền và
đúng phiên bản. Vì vậy câu hỏi tôi chọn kiểm chứng là: hệ thống có thể dùng bối
cảnh người hỏi để chọn đúng tri thức mà không làm lộ tài liệu khác quyền không?”

Trên màn hình: mở trang chủ, chỉ vào persona và năm guardrails.

## 0:35–1:15 — Phần được chọn để chứng minh

“Tôi hiện thực hóa policy-aware retrieval. Luồng xử lý là: câu hỏi và user ID →
nạp company, department, role → lọc quyền trước truy xuất → kiểm tra hiệu lực →
ưu tiên scope gần nhất và version mới nhất → phát hiện conflict → trả lời kèm
nguồn hoặc từ chối. Tôi cố ý chưa dùng LLM để core decision deterministic và có
thể kiểm thử lặp lại.”

Trên màn hình: mở sơ đồ core loop trong README hoặc lướt nhanh source engine.

## 1:15–2:20 — Demo case bắt buộc

1. Chọn **Nguyễn Minh An — AppotaPay / Engineering / employee**.
2. Hỏi: “Quy định nghỉ phép của tôi như thế nào?”
3. Chỉ ra kết quả 14 ngày, nguồn AppotaPay v2.0 và ngày hiệu lực.
4. Chuyển sang **Trần Đức Bình — Appota Ads / Sales / manager**.
5. Hỏi lại đúng câu trên.
6. Chỉ ra kết quả 12 ngày + 2 wellbeing, nguồn Appota Ads v3.0.

Lời dẫn: “Câu hỏi không đổi, chỉ bối cảnh người hỏi thay đổi. Hai kết quả khác
nhau và đều có nguồn kiểm chứng.”

## 2:20–3:15 — Quyền truy cập và tình huống khó

1. Với An, hỏi: “Quy trình chốt bảng lương thế nào?”
2. Hệ thống từ chối do không có evidence được phép; không tiết lộ tên hay ID tài
   liệu HR.
3. Chọn Chi — HR Admin và hỏi lại để thấy tài liệu hợp lệ được trả về.
4. Hỏi: “Mức công tác phí là bao nhiêu?”
5. Chỉ ra hai tài liệu v2.0 cùng hiệu lực nhưng định mức khác nhau.

Lời dẫn: “Hệ thống không chọn ngẫu nhiên hoặc để model đoán. Nó fail-closed và
đưa hai nguồn để chủ sở hữu chính sách xử lý.”

## 3:15–3:50 — Bộ kiểm thử

Chạy:

```powershell
python -m unittest discover -s tests -v
```

“Có 8 automated tests: khác biệt theo context, version hết hạn, policy cấp phòng,
ACL không rò rỉ, quyền HR, conflict, thiếu dữ liệu và identity không xác định.
Báo cáo test ghi rõ kỳ vọng, thực tế, đạt/chưa đạt và điều học được.”

## 3:50–4:30 — Hạn chế và kết luận

“Giới hạn lớn nhất là retrieval theo intent/keyword: cách diễn đạt lạ có thể bị
bỏ sót. Metadata sai cũng có thể dẫn tới dùng sai chính sách. Hiện tại hệ thống
giảm rủi ro bằng deny-by-default, citation, conflict refusal và test. Bước tiếp
theo là SSO, metadata approval, hybrid search, Recall@k và audit log.

MVP chưa phải chatbot hoàn chỉnh, nhưng đã chứng minh giả thuyết quan trọng nhất:
cùng một kho tri thức, mỗi nhân sự nhận thông tin phù hợp với bối cảnh và quyền.”
