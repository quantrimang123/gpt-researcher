import os
import time
from datetime import datetime
from openai import OpenAI
from duckduckgo_search import DDGS
from prompt_template import get_hsg9_prompt

# Đọc bộ 4 key: GROQ_API_KEY, GROQ_API_KEY_2, GROQ_API_KEY_3, GROQ_API_KEY_4
GROQ_API_KEYS = [
    os.getenv('GROQ_API_KEY'),
    os.getenv('GROQ_API_KEY_2'),
    os.getenv('GROQ_API_KEY_3'),
    os.getenv('GROQ_API_KEY_4'),
]
# Lọc bỏ các key bị trống hoặc không hợp lệ
GROQ_API_KEYS = [k for k in GROQ_API_KEYS if k and k.startswith('gsk_')]

current_key_idx = 0

def get_client():
    if not GROQ_API_KEYS:
        return None
    key = GROQ_API_KEYS[current_key_idx]
    return OpenAI(
        api_key=key,
        base_url="https://api.groq.com/openai/v1"
    )

def main():
    global current_key_idx

    print("=== BẮT ĐẦU CHẠY SCRIPT NGHIÊN CỨU ===", flush=True)

    if not GROQ_API_KEYS:
        print("LỖI: Không tìm thấy Groq API Key nào hợp lệ (hoặc key không bắt đầu bằng gsk_)!", flush=True)
        return

    print(f"Đã nạp thành công {len(GROQ_API_KEYS)} Groq API Key.", flush=True)

    MODEL_NAME = 'openai/gpt-oss-20b'

    if not os.path.exists('topics.txt'):
        print("LỖI: Không tìm thấy file 'topics.txt'!", flush=True)
        return

    with open('topics.txt', 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    print(f"Đọc thành công {len(topics)} chuyên đề từ file 'topics.txt'.", flush=True)

    if not topics:
        print("LỖI: File 'topics.txt' trống!", flush=True)
        return

    os.makedirs('hsg9_reports', exist_ok=True)

    # Lấy ngày từ biến môi trường RUN_DATE (do YAML truyền sang), nếu chạy local thì lấy ngày hiện tại
    current_date = os.getenv('RUN_DATE') or datetime.now().strftime('%Y%m%d')

    pending_topics = []
    for idx, query in enumerate(topics, 1):
        safe_filename = "".join(c if c.isalnum() else "_" for c in query)[:30].lower()
        # Tên file gom gọn kèm ngày tháng: 01_ten_chuyen_de_20261101.md
        filename = f"hsg9_reports/{idx:02d}_{safe_filename}_{current_date}.md"
        if not os.path.exists(filename):
            pending_topics.append((idx, query, filename))

    print(f"Số chuyên đề chưa có báo cáo cần xử lý: {len(pending_topics)}", flush=True)

    if not pending_topics:
        print("Toàn bộ các chuyên đề đã có file báo cáo rồi!", flush=True)
        return

    for count, (idx, query, filename) in enumerate(pending_topics, 1):
        print(f"\n--- Xử lý [{count}/{len(pending_topics)}] Chủ đề [{idx} vào file: {filename}]: {query} ---", flush=True)

        search_results = []
        try:
            print("Đang gọi DuckDuckGo Search...", flush=True)
            with DDGS() as ddgs:
                for r in ddgs.text(f"math olympiad hsg 9 {query}", max_results=8):
                    search_results.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}\n")
            print(f"-> Tìm kiếm xong. Lấy được {len(search_results)} kết quả.", flush=True)
        except Exception as e:
            print(f"Lỗi tìm kiếm DuckDuckGo: {e}", flush=True)
            search_results = ["No external search results. Relying on internal expert math knowledge."]

        search_context = '\n'.join(search_results)
        prompt = get_hsg9_prompt(query, search_context)

        success = False

        while not success:
            client = get_client()
            if not client:
                print("Lỗi: Không khởi tạo được Groq Client!", flush=True)
                break

            for attempt in range(1, 4):
                try:
                    print(f"Đang gọi Groq model [{MODEL_NAME}] bằng Key số [{current_key_idx + 1}] (Lần thử {attempt})...", flush=True)

                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": "You are an elite expert mathematics researcher and olympiad coach. You strictly follow all instructions regarding counts and output length without summarizing."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2,       # Giảm nhiệt độ để ép model tập trung tuyệt đối vào nội dung liệt kê dài
                        max_tokens=16384      # Cấp đủ trần token để không bị cụt bài giữa chừng
                    )

                    report = response.choices[0].message.content

                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(report)
                    print(f"--> Đã lưu thành công báo cáo vào {filename}", flush=True)
                    success = True
                    break
                except Exception as e:
                    err_msg = str(e)
                    print(f"  └─ Lỗi gọi API: {err_msg}", flush=True)
                    if "429" in err_msg or "rate_limit_exceeded" in err_msg.lower():
                        print(f"  └─ Chuyển sang Key tiếp theo...", flush=True)
                        if len(GROQ_API_KEYS) > 1:
                            current_key_idx = (current_key_idx + 1) % len(GROQ_API_KEYS)
                            break
                        else:
                            time.sleep(10)
                    else:
                        time.sleep(3)

            if success:
                break

        if not success:
            print(f"⚠️ Bỏ qua chuyên đề {idx} do lỗi liên tục, tiếp tục bài sau...", flush=True)
            # Dùng continue thay vì break để nó không dừng hẳn vòng lặp lớn, ép cày hết sạch các mục còn lại!
            continue

        time.sleep(1)

    print("\n=== HOÀN THÀNH TOÀN BỘ TIẾN TRÌNH ===", flush=True)

if __name__ == '__main__':
    main()
