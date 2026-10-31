import os
import time
from google import genai
from ddgs import DDGS
from prompt_template import get_hsg9_prompt

API_KEYS = [
    os.getenv('GEMINI_API_KEY'),
    os.getenv('GEMINI_API_KEY_1'),
    os.getenv('GEMINI_API_KEY_2'),
    os.getenv('GEMINI_API_KEY_3'),
]
API_KEYS = [k for k in API_KEYS if k]

current_key_idx = 0

def get_client():
    if not API_KEYS:
        return None
    key = API_KEYS[current_key_idx]
    return genai.Client(api_key=key)

def rotate_key_and_retry():
    global current_key_idx
    if len(API_KEYS) > 1:
        current_key_idx = (current_key_idx + 1) % len(API_KEYS)
        print(f"⚠️ Hết Quota trên Key cũ! Tự động xoay vòng sang API Key [{current_key_idx + 1}/{len(API_KEYS)}]")
        return get_client()
    return None

def main():
    if not API_KEYS:
        print("Error: Không tìm thấy bất kỳ Gemini API Key nào trong Environment/Secrets!")
        return

    print(f"Đã nạp thành công {len(API_KEYS)} API Key vào hệ thống xoay vòng.")
    client = get_client()

    MODELS = ['gemini-3.8-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']

    if not os.path.exists('topics.txt'):
        print("Error: topics.txt not found! Please create a topics.txt file.")
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
        print("Toàn bộ các chuyên đề trong topics.txt đã được hoàn thành xuất sắc!")
        return

    print(f"Tổng số chuyên đề còn lại cần xử lý: {len(pending_topics)}/{len(topics)}.\n")

    for count, (idx, query, filename) in enumerate(pending_topics, 1):
        print(f"\n[{count}/{len(pending_topics)}] Starting deep research on topic [{idx}/{len(topics)}]: {query}")

        search_results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(f"math olympiad hsg 9 {query}", max_results=12):
                    search_results.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}\n")
        except Exception as e:
            print(f"Search error for '{query}': {e}")
            search_results = ["No external search results. Relying on internal expert math knowledge."]

        search_context = '\n'.join(search_results)

        prompt = get_hsg9_prompt(query, search_context)

        success = False
        max_key_attempts = len(API_KEYS) + 1
        key_attempt = 0

        while not success and key_attempt < max_key_attempts:
            for model_name in MODELS:
                if success: 
                    break
                
