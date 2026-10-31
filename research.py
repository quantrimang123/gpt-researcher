import os
import time
from google import genai
from ddgs import DDGS
from prompt_template import get_hsg9_prompt

API_KEYS = [
    os.getenv('GEMINI_API_KEY'),
    os.getenv('GEMINI_API_KEY_1'),
    os.getenv('GEMINI_API_KEY_2'),
    os.getenv('GEMINI_API_KEY_3'],
]
API_KEYS = [k for k in API_KEYS if k]

current_key_idx = 0

def get_client():
    if not API_KEYS:
        return None
    key = API_KEYS[current_key_idx]
    return genai.Client(api_key=key)

def main():
    global current_key_idx

    if not API_KEYS:
        print("Error: Không tìm thấy bất kỳ Gemini API Key nào trong Environment/Secrets!")
        return

    print(f"Đã nạp thành công {len(API_KEYS)} API Key. Bắt đầu hệ thống tự động tìm kiếm và nghiên cứu...")
    
    # Chỉ sử dụng model chuẩn hiện hành, loại bỏ hoàn toàn các model cũ gây lỗi 404
    MODELS = ['gemini-3.8-flash']

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

    print(f"Còn lại {len(pending_topics)} chuyên đề cần xử lý.\n")

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
            if not client:
                print("Lỗi: Không khởi tạo được Gemini Client!")
                break

            for model_name in MODELS:
                if success:
                    break

                for attempt in range(1, 4):
                    try:
                        print(f"Đang gọi model [{model_name}] bằng Key [{current_key_idx + 1}] (Lần thử {attempt})...")
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                        )
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"--> Đã lưu thành công báo cáo vào {filename}")
                        success = True
                        break
                    except Exception as e:
                        err_msg = str(e)
                        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                            print(f"  └─ Key [{current_key_idx + 1}] hết quota (429). Chuyển sang Key tiếp theo...")
                            if len(API_KEYS) > 1:
                                current_key_idx = (current_key_idx + 1) % len(API_KEYS)
                                break
                            else:
                                print("  └─ Đã hết hạn mức Key duy nhất!")
                                time.sleep(10)
                        elif "503" in err_msg or "UNAVAILABLE" in err_msg:
                            print(f"  └─ Server quá tải (503). Thử lại sau {attempt * 5}s...")
                            time.sleep(attempt * 5)
                        else:
                            print(f"  └─ Lỗi: {e}")
                            time.sleep(3)
                if success:
                    break
            if not success and len(API_KEYS) == 1:
                print("Đã thử mọi cách nhưng kẹt quota hoàn toàn.")
                break

        if not success:
            print(f"Bỏ qua chuyên đề {idx} do lỗi hệ thống.")
            break

        time.sleep(3)

    print("\nHoàn thành tiến trình!")

if __name__ == '__main__':
    main()
