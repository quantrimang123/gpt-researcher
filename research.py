import os
import time
from google import genai
from duckduckgo_search import DDGS

def main():
    client = genai.Client()
    model_name = 'gemini-2.5-flash'

    # Đọc danh sách các chủ đề từ file topics.txt
    if not os.path.exists('topics.txt'):
        print("Error: topics.txt not found!")
        return

    with open('topics.txt', 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not topics:
        print("No topics found in topics.txt")
        return

    os.makedirs('reports', exist_ok=True)

    for idx, query in enumerate(topics, 1):
        print(f"\n[{idx}/{len(topics)}] Starting research on: {query}")
        
        # Tìm kiếm web miễn phí qua DuckDuckGo
        search_results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=8):
                    search_results.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}\n")
        except Exception as e:
            print(f"Search error for '{query}': {e}")
            continue

        search_context = '\n'.join(search_results)

        # Tổng hợp báo cáo bằng Gemini
        prompt = f'''
        You are an expert research assistant. Based on the web search results below, write a comprehensive, detailed, and professional research report in Markdown format about: {query}

        Web Search Results:
        {search_context}

        Please format the output cleanly with an introduction, key concepts, technical details, and a conclusion.
        '''

        try:
            print('Generating research report with Gemini...')
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            report = response.text

            # Đặt tên file theo thứ tự hoặc từ khóa gọn gàng
            safe_filename = "".join(c if c.isalnum() else "_" for c in query)[:40].lower()
            filename = f"reports/report_{idx}_{safe_filename}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Saved report to {filename}")
            
        except Exception as e:
            print(f"Gemini generation error for '{query}': {e}")

        # Nghỉ nhẹ giữa các request để tránh chạm giới hạn tần suất
        time.sleep(3)

if __name__ == '__main__':
    main()
