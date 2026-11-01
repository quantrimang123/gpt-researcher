import os
from openai import OpenAI
from anthropic import Anthropic

# Khởi tạo các client độc lập cho từng Giám khảo trong Hội đồng

# 1. Claude Client (Anthropic)
claude_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# 2. Qwen Client (Chuẩn OpenAI-compatible endpoint - ví dụ qua DashScope hoặc OpenRouter)
qwen_client = OpenAI(
    api_key=os.getenv('QWEN_API_KEY') or os.getenv('OPENAI_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1" # Có thể thay base_url nếu dùng OpenRouter
)

# 3. Llama Client (Chạy qua Groq API với các model Llama 3/3.1 mạnh mẽ chuyên chấm bài)
llama_client = OpenAI(
    api_key=os.getenv('LLAMA_API_KEY') or os.getenv('GROQ_API_KEY'),
    base_url="https://api.groq.com/openai/v1"
)


def evaluate_by_claude(topic, content):
    """Giám khảo 1: Claude (Chủ tịch Hội đồng thẩm định chuyên sâu Toán HSG)"""
    prompt = f"""
Bạn là Chủ tịch Hội đồng Giám khảo Toán HSG. Hãy kiểm tra bài làm chuyên đề: "{topic}".
Nội dung (đã trích xuất):
{content[:10000]}...

TIÊU CHÍ KHẮT KHE:
1. Phải có ĐỦ 50 phương pháp riêng biệt, cấu trúc rõ ràng.
2. Tuyệt đối không gian lận, không viết cụt ngủn, phải có công thức LaTeX và bài toán ví dụ + lời giải chi tiết.

Trả về ĐÚNG định dạng sau (không lan man):
STATUS: [PASS hoặc FAIL]
REASON: [Lý do cụ thể nếu fail]
"""
    try:
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        if "STATUS: PASS" in text:
            return True, "Claude: Đạt"
        return False, text.split("REASON:")[-1].strip() if "REASON:" in text else "Claude đánh rớt."
    except Exception as e:
        return True, f"Bỏ qua lỗi Claude: {e}"


def evaluate_by_qwen(topic, content):
    """Giám khảo 2: Qwen (Chuyên gia thẩm định logic toán học & lập luận)"""
    prompt = f"""
Bạn là Thành viên Hội đồng Giám khảo Toán học cấp cao (Qwen). Hãy thẩm định báo cáo chuyên đề: "{topic}".
Nội dung bài làm:
{content[:8000]}...

TIÊU CHÍ: 
1. Có đủ ĐÚNG 50 phương pháp được đánh số rõ ràng không?
2. Có chứa công thức LaTeX và bài toán ví dụ + lời giải chi tiết không, hay chỉ viết sơ sài, lặp rác, lười biếng?

Trả về ĐÚNG định dạng:
STATUS: [PASS hoặc FAIL]
REASON: [Nhận xét chi tiết của Qwen]
"""
    try:
        response = qwen_client.chat.completions.create(
            model="qwen-max",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=300
        )
        text = response.choices[0].message.content.strip()
        if "STATUS: PASS" in text:
            return True, "Qwen: Đạt"
        return False, text.split("REASON:")[-1].strip() if "REASON:" in text else "Qwen đánh rớt."
    except Exception as e:
        return True, f"Bỏ qua lỗi Qwen: {e}"


def evaluate_by_llama(topic, content):
    """Giám khảo 3: Llama (Chuyên gia phản biện kiểm tra lỗi ngụy biện / lách luật)"""
    prompt = f"""
Bạn là Thành viên Hội đồng Giám khảo phản biện độc lập (Llama). Hãy kiểm tra báo cáo chuyên đề: "{topic}".
Nội dung bài làm:
{content[:8000]}...

TIÊU CHÍ:
1. Đảm bảo đủ 50 phương pháp không bị gộp nhóm trá hình.
2. Kiểm tra xem các bước giải toán có bị cụt ngủn hoặc thiếu logic bước nhảy vọt hay không.

Trả về ĐÚNG định dạng:
STATUS: [PASS hoặc FAIL]
REASON: [Nhận xét chi tiết của Llama]
"""
    try:
        # Sử dụng model Llama mạnh nhất trên Groq (ví dụ llama-3.3-70b-versatile hoặc llama-3.1-70b)
        response = llama_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=300
        )
        text = response.choices[0].message.content.strip()
        if "STATUS: PASS" in text:
            return True, "Llama: Đạt"
        return False, text.split("REASON:")[-1].strip() if "REASON:" in text else "Llama đánh rớt."
    except Exception as e:
        return True, f"Bỏ qua lỗi Llama: {e}"
