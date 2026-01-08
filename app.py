from flask import Flask, request, jsonify, render_template_string
import requests
import cloudscraper
from bs4 import BeautifulSoup
import urllib.parse
import os
import random
import time

app = Flask(__name__)

# ==========================================
# 🛡️ উন্নত সিকিউরিটি ও বাইপাস মেকানিজম
# ==========================================

# বিভিন্ন ব্রাউজারের ইউজার এজেন্ট লিস্ট
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

# ==========================================
# 🎨 ফ্রন্টএন্ড ডিজাইন (অপরিবর্তিত রাখা হয়েছে)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAI v3 - Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&family=Hind+Siliguri:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --glass-bg: rgba(255, 255, 255, 0.1);
            --glass-border: rgba(255, 255, 255, 0.2);
            --text-light: #ffffff;
            --accent-color: #00f2fe;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Poppins', 'Hind Siliguri', sans-serif; background: #0f0f0f; color: var(--text-light); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
        .header { background: rgba(20, 20, 20, 0.95); padding: 15px; text-align: center; border-bottom: 1px solid var(--glass-border); }
        .chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; }
        .message { max-width: 90%; padding: 15px; border-radius: 15px; line-height: 1.6; animation: fadeIn 0.4s ease; }
        .user-msg { align-self: flex-end; background: var(--primary-gradient); }
        .bot-msg { align-self: flex-start; background: var(--glass-bg); border: 1px solid var(--glass-border); width: 95%; }
        .scraped-img { max-width: 100%; height: auto; border-radius: 8px; margin: 10px 0; border: 1px solid #444; }
        .movie-card { background: rgba(255,255,255,0.05); padding: 10px; margin-top: 10px; border-left: 4px solid #ff5722; }
        .input-area { padding: 15px; background: #1a1a1a; display: flex; gap: 10px; }
        input { flex: 1; padding: 12px 20px; border-radius: 25px; border: 1px solid #444; background: #222; color: white; outline: none; }
        button#sendBtn { background: var(--primary-gradient); border: none; padding: 10px 25px; border-radius: 25px; color: white; cursor: pointer; }
        .footer { text-align: center; padding: 10px; font-size: 11px; color: #666; background: #000; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
<div class="header">
    <h1 style="font-size: 20px; color: var(--accent-color);">SAI v3 - High Speed</h1>
    <div style="font-size: 10px; color: #aaa;">Optimized for Cloud Deployment</div>
</div>
<div class="chat-container" id="chatBox">
    <div class="message bot-msg">আসসালামু আলাইকুম! আমি SAI v3। মুভির নাম বা আপনার প্রশ্নটি লিখুন।</div>
</div>
<div class="input-area">
    <input type="text" id="userInput" placeholder="এখানে লিখুন..." onkeypress="if(event.key === 'Enter') startSearch()">
    <button id="sendBtn" onclick="startSearch()">পাঠান</button>
</div>
<div class="footer">Developed by Sayeef Adnan</div>

<script>
    let currentLinks = [];
    let currentIndex = 0;
    let lastQuery = "";

    async function startSearch() {
        const input = document.getElementById('userInput');
        const query = input.value.trim();
        if (!query) return;
        lastQuery = query; currentLinks = []; currentIndex = 0;
        addMessage(query, 'user-msg'); input.value = '';
        processSearch(query, false);
    }

    async function processSearch(query, isNext) {
        const chatBox = document.getElementById('chatBox');
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-msg';
        loadingDiv.id = loadingId;
        loadingDiv.innerHTML = '<i>সার্ভার থেকে তথ্য সংগ্রহ করা হচ্ছে...</i>';
        chatBox.appendChild(loadingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query, index: currentIndex, links: currentLinks, is_next: isNext})
            });
            const data = await response.json();
            document.getElementById(loadingId).remove();
            if (!isNext) currentLinks = data.all_links || [];
            currentIndex = data.current_index;
            displayResponse(data);
        } catch (e) {
            document.getElementById(loadingId).innerText = 'Error: সার্ভার ব্যস্ত আছে। আবার চেষ্টা করুন।';
        }
    }

    function displayResponse(data) {
        const chatBox = document.getElementById('chatBox');
        let html = `<div><b>ফলাফল:</b><br><br>${data.content}</div>`;
        if (data.movies && data.movies.length > 0) {
            html += `<hr style="margin:15px 0;"><b>সংশ্লিষ্ট মুভি লিঙ্ক:</b>`;
            data.movies.forEach(m => {
                html += `<div class="movie-card"><a href="${m.link}" target="_blank" style="color:var(--accent-color);">${m.title}</a></div>`;
            });
        }
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-msg';
        msgDiv.innerHTML = html;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addMessage(text, className) {
        const chatBox = document.getElementById('chatBox');
        const div = document.createElement('div');
        div.className = 'message ' + className;
        div.innerText = text;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
</script>
</body>
</html>
"""

# ==========================================
# ⚙️ ব্যাকএন্ড লজিক (উন্নত করা হয়েছে)
# ==========================================

def get_web_links(query):
    """DuckDuckGo বাইপাস করে লিঙ্ক সংগ্রহ করা।"""
    scraper = cloudscraper.create_scraper()
    # DuckDuckGo HTML অনেক সময় রেন্ডারে ব্লক হয়, তাই আমরা একটু ভিন্ন স্টাইল ট্রাই করি
    search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    
    try:
        res = scraper.get(search_url, headers=get_headers(), timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = []
        for a in soup.find_all('a', class_='result__a'):
            href = a['href']
            if "duckduckgo.com" not in href:
                links.append(href)
        
        # যদি DuckDuckGo তে কাজ না হয়, গুগল ট্রাই করতে পারি (অপশনাল)
        return links
    except Exception as e:
        print(f"Link fetch error: {e}")
        return []

def scrape_site_content(url):
    """উন্নত স্ক্র্যাপিং মেকানিজম।"""
    scraper = cloudscraper.create_scraper()
    try:
        res = scraper.get(url, headers=get_headers(), timeout=12)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            s.decompose()

        images_html = ""
        count = 0
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and src.startswith('http'):
                images_html += f'<img src="{src}" class="scraped-img" onerror="this.style.display=\'none\'">'
                count += 1
            if count >= 10: break

        text_content = ""
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
        for p in paragraphs:
            txt = p.get_text().strip()
            if len(txt) > 40:
                text_content += f"<p>{txt}</p>"
        
        if len(text_content) < 150: return None, None
        return text_content[:5000], images_html 
    except:
        return None, None

def search_cinefreak(query):
    scraper = cloudscraper.create_scraper()
    url = f"https://www.cinefreak.net/?s={urllib.parse.quote(query)}"
    try:
        res = scraper.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        results = []
        for post in soup.find_all('article')[:5]:
            title_tag = post.find(['h1', 'h2', 'h3', 'a'])
            link_tag = post.find('a')
            if title_tag and link_tag:
                results.append({'title': title_tag.text.strip(), 'link': link_tag['href']})
        return results
    except:
        return []

@app.route('/search', methods=['POST'])
def search_api():
    data = request.json
    query = data.get('query', '')
    index = data.get('index', 0)
    links = data.get('links', [])
    is_next = data.get('is_next', False)
    
    if not is_next or not links:
        links = get_web_links(query)
        index = 0

    scraped_text = ""
    scraped_imgs = ""
    current_idx = index
    success = False

    # ভেরিফিকেশন লুপ
    while current_idx < len(links):
        target_url = links[current_idx]
        text, imgs = scrape_site_content(target_url)
        if text:
            scraped_text, scraped_imgs = text, imgs
            success = True
            break
        current_idx += 1

    content = scraped_imgs + scraped_text if success else f"দুঃখিত, '{query}' এর কোনো তথ্য পাওয়া যায়নি। ক্লাউড সার্ভারের কারণে কিছু সাইট ব্লক থাকতে পারে।"
    movie_results = search_cinefreak(query)

    return jsonify({
        'content': content,
        'movies': movie_results,
        'all_links': links,
        'current_index': current_idx,
        'has_web_data': success
    })

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
