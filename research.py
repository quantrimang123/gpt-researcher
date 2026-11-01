import os
import re
import time
import yaml
from datetime import datetime
from openai import OpenAI
from duckduckgo_search import DDGS
from prompt_template import get_hsg9_prompt
from api_clients import evaluate_by_claude, evaluate_by_qwen, evaluate_by_llama

GROQ_API_KEYS = [
    os.getenv('GROQ_API_KEY'),
    os.getenv('GROQ_API_KEY_2'),
    os.getenv('GROQ_API_KEY_3'),
    os.getenv('GROQ_API_KEY_4'),
]
GROQ_API_KEYS = [k for k in GROQ_API_KEYS if k and k.startswith('gsk_')]

current_key_idx = 0


def iron_shield_validator(report: str):
    if not report or not isinstance(report, str):
        return False, "Bài báo trống hoặc không phải chuỗi văn bản."

    text = report.strip()
    if not text:
        return False, "Bài báo trống sau khi cắt khoảng trắng."

    if "### Phương pháp" not in text:
        return False, "Thiếu mốc phương pháp: không tìm thấy tiêu đề ### Phương pháp ..."

    method_blocks = re.findall(
        r"(?ms)^###\s*Phương pháp\s*\d+.*?(?=^###\s*Phương pháp\s*\d+|\Z)",
        text,
    )

    if len(method_blocks) < 50:
        return False, f"Thiếu mốc phương pháp: tìm thấy {len(method_blocks)}/50 phương pháp."

    for idx, block in enumerate(method_blocks[:50], 1):
        cleaned = block.strip()
        if len(cleaned) < 150:
            return False, f"Phương pháp {idx} quá ngắn (<150 ký tự)."

    return True, "Đạt chuẩn qua Iron Shield."


def run_quality_gate(topic: str, report: str):
    ok, reason = iron_shield_validator(report)
    if not ok:
        return False, f"Iron Shield: {reason}"

    judge_checks = [
        ("Claude", evaluate_by_claude),
        ("Qwen", evaluate_by_qwen),
        ("Llama", evaluate_by_llama),
    ]
    failures = []

    for judge_name, judge_fn in judge_checks:
        try:
            judge_ok, judge_reason = judge_fn(topic, report)
            if not judge_ok:
                failures.append(f"{judge_name}: {judge_reason}")
        except Exception as exc:
            failures.append(f"{judge_name}: lỗi khi chấm bài - {exc}")

    if failures:
        return False, " | ".join(failures)

    return True, "Đạt kiểm định nội bộ và giám khảo."


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
        print("LỖI: Không tìm thấy Groq API Key nào hợp lệ!", flush=True)
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

    current_date = os.getenv('RUN_DATE') or datetime.now().strftime('%Y%m%d')

    pending_topics = []
    for idx, query in enumerate(topics, 1):
        safe_filename = "".join(c if c.isalnum() else "_" for c in query)[:30].lower()
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
            print("Đang gọi DuckDuckGo Search (60 nguồn đa dạng)...", flush=True)
            with DDGS() as ddgs:
                # Kéo tối đa 60 nguồn, mỗi snippet cắt đúng 50 ký tự để vét sạch dữ liệu mà vẫn an toàn token
                for r in ddgs.text(f"math olympiad hsg 9 {query}", max_results=60):
                    title = (r.get('title') or '')[:30]
                    body = (r.get('body') or '')[:50]
                    search_results.append(f"- {title}: {body}")
            print(f"-> Đã bóc tách xong {len(search_results)} nguồn gọn nhẹ.", flush=True)
        except Exception as e:
            print(f"Lỗi tìm kiếm DuckDuckGo: {e}", flush=True)
            search_results = ["- Ký ức chuyên gia toán học."]

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
                            {
                                "role": "system",
                                "content": "You are an elite expert mathematics researcher and olympiad coach. You strictly follow all instructions regarding counts and output length. Generate a complete, detailed, high-quality report with exactly 50 numbered methods. Every method must be distinct, include formulas, examples, and reasoning. Do not invent fake references. Keep all content rich and deep."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2,
                        max_tokens=16384
                    )

                    report = (response.choices[0].message.content or "").strip()

                    quality_ok, quality_reason = run_quality_gate(query, report)
                    if not quality_ok:
                        print(f"  └─ Báo cáo không đạt kiểm định: {quality_reason}. Bắt đầu làm lại...", flush=True)
                        if attempt < 3:
                            time.sleep(2)
                            continue
                        break

                    # Lưu file báo cáo Markdown
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(report)
                    print(f"--> Đã lưu thành công báo cáo vào {filename}", flush=True)

                    # Tự động sinh file YAML metadata đồng bộ
                    metadata = {
                        "topic": query,
                        "report_file": filename,
                        "date": current_date,
                        "status": "APPROVED",
                        "validator": "Iron Shield + Jury Passed"
                    }
                    yaml_filename = filename.replace('.md', '.yaml')
                    with open(yaml_filename, 'w', encoding='utf-8') as yf:
                        yaml.dump(metadata, yf, allow_unicode=True, sort_keys=False)
                    print(f"--> Đã xuất file metadata YAML vào {yaml_filename}", flush=True)

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
            continue

        time.sleep(1)

    print("\n=== HOÀN THÀNH TOÀN BỘ TIẾN TRÌNH ===", flush=True)


if __name__ == '__main__':
    main()
