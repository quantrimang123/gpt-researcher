import unittest
from prompt_template import get_hsg9_prompt
from research import iron_shield_validator

class TestHSG9ResearchSystem(unittest.TestCase):

    def test_prompt_template_generation(self):
        """Kiểm tra xem prompt template có sinh ra nội dung chứa đúng từ khóa cốt lõi không."""
        query = "Phương pháp giải phương trình nghiệm nguyên"
        search_context = "Title: Test Title\nSnippet: Test Snippet"
        
        prompt = get_hsg9_prompt(query, search_context)
        
        # Kiểm tra các ràng buộc cứng phải có trong prompt
        self.assertIn("50 PHƯƠNG PHÁP", prompt)
        self.assertIn("NÓI KHÔNG VỚI LÝ THUYẾT HÀN LÂM", prompt)
        self.assertIn(query, prompt)
        self.assertIn(search_context, prompt)

    def test_iron_shield_validator_valid_content(self):
        """Kiểm tra Lớp Sắt Đá (Python Shield) phải CHẤP NHẬN văn bản đạt chuẩn."""
        # Giả lập một bài viết chuẩn có đủ 50 phương pháp và độ dài mỗi mục hợp lệ
        valid_report = ""
        for i in range(1, 51):
            valid_report += f"\n### Phương pháp {i}: Kỹ thuật giải toán nâng cao số {i}\n"
            valid_report += "Đây là nội dung chi tiết bài toán ví dụ với công thức $\\frac{a}{b} + \\sqrt{x} = c$ và các bước giải chi tiết từng dòng một để đảm bảo vượt qua định mức ký tự tối thiểu cho phép.\n" * 3

        is_valid, reason = iron_shield_validator(valid_report)
        self.assertTrue(is_valid, f"Bài viết chuẩn phải được duyệt nhưng lại bị từ chối vì: {reason}")

    def test_iron_shield_validator_missing_methods(self):
        """Kiểm tra Thư ký Python Shield phải TỪ CHỐI nếu thiếu quá nhiều mốc phương pháp."""
        # Bài viết chỉ có 10 phương pháp đầu
        incomplete_report = ""
        for i in range(1, 11):
            incomplete_report += f"\n### Phương pháp {i}: Kỹ thuật {i}\n" + "Nội dung dài dặc đủ ký tự ở đây..." * 10

        is_valid, reason = iron_shield_validator(incomplete_report)
        self.assertFalse(is_valid, "Bài viết thiếu phương pháp nhưng lại bị lọt qua cửa kiểm định!")
        self.assertIn("Thiếu mốc phương pháp", reason)

    def test_iron_shield_validator_lazy_short_content(self):
        """Kiểm tra Thư ký Python Shield phải TỪ CHỐI nếu AI lười biếng viết cụt ngủn mục bất kỳ."""
        # Tạo bài đủ 50 phương pháp nhưng có mục bị viết cụt ngủn dưới 150 ký tự
        lazy_report = ""
        for i in range(1, 51):
            if i == 25:
                lazy_report += f"\n### Phương pháp {i}:\nCụt ngủn.\n" # Mục này quá ngắn
            else:
                lazy_report += f"\n### Phương pháp {i}: Kỹ thuật chuẩn {i}\n" + "Nội dung dài dặc đủ ký tự..." * 10

        is_valid, reason = iron_shield_validator(lazy_report)
        self.assertFalse(is_valid, "Bài viết có mục cụt ngủn nhưng vẫn lọt qua cửa kiểm định!")
        self.assertIn("quá ngắn", reason)

if __name__ == '__main__':
    unittest.main()
