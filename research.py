import os
import re
import time
import random
import yaml
from datetime import datetime
from openai import OpenAI
import requests
from prompt_template import get_hsg9_prompt

GROQ_API_KEYS = [
    os.getenv('GROQ_API_KEY'),
    os.getenv('GROQ_API_KEY_2'),
    os.getenv('GROQ_API_KEY_3'),
    os.getenv('GROQ_API_KEY_4'),
]
GROQ_API_KEYS = [k for k in GROQ_API_KEYS if k and k.startswith('gsk_')]

current_key_idx = 0

SEARXNG_INSTANCES = [
    "https://anonsearch.win/search",
    "https://baresearch.org/search",
    "https://etsi.me/search",
    "https://failsearx.culturanerd.it/search",
    "https://find.xenorio.xyz/search",
    "https://grep.vim.wtf/search",
    "https://libresearch.space/search",
    "https://opnxng.com/search",
    "https://oziway.net/search",
    "https://paulgo.io/search",
    "https://priv.au/search",
    "https://sear.lurx.net/search",
    "https://search.anoni.net/search",
    "https://search.banke.cloud/search",
    "https://search.bladerunn.in/search",
    "https://search.catboy.house/search",
    "https://search.chocolatemoo53.com/search",
    "https://search.ctq.ro/search",
    "https://search.einfachzocken.eu/search",
    "https://search.ethibox.fr/search",
    "https://search.femboy.ad/search",
    "https://search.hbubli.cc/search",
    "https://search.im-in.space/search",
    "https://search.inetol.net/search",
    "https://search.jeremyh.xyz/search",
    "https://search.liuzj.net/search",
    "https://search.lumy.live/search",
    "https://search.mdosch.de/search",
    "https://search.mectov.my.id/search",
    "https://search.minus27315.dev/search",
    "https://search.mizuki.st/search",
    "https://search.pereira.is/search",
    "https://search.pi.vps.pw/search",
    "https://search.privacyredirect.com/search",
    "https://search.rhscz.eu/search",
    "https://search.rowie.at/search",
    "https://search.seddens.net/search",
    "https://search.serpensin.com/search",
    "https://search.spiralab.org/search",
    "https://search.undertale.uk/search",
    "https://search.unredacted.org/search",
    "https://search.utilibre.org/search",
    "https://search.yuri.llc/search",
    "https://search.zina.dev/search",
    "https://searx.dresden.network/search",
    "https://searx.githo.st/search",
    "https://searx.linxx.net/search",
    "https://searx.mbuf.net/search",
    "https://searx.mxchange.org/search",
    "https://searx.namejeff.xyz/search",
    "https://searx.oloke.xyz/search",
    "https://searx.ononoki.org/search",
    "https://searx.party/search",
    "https://searx.perennialte.ch/search",
    "https://searx.redgarden.cv/search",
    "https://searx.rhscz.eu/search",
    "https://searx.ro/search",
    "https://searx.sev.monster/search",
    "https://searx.thefloatinglab.world/search",
    "https://searx.tiekoetter.com/search",
    "https://searx.tsmdt.de/search",
    "https://searxng.buffon.cloud/search",
    "https://searxng.canine.tools/search",
    "https://searxng.cups.moe/search",
    "https://searxng.deggo.fyi/search",
    "https://searxng.eshnetwork.space/search",
    "https://searxng.gdebest.net/search",
    "https://searxng.gr/search",
    "https://searxng.jaydenha.uk/search",
    "https://searxng.moonshadow.dev/search",
    "https://searxng.paralaxitaentomology.org/search",
    "https://searxng.shreven.org/search",
    "https://searxng.site/search",
    "https://searxng.tr/search",
    "https://searxng.website/search",
    "https://searxng.wuemeli.com/search",
    "https://shrt.win/search",
    "https://sx.catgirl.cloud/search",
    "https://sx.xo.st/search",
    "https://www.gruble.de/search",
    "https://www.isci.si/search",
    "https://xka.cz/search"
]

current_searxng_idx = 0

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]


def iron_shield_validator(report: str):
    if not report or not isinstance(report, str):
        return False, "Bài báo trống hoặc không phải chuỗi văn bản."
    text = report.strip()
    if not text:
        return False, "Bài báo trống."
    if "### Phương pháp" not in text:
        return False, "Thiếu tiêu đề phương pháp."
    method_blocks = re.findall(r"(?ms)^###\s*Phương pháp\s*\d+.*?(?=^###\s*Phương pháp\s*\d+|\Z)", text)
    if len(method_blocks) < 50:
        return False, f"Tìm thấy {len(method_blocks)}/50 phương pháp."
    for idx, block in enumerate(method_blocks[:50], 1):
        if len(block.strip()) < 150:
            return False, f"Phương pháp {idx} quá ngắn."
    return True, "Đạt chuẩn."


def run_quality_gate(topic: str, report: str):
    ok, reason = iron_shield_validator(report)
    if not ok:
        return False, f"Iron Shield: {reason}"
    return True, "Thành công."


def get_client():
    if not GROQ_API_KEYS:
        return None
    return OpenAI(api_key=GROQ_API_KEYS[current_key_idx], base_url="https://api.groq.com/openai/v1")


def fetch_search_results_with_searxng(query: str, max_target=60):
    global current_searxng_idx
    search_results = []
    seen_snippets = set()
    full_search_term = f"math olympiad hsg 9 {query}"
    print(f"Đang tìm kiếm qua pool SearXNG cho: {full_search_term}...", flush=True)

    total_instances = len(SEARXNG_INSTANCES)
    attempts = 0

    while attempts < total_instances and len(search_results) < max_target:
        url = SEARXNG_INSTANCES[current_searxng_idx]
        current_searxng_idx = (current_searxng_idx + 1) % total_instances
        attempts += 1

        try:
            params = {"q": full_search_term, "format": "json", "language": "vi"}
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            response = requests.get(url, params=params, headers=headers, timeout=4)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                for item in results:
                    if len(search_results) >= max_target:
                        break
                    title = item.get("title", "Olympiad Source")
                    body = item.get("content", "")
                    snippet_str = f"- {title[:30]}: {body[:50]}"
                    if snippet_str not in seen_snippets and body:
                        seen_snippets.add(snippet_str)
                        search_results.append(snippet_str)
                if search_results:
                    print(f"-> Lấy thành công từ instance: {url}", flush=True)
                    break
        except Exception:
            continue

    if not search_results:
        print("⚠️ Toàn bộ pool SearXNG bận, chuyển sang tri thức chuyên gia nội bộ...", flush=True)
        search_results = [
            f"- Chuyên đề nâng cao luyện thi HSG Toán 9: {query}",
            "- Hệ thống phương pháp luận toán học sơ cấp, bất đẳng thức, cực trị và phương trình nghiệm nguyên."
        ]

    return search_results[:max_target]


def main():
    global current_key_idx
    print("=== BẮT ĐẦU CHẠY SCRIPT NGHIÊN CỨU ===", flush=True)

    if not GROQ_API_KEYS:
        print("LỖI: Không tìm thấy Groq API Key!", flush=True)
        return

    MODEL_NAME = 'openai/gpt-oss-20b'

    if not os.path.exists('topics.txt'):
        print("LỖI: Không tìm thấy 'topics.txt'!", flush=True)
        return

    with open('topics.txt', 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    os.makedirs('hsg9_reports', exist_ok=True)
    current_date = os.getenv('RUN_DATE') or datetime.now().strftime('%Y%m%d')

    pending_topics = []
    for idx, query in enumerate(topics, 1):
        safe_filename = "".join(c if c.isalnum() else "_" for c in query)[:30].lower()
        filename = f"hsg9_reports/{idx:02d}_{safe_filename}_{current_date}.md"
        if not os.path.exists(filename):
            pending_topics.append((idx, query, filename))

    if not pending_topics:
        print("Toàn bộ chuyên đề đã có báo cáo!", flush=True)
        return

    for count, (idx, query, filename) in enumerate(pending_topics, 1):
        print(f"\n--- Xử lý [{count}/{len(pending_topics)}] Chủ đề [{idx}]: {query} ---", flush=True)

        search_results = fetch_search_results_with_searxng(query, max_target=60)
        search_context = '\n'.join(search_results)
        prompt = get_hsg9_prompt(query, search_context)

        success = False
        while not success:
            client = get_client()
            if not client:
                break

            for attempt in range(1, 4):
                try:
                    print(f"Gọi Groq [{MODEL_NAME}] Key [{current_key_idx + 1}] (Thử {attempt})...", flush=True)
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an elite expert mathematics researcher. Generate a complete report with exactly 50 numbered methods. Every method must be distinct, include formulas, examples, and reasoning."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2,
                        max_tokens=16384
                    )
                    report = (response.choices[0].message.content or "").strip()

                    quality_ok, quality_reason = run_quality_gate(query, report)
                    if not quality_ok:
                        print(f"  └─ Không đạt: {quality_reason}", flush=True)
                        if attempt < 3:
                            time.sleep(2)
                            continue
                        break

                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(report)

                    yaml_filename = filename.replace('.md', '.yaml')
                    with open(yaml_filename, 'w', encoding='utf-8') as yf:
                        yaml.dump({"topic": query, "report_file": filename, "date": current_date, "status": "APPROVED"}, yf, allow_unicode=True, sort_keys=False)

                    success = True
                    break

                except Exception as e:
                    err_msg = str(e)
                    print(f"  └─ Lỗi API: {err_msg}", flush=True)
                    if "429" in err_msg or "rate_limit_exceeded" in err_msg.lower():
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
            print(f"⚠️ Bỏ qua chuyên đề {idx} do lỗi.", flush=True)
            continue

        time.sleep(1)

    print("\n=== HOÀN THÀNH ===", flush=True)


if __name__ == '__main__':
    main()
