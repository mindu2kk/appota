# Appota Context-Aware Knowledge MVP

MVP cho Mission 2: cùng một câu hỏi, hệ thống dùng bối cảnh tổ chức và quyền của
người hỏi để chọn đúng tài liệu đang có hiệu lực, trả lời kèm nguồn, hoặc từ chối
khi không đủ căn cứ.

Repository chính thức: <https://github.com/mindu2kk/appota>

Bản chạy online: đang triển khai trên Render.

## Giả thuyết được kiểm chứng

> Nếu lọc quyền **trước khi truy xuất**, sau đó xếp hạng theo hiệu lực và độ gần
> của phạm vi tổ chức, mỗi nhân sự sẽ nhận được câu trả lời phù hợp mà không làm
> lộ tri thức ngoài quyền.

MVP cố ý dùng bộ máy truy xuất deterministic thay vì LLM. Điều này giúp kiểm thử
quyền, phiên bản, xung đột và từ chối một cách lặp lại được trong 3 ngày.

## Ba câu hỏi bắt buộc

### 1. Phần quan trọng nhất được hiện thực hóa là gì?

Tôi chọn hiện thực hóa **policy-aware retrieval**: nhận câu hỏi cùng danh tính
người dùng, lọc tài liệu theo quyền và phạm vi tổ chức trước khi truy xuất, xử lý
hiệu lực/phiên bản/xung đột, rồi trả lời kèm nguồn hoặc từ chối.

Đây là giả thuyết rủi ro nhất của bài toán. Một chatbot có thể tìm được đoạn văn
liên quan nhưng vẫn thất bại nếu lấy chính sách của sai công ty hoặc làm lộ tài
liệu người hỏi không được xem. MVP chứng minh phần này hoạt động bằng tình huống
cùng câu hỏi nghỉ phép: An thuộc AppotaPay nhận chính sách AppotaPay v2.0, còn
Bình thuộc Appota Ads nhận chính sách Appota Ads v3.0. Automated tests đồng thời
chứng minh bản hết hiệu lực bị loại và tài liệu HR không lộ cho nhân viên thường.

Nếu vòng quyết định này hoạt động, hướng giải quyết là khả thi vì semantic search
hay LLM có thể được thay vào tầng retrieval/synthesis sau này mà không thay đổi
ranh giới authorization, version resolution và evidence contract đã kiểm thử.

### 2. Những quyết định đã thay đổi so với Mission 1

Ở thiết kế đầy đủ của Mission 1, hướng giải pháp gồm ingestion nhiều loại tài
liệu, semantic/hybrid search, LLM synthesis, quản trị tri thức và audit. Khi triển
khai Mission 2, tôi thu hẹp và thay đổi ba quyết định:

1. **Không dùng LLM trong core loop.** Tôi dùng answer template và dữ liệu có cấu
   trúc để hành vi về quyền, phiên bản và từ chối deterministic, dễ kiểm chứng.
2. **Không xây ingestion/vector database.** Dữ liệu JSON giả lập đủ để chứng minh
   ranh giới tổ chức và ACL; thời gian được dành cho các case rủi ro thay vì hạ
   tầng chưa phục vụ giả thuyết chính.
3. **Conflict chuyển từ ưu tiên ngầm sang fail-closed.** Khi hai tài liệu cùng
   scope và version mâu thuẫn, hệ thống hiển thị hai căn cứ nhưng không kết luận.

Nguyên nhân thay đổi là khi tạo test cases, tôi nhận ra một câu trả lời trôi chảy
không phải bằng chứng hệ thống dùng đúng tri thức. Khả năng giải thích quyết định,
từ chối an toàn và test lặp lại được có giá trị hơn số lượng tính năng trong MVP.

### 3. Trường hợp dễ dùng sai tri thức nhất và cách kiểm soát

Rủi ro lớn nhất hiện nay là **metadata tài liệu sai hoặc thiếu** — ví dụ tài liệu
Appota Ads bị gắn nhầm scope AppotaPay, ACL quá rộng, hoặc bản cũ không có ngày
hết hiệu lực. Vì engine tin metadata để ra quyết định, lỗi này có thể khiến hệ
thống chọn nhầm chính sách dù thuật toán hoạt động đúng.

MVP kiểm soát rủi ro theo các lớp:

- deny-by-default: role/scope không khớp thì tài liệu bị loại trước khi chấm điểm;
- chỉ xét tài liệu đang hiệu lực, sau đó ưu tiên scope cụ thể và version mới nhất;
- nếu còn hai nguồn ngang mức nhưng khác nội dung thì từ chối kết luận;
- citation và decision trace giúp người dùng kiểm tra nguồn đã được sử dụng;
- test riêng cho cross-context, bản hết hạn, ACL, thiếu dữ liệu và conflict.

Rủi ro chưa giải quyết tốt là câu hỏi diễn đạt khác keyword: hệ thống có thể bỏ
sót tài liệu và từ chối dù dữ liệu tồn tại. Đây là fail-safe hơn trả lời sai, nhưng
cần hybrid/semantic retrieval, bộ test paraphrase và Recall@k để cải thiện.

## Chạy sản phẩm

Yêu cầu: Python 3.11+; không cần cài package.

```powershell
python app.py
```

Mở <http://127.0.0.1:8000>. Dừng bằng `Ctrl+C`.

Chạy kiểm thử:

```powershell
python -m unittest discover -s tests -v
```

Kết quả tham chiếu ngày 14/10/2026: `8 tests`, tất cả `OK`.

## Core loop

```text
Câu hỏi + user_id
  -> nạp ngữ cảnh (công ty, phòng ban, vai trò)
  -> lọc tài liệu theo quyền và phạm vi áp dụng
  -> bỏ bản hết hiệu lực / ưu tiên bản mới nhất
  -> phát hiện xung đột
  -> truy xuất theo ý định
  -> trả lời có citation hoặc từ chối an toàn
```

Quy tắc an toàn quan trọng: tài liệu không được phép không đi vào bước chấm điểm,
không xuất hiện trong câu trả lời, nguồn hay trace trả về client.

## Dữ liệu giả lập

- Tập đoàn Appota Group.
- Công ty AppotaPay và Appota Ads.
- Phòng Engineering, Sales, HR và Finance.
- Tài liệu cấp tập đoàn, công ty, phòng ban; có bản cũ/hết hiệu lực, tài liệu hạn
  chế theo vai trò và một cặp tài liệu đang mâu thuẫn.

Ba persona demo:

- An — AppotaPay / Engineering / Employee.
- Bình — Appota Ads / Sales / Manager.
- Chi — Appota Group / HR / HR Admin.

## Cấu trúc

- `app.py`: HTTP server và API.
- `knowledge_engine.py`: authorization, version resolution, conflict detection,
  retrieval và answer composition.
- `data/users.json`, `data/documents.json`: dữ liệu giả lập.
- `web/`: giao diện demo.
- `tests/`: kiểm thử core loop.
- `TEST_REPORT.md`: kết quả theo format đề bài.

## Giới hạn đã biết

- Truy xuất dựa trên intent/keyword, chưa hiểu tốt câu hỏi dài hoặc diễn đạt lạ.
- Identity đang được chọn từ giao diện demo; production phải lấy từ SSO/JWT đã
  xác thực, không tin `user_id` do client tự khai.
- Chưa có vector search, OCR, ingestion pipeline, audit store hoặc admin console.
- Câu trả lời là template trích từ tài liệu, chưa có LLM synthesis.
- Chính sách xung đột hiện từ chối toàn bộ thay vì chuyển ticket cho chủ tài liệu.

## Hướng production

Thay persona demo bằng SSO; lưu ACL và organization tree trong database; dùng
hybrid search trên tập tài liệu đã pre-filter; kiểm tra citation/entailment sau
synthesis; lưu audit event; thêm workflow phê duyệt, owner và SLA xử lý xung đột.

## Hồ sơ nộp bài

- Bộ test và kết quả chi tiết: [`TEST_REPORT.md`](TEST_REPORT.md).
- Kịch bản video tối đa 5 phút: [`VIDEO_SCRIPT.md`](VIDEO_SCRIPT.md).
- Checklist xuất bản: [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md).

Repository public chứa mã nguồn và hướng dẫn chạy local. MVP hiện chưa có link
deploy online; sản phẩm không cần API key và không chứa dữ liệu nội bộ Appota.
