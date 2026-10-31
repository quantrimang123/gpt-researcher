import os
import time
from google import genai
from duckduckgo_search import DDGS

def main():
    # Khởi tạo Gemini client chuẩn mới nhất
    client = genai.Client()
    
    # Sử dụng model Flash mới nhất: Tốc độ cao, thông minh và hỗ trợ context token cực lớn
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

    os.makedirs('reports', exist_ok=True)

    for idx, query in enumerate(topics, 1):
        print(f"\n[{idx}/{len(topics)}] Starting research on: {query}")
        
        # 1. Tìm kiếm thông tin trên web qua DuckDuckGo
        search_results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=10): # Có thể kéo dài số lượng kết quả lấy về nhờ token khủng
                    search_results.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}\n")
        except Exception as e:
            print(f"Search error for '{query}': {e}")
            continue

        search_context = '\n'.join(search_results)

        # 2. Prompt tổng hợp chi tiết
        prompt = f'''
        You are an expert research assistant. Based on the extensive web search results below, write a comprehensive, highly detailed, and professional research report in Markdown format about: {query}

        Web Search Results:
        {search_context}

        Please format the output cleanly with an introduction, deep technical analysis, key theorems/methods, and a conclusion.
        '''

        # 3. Gọi Gemini với model token khủng
        try:
            print(f'Generating research report using {model_name}...')
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            report = response.text

            safe_filename = "".join(c if c.isalnum() else "_" for c in query)[:40].lower()
            filename = f"reports/report_{idx}_{safe_filename}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Successfully saved report to {filename}")
            
        except Exception as e:
            print(f"Gemini generation error for '{query}': {e}")

        time.sleep(3)

    print("\nAll research tasks completed successfully!")

if __name__ == '__main__':
    main()
