# research.py
import os
import time
from google import genai
from ddgs import DDGS
from prompt_template import get_hsg9_prompt

def main():
    # Khởi tạo Gemini client chuẩn mới nhất
    client = genai.Client()
    
    # Sử dụng dòng model Flash mới nhất với context token siêu khủng
    model_name = 'gemini-3.8-flash'

    # Kiểm tra file topics.txt
    if not os.path.exists('topics.txt'):
        print("Error: topics.txt not found! Please create a topics.txt file.")
        return

    with open('topics.txt', 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not topics:
        print("No topics found in topics.txt")
        return

    os.makedirs('hsg9_reports', exist_ok=True)

    for idx, query in enumerate(topics, 1):
        print(f"\n[{idx}/{len(topics)}] Starting deep research on: {query}")

        # 1. Cào thông tin qua ddgs (tối ưu số lượng kết quả)
        search_results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=12):
                    search_results.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}\n")
        except Exception as e:
            print(f"Search error for '{query}': {e}")
            search_results = ["No external search results. Relying on internal expert math knowledge."]

        search_context = '\n'.join(search_results)

        # 2. Lấy prompt từ file prompt_template.py đã tách riêng
        prompt = get_hsg9_prompt(query, search_context)

        # 3. Gọi Gemini tạo báo cáo với cơ chế thử lại an toàn
        success = False
        for attempt in range(3):
            try:
                print(f'Generating max-token research report using {model_name} (Attempt {attempt+1})...')
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                report = response.text

                safe_filename = "".join(c if c.isalnum() else "_" for c in query)[:40].lower()
                filename = f"hsg9_reports/report_{idx:02d}_{safe_filename}.md"

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"Successfully saved max-tier report to {filename}")
                success = True
                break
            except Exception as e:
                print(f"Gemini generation error (Attempt {attempt+1}) for '{query}': {e}")
                time.sleep(5)

        if not success:
            print(f"Failed to generate report for topic {idx} after 3 attempts.")

        time.sleep(3)

    print("\nAll research tasks completed successfully!")

if __name__ == '__main__':
    main()
