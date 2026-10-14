# Báo cáo kiểm thử Mission 2

Ngày kiểm thử: 14/10/2026

Môi trường: local, Python 3.13, dữ liệu giả lập

Lệnh: `python -m unittest discover -s tests -v`

## Kết quả

| # | Tình huống | Kỳ vọng | Kết quả thực tế | Đánh giá | Điều học được |
|---|---|---|---|---|---|
| 1 | Cùng câu “Quy định nghỉ phép…”; An thuộc AppotaPay và Bình thuộc Appota Ads | Hai câu trả lời khác nhau, đúng công ty, có nguồn | An nhận 14 ngày từ PAY-LEAVE-002; Bình nhận 12 ngày + 2 wellbeing từ ADS-LEAVE-003 | Đạt | Context tổ chức phải tham gia trực tiếp vào retrieval, không chỉ đưa cho LLM ở cuối |
| 2 | An hỏi nghỉ phép khi tồn tại bản AppotaPay v1 đã hết hiệu lực và v2 đang hiệu lực | Chỉ dùng v2 | Nguồn trả về là v2.0; bản cũ không được chọn | Đạt | Lọc hiệu lực trước xếp hạng loại được lỗi dùng chính sách cũ |
| 3 | Nhân viên thường hỏi quy trình chốt bảng lương chỉ HR Admin được đọc | Từ chối, không lộ tiêu đề, ID hay nội dung tài liệu | Trả `INSUFFICIENT_EVIDENCE`, citations rỗng, response không chứa ID/nội dung hạn chế | Đạt | “Không tìm thấy trong tập được phép” an toàn hơn tiết lộ rằng tài liệu mật tồn tại |
| 4 | HR Admin hỏi cùng quy trình bảng lương | Trả lời được và có nguồn | Trả nội dung C&B-07, nguồn GRP-PAYROLL-ADMIN | Đạt | ACL theo vai trò tạo khác biệt hợp lệ cho cùng kho tri thức |
| 5 | Hai tài liệu công tác phí cùng scope, version và hiệu lực nhưng khác định mức | Không tự chọn một bản; báo mâu thuẫn và từ chối kết luận | Trả `CONFLICTING_EVIDENCE`, hiển thị hai nguồn để kiểm chứng | Đạt (tình huống khó) | Cần workflow owner giải quyết conflict thay vì để model “đoán” |
| 6 | Hỏi chính sách mua laptop không có trong kho | Từ chối do thiếu căn cứ | Trả `INSUFFICIENT_EVIDENCE`, không tạo câu trả lời | Đạt | Từ chối là hành vi đúng khi recall bằng 0 |
| 7 | Câu hỏi diễn đạt lạ, không chứa keyword/intent đã biết | Hệ thống hiểu được ý nghĩa | Bộ máy keyword có thể từ chối dù tài liệu liên quan tồn tại | Chưa đạt (thất bại đã biết) | Cần semantic/hybrid retrieval và bộ dữ liệu paraphrase để đo Recall@k |

## Tổng kết

- Automated: 8/8 test cases pass cho hành vi đã đặc tả.
- Chứng minh được core loop và tình huống bắt buộc “cùng câu hỏi, hai bối cảnh,
  hai kết quả”.
- Case #7 là giới hạn có chủ đích của MVP: test hiện tại ghi nhận trong báo cáo,
  chưa biến thành test phải-pass vì chưa có semantic retriever.
- Automated test chứng minh logic; demo trình duyệt vẫn cần người đánh giá thao tác
  để xác nhận trải nghiệm trình bày.
