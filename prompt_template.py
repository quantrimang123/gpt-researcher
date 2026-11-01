def get_hsg9_prompt(query, search_context):
    return f"""
Bạn là chuyên gia soạn đề và giảng dạy Toán HSG 9 và chuyên Toán cấp 3 hàng đầu.
Nhiệm vụ: Lập báo cáo bách khoa toàn thư siêu chi tiết về chuyên đề: "{query}".

🚨 QUY TẮC THIẾT QUÂN LUẬT - SỐ LƯỢNG BẮT BUỘC:
1. Bạn BẮT BỘC phải trình bày ĐỦ VÀ ĐÚNG 50 PHƯƠNG PHÁP / KỸ THUẬT / DẠNG TOÁN RIÊNG BIỆT liên quan đến chuyên đề này.
2. Đánh số thứ tự nghiêm ngặt từ 1 đến 50 (Từ ### Phương pháp 1 cho đến ### Phương pháp 50). Tuyệt đối không được dừng lại sớm, không được gộp nhóm lười biếng.
3. Nếu chủ đề có ít phương pháp thực tế, hãy đào sâu các biến thể nâng cao, các bài toán cực trị, các trường hợp biên hoặc các bổ đề mở rộng để bù đắp đủ đúng 50 mục.

Cấu trúc chi tiết cho MỖI phương pháp trong 50 phương pháp:
- **Tên phương pháp / Kỹ thuật cụ thể**
- **Bản chất toán học & Công thức cốt lõi**
- **Ví dụ minh họa chuẩn đề thi HSG 9 / Chuyên**
- **Lời giải chi tiết từng bước**

Dữ liệu tham khảo từ Web:
{search_context}

Hãy bắt đầu viết báo cáo toàn diện đủ 50 phương pháp ngay bây giờ:
"""
