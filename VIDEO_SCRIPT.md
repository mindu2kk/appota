# Kịch bản thuyết trình Mission 2 — Knowledge Guard

Thời lượng mục tiêu: **4 phút 30 giây**

Link demo: <https://mindu2kk.github.io/appota/>

Link source: <https://github.com/mindu2kk/appota>

## Chuẩn bị trước khi quay

1. Mở sẵn demo online và đặt persona về Nguyễn Minh An.
2. Mở sẵn terminal tại thư mục dự án để chạy test.
3. Tăng zoom trình duyệt lên 110–125% và tắt thông báo trên máy.
4. Tập thử một lượt; không dành quá 70 giây cho mỗi màn demo.

## 0:00–0:35 — Bài toán

**Màn hình:** Trang đầu Knowledge Guard, chưa nhập câu hỏi.

**Lời nói:**

“Xin chào, đây là bài làm Mission 2 của tôi với tên gọi Knowledge Guard.

Bài toán tôi giải quyết là tri thức trong doanh nghiệp nằm ở nhiều cấp, từ Tập
đoàn, Công ty đến Phòng ban. Vì vậy tìm được tài liệu liên quan là chưa đủ. Hệ
thống còn phải biết ai đang hỏi, họ thuộc đơn vị nào, có quyền xem gì và tài liệu
nào đang có hiệu lực.

Mục tiêu của tôi là chứng minh một vòng lặp nhỏ nhưng quan trọng: câu hỏi cùng bối
cảnh người dùng sẽ dẫn tới đúng tri thức, đúng phạm vi và câu trả lời có nguồn.”

## 0:35–1:10 — Phần quan trọng nhất được chọn

**Màn hình:** Chỉ vào persona và danh sách Guardrail.

**Lời nói:**

“Phần tôi chọn hiện thực hóa là policy-aware retrieval, tức truy xuất có nhận
biết quyền và bối cảnh.

Luồng xử lý gồm: nhận câu hỏi và danh tính người dùng; nạp company, department và
role; lọc quyền trước khi truy xuất; loại tài liệu hết hiệu lực; ưu tiên phạm vi
gần người hỏi và phiên bản mới nhất; cuối cùng trả lời có nguồn hoặc từ chối.

Tôi cố ý chưa đưa LLM vào core loop. Với MVP này, điều quan trọng hơn câu trả lời
trôi chảy là quyết định phải deterministic, giải thích được và kiểm thử được.”

## 1:10–2:15 — Demo bắt buộc: cùng câu hỏi, khác bối cảnh

**Màn hình và thao tác:**

1. Chọn **Nguyễn Minh An — AppotaPay / Engineering / employee**.
2. Bấm “Nghỉ phép”, sau đó bấm “Tra cứu”.

**Lời nói:**

“Đầu tiên, Nguyễn Minh An thuộc AppotaPay hỏi: Quy định nghỉ phép của tôi như thế
nào? Hệ thống trả lời 14 ngày phép và yêu cầu đăng ký trước hai ngày. Căn cứ là
chính sách AppotaPay phiên bản 2.0, có hiệu lực từ ngày 1 tháng 1 năm 2026.”

3. Chuyển persona sang **Trần Đức Bình — Appota Ads / Sales / manager**.
4. Hỏi lại đúng câu trên.

**Lời nói:**

“Tôi giữ nguyên câu hỏi nhưng đổi người hỏi sang Trần Đức Bình thuộc Appota Ads.
Kết quả bây giờ là 12 ngày phép và 2 ngày wellbeing, lấy từ chính sách Appota Ads
phiên bản 3.0.

Như vậy câu hỏi không đổi, nhưng bối cảnh khác đã tạo ra hai câu trả lời phù hợp
khác nhau. Cả hai đều hiển thị nguồn và ngày hiệu lực để người dùng kiểm chứng.”

## 2:15–3:10 — Quyền truy cập và tình huống khó

**Màn hình và thao tác:**

1. Chuyển lại Nguyễn Minh An.
2. Nhập: **“Quy trình chốt bảng lương thế nào?”**

**Lời nói:**

“Tình huống tiếp theo kiểm tra quyền truy cập. An là nhân viên thông thường nên
không có quyền xem quy trình chốt bảng lương của HR. Hệ thống trả về thiếu căn cứ
được phép, không tiết lộ tên, ID hay nội dung của tài liệu hạn chế.”

3. Bấm “Dữ liệu mâu thuẫn”, rồi “Tra cứu”.

**Lời nói:**

“Đây là tình huống khó. Có hai tài liệu công tác phí cùng phạm vi, cùng phiên bản
và cùng ngày hiệu lực, nhưng một bản ghi 900 nghìn và bản còn lại ghi 1 triệu 200
nghìn đồng.

Hệ thống không tự chọn một bản và cũng không đoán. Nó từ chối kết luận, hiển thị
hai nguồn mâu thuẫn để chủ sở hữu chính sách xử lý. Đây là nguyên tắc fail-closed
của MVP.”

## 3:10–3:45 — Bộ kiểm thử

**Màn hình:** Terminal tại thư mục dự án.

**Thao tác:**

```powershell
python -m unittest discover -s tests -v
```

**Lời nói trong khi test chạy:**

“MVP có 8 automated tests, nhiều hơn yêu cầu tối thiểu 5. Các test bao phủ: cùng
câu hỏi khác bối cảnh, phiên bản hết hạn, chính sách cấp phòng, tài liệu hạn chế
không bị lộ, quyền HR Admin, dữ liệu mâu thuẫn, thiếu tri thức và danh tính không
xác định. Kết quả hiện tại là 8 trên 8 test đạt.”

## 3:45–4:30 — Thay đổi, hạn chế và kết luận

**Màn hình:** Quay lại demo hoặc README.

**Lời nói:**

“So với thiết kế đầy đủ ở Mission 1, tôi đã thu hẹp ingestion, vector database và
LLM synthesis để tập trung vào rủi ro lớn nhất là dùng sai tri thức hoặc sai quyền.
Trong quá trình làm, tôi cũng đổi cách xử lý conflict từ ưu tiên ngầm sang từ chối
an toàn.

Hạn chế lớn nhất hiện tại là retrieval dựa trên intent và keyword. Cách diễn đạt
lạ có thể khiến hệ thống bỏ sót tài liệu và từ chối dù dữ liệu tồn tại. Ngoài ra,
nếu metadata về scope, ACL hoặc ngày hiệu lực bị gắn sai thì hệ thống vẫn có thể
dùng sai chính sách. Tôi kiểm soát bằng deny-by-default, citation, conflict
detection và các test regression.

MVP chưa phải sản phẩm production-ready, nhưng đã chứng minh giả thuyết quan trọng
nhất: mỗi nhân sự có thể nhận đúng thông tin theo đơn vị và quyền của mình, với
nguồn có thể kiểm chứng. Cảm ơn mọi người đã theo dõi.”

## Câu dự phòng khi demo online chậm

Nếu trang online không tải trong khoảng 5 giây, nói:

“Để không mất thời gian trình bày vì đường truyền, tôi chuyển sang bản local. Bản
này dùng cùng source code và cùng bộ dữ liệu với bản đã deploy.”

Sau đó chạy:

```powershell
python app.py
```

và mở <http://127.0.0.1:8000>.
