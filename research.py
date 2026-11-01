import os
import time
from openai import OpenAI
from ddgs import DDGS
from prompt_template import get_hsg9_prompt

# Lấy 4 biến môi trường Groq đã cài trong Secrets
GROQ_API_KEYS = [
    os.getenv('GROQ_API_KEY'),
    os.getenv('GROQ_API_KEY_1'),
    os.getenv('GROQ_API_KEY_2'),
    os.getenv('GROQ_API_KEY_3'),
]
GROQ_API_KEYS = [k for k in GROQ_API_KEYS if k]

current_key_idx = 0

def get_client():
    if not GROQ_API_KEYS:
        return None
    key = GROQ_API_KEYS[current_key_idx]
    # Khởi tạo OpenAI SDK trỏ thẳng vào endpoint của Groq
    return OpenAI(
        api_key=key,
        base_url="https://api.groq.com/openai/v1"
    )

def main():
    global current_key_idx

    if not GROQ_API_KEYS:
        print("Error: Không tìm thấy bất kỳ Groq API Key nào trong Environment/Secrets!")
        return

    print(f"Đã nạp thành công {len(GROQ_API_KEYS)} Groq API Key. Bắt đầu hệ thống tự động tìm kiếm...")

    # Sử dụng model Llama 3.3 70B đang sống khỏe, cực thông minh và miễn phí tơi tả trên Groq
    MODEL_NAME = 'llama-3.3-70b-versatile'

    if not os.path.exists('topics.txt'):
        print("Error: topics.txt not found!")
        return

    with open('topics.txt', 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not topics:
        print("No topics found in topics.txt")
        return

    os.makedirs('hsg9_reports', exist_ok=True)

    pending_topics = []
    for idx, query in enumerate(topics, 1):
        safe_filename = "".join(c if c.isalnum() else "_" for c in query)[:40].lower()
        filename = f"hsg9_reports/report_{idx:02d}_{safe_filename}.md"
        if not os.path.exists(filename):
            pending_topics.append((idx, query, filename))

    if not pending_topics:
        print("Toàn bộ các chuyên đề đã hoàn thành!")
        return

    print(f"Còn lại {len(pending_topics)} chuyên đề cần xử lý qua Groq.\n")

    for count, (idx, query, filename) in enumerate(pending_topics, 1):
        print(f"\n[{count}/{len(pending_topics)}] Đang đi tìm thông tin cho chủ đề [{idx}/{len(topics)}]: {query}")

        search_results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(f"math olympiad hsg 9 {query}", max_results=12):
                    search_results.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}\n")
        except Exception as e:
            print(f"Lỗi tìm kiếm DuckDuckGo: {e}")
            search_results = ["No external search results. Relying on internal expert math knowledge."]

        search_context = '\n'.join(search_results)
        prompt = get_hsg9_prompt(query, search_context)

        success = False

        while not success:
            client = get_client()
            
