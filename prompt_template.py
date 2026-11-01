def get_hsg9_prompt(query, search_context):
    return f"""
Bạn là chuyên gia soạn đề và giảng dạy Toán HSG 9 và chuyên Toán cấp 3 hàng đầu.
Nhiệm vụ: Lập báo cáo bách khoa toàn thư siêu chi tiết về chuyên đề: "{query}".

🚨 QUY TẮC THIẾT QUÂN LUẬT - CHỐNG CỤT NGỦN (VI PHẠM SẼ BỊ HỦY BỎ):
1. Bạn BẮT BỘC phải trình bày ĐỦ VÀ ĐÚNG 50 PHƯƠNG PHÁP / KỸ THUẬT / DẠNG TOÁN riêng biệt.
2. Đánh số thứ tự từ 1 đến 50 (Từ ### Phương pháp 1 đến ### Phương pháp 50). 
3. ⚠️ QUAN TRỌNG: MỖI phương pháp TRÊN BẮT BỘC phải có độ dài TỐI THIỂU từ 4 đến 6 dòng chữ trở lên, bao gồm:
   - **Bản chất / Công thức** (Viết rõ ràng biểu thức toán học).
   - **Ví dụ minh họa & Lời giải** (Phải trình bày các bước giải chi tiết, không được viết chung chung kiểu "tương tự như trên").
   - Tuyệt đối CẤM viết một dòng cụt ngủn hoặc tóm tắt. Nếu phương pháp nào viết cụt ngủn dưới 4 dòng, toàn bộ báo cáo sẽ bị coi là không đạt yêu cầu.Ghi các kí hiệu Latex toán học (Phải ghi).

Dữ liệu tham khảo từ Web:
{search_context}

Hãy viết báo cáo toàn diện, dài dặc, chi tiết từng li từng tí cho đủ 50 phương pháp ngay bây giờ:
"""
