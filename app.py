from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

app = Flask(__name__)

# ==========================================
# 🎨 ফ্রন্টএন্ড ডিজাইন (HTML/CSS/JS)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAI v3</title>
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
        body {
            font-family: 'Poppins', 'Hind Siliguri', sans-serif;
            background: #0f0f0f;
            color: var(--text-light);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .header {
            background: rgba(20, 20, 20, 0.95);
            padding: 15px;
            text-align: center;
            border-bottom: 1px solid var(--glass-border);
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            scroll-behavior: smooth;
        }

        .message {
            max-width: 90%;
            padding: 15px;
            border-radius: 15px;
            line-height: 1.6;
            animation: fadeIn 0.4s ease;
        }

        .user-msg { align-self: flex-end; background: var(--primary-gradient); }
        .bot-msg { align-self: flex-start; background: var(--glass-bg); border: 1px solid var(--glass-border); width: 95%; }

        .scraped-img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 10px 0;
            display: block;
            border: 1px solid #444;
        }

        .movie-card {
            background: rgba(255,255,255,0.05);
            padding: 10px;
            margin-top: 10px;
            border-left: 4px solid #ff5722;
        }

        .feedback-btns {
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid #333;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .btn-small {
            padding: 8px 15px;
            border-radius: 20px;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: 0.3s;
        }

        .btn-yes { background: #4CAF50; color: white; }
        .btn-no { background: #f44336; color: white; }
        .btn-small:hover { opacity: 0.8; transform: scale(1.05); }

        .input-area {
            padding: 15px;
            background: #1a1a1a;
            display: flex;
            gap: 10px;
            border-top: 1px solid #333;
        }

        input {
            flex: 1;
            padding: 12px 20px;
            border-radius: 25px;
            border: 1px solid #444;
            background: #222;
            color: white;
            outline: none;
        }

        button#sendBtn {
            background: var(--primary-gradient);
            border: none;
            padding: 10px 25px;
            border-radius: 25px;
            color: white;
            cursor: pointer;
            font-weight: 600;
        }

        .footer { text-align: center; padding: 10px; font-size: 11px; color: #666; background: #000; }
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

<div class="header">
    <h1 style="font-size: 20px; color: var(--accent-color);">SAI v3</h1>
    <div style="font-size: 10px; color: #aaa;">Developed by Sayeef Adnan</div>
</div>

<div class="chat-container" id="chatBox">
    <div class="message bot-msg">
        আসসালামু আলাইকুম! আমি <b>Sayeef Adnan</b> এর তৈরি বট। আপনার মুভির নাম বা যেকোনো প্রশ্ন লিখুন।
    </div>
</div>

<div class="input-area">
    <input type="text" id="userInput" placeholder="এখানে আপনার প্রশ্ন লিখুন..." autocomplete="off" onkeypress="if(event.key === 'Enter') startSearch()">
    <button id="sendBtn" onclick="startSearch()">পাঠান</button>
</div>

<div class="footer">
    ⚠️ Warning: Copying Adnan's website without permission is a punishable offense. <br>
    Website developed by <b>Sayeef Adnan</b>.
</div>

<script>
    let currentLinks = [];
    let currentIndex = 0;
    let lastQuery = "";

    async function startSearch() {
        const input = document.getElementById('userInput');
        const query = input.value.trim();
        if (!query) return;

        // Reset state for new search
        lastQuery = query;
        currentLinks = [];
        currentIndex = 0;

        addMessage(query, 'user-msg');
        input.value = '';
        
        processSearch(query, false);
    }

    async function processSearch(query, isNext) {
        const chatBox = document.getElementById('chatBox');
        
        // Loader
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-msg';
        loadingDiv.id = loadingId;
        loadingDiv.innerHTML = '<i>তথ্য বিশ্লেষণ করা হচ্ছে... অনুগ্রহ করে কিছুক্ষণ অপেক্ষা করুন...</i>';
        chatBox.appendChild(loadingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    query: query, 
                    index: currentIndex, 
                    links: currentLinks,
                    is_next: isNext
                })
            });
            
            const data = await response.json();
            document.getElementById(loadingId).remove();
            
            // Update global links only if it's a new search
            if (!isNext) {
                currentLinks = data.all_links || [];
            }
            currentIndex = data.current_index;

            displayResponse(data);

        } catch (e) {
            document.getElementById(loadingId).innerText = 'সার্ভার ত্রুটি! আবার চেষ্টা করুন।';
        }
    }

    function displayResponse(data) {
        const chatBox = document.getElementById('chatBox');
        let html = `<div><b>বিসমিল্লাহির রহমানির রহিম</b><br><br>${data.content}</div>`;
        
        // CineFreak Movies (Always at bottom)
        if (data.movies && data.movies.length > 0) {
            html += `<hr style="margin:15px 0; border:0; border-top:1px dashed #555;"><b>Relevant Movies::</b>`;
            data.movies.forEach(m => {
                html += `<div class="movie-card"><a href="${m.link}" target="_blank" style="color:var(--accent-color); text-decoration:none;">${m.title}</a></div>`;
            });
        }

        html += `<div style="font-size:10px; margin-top:10px; color:#888;">Build by Sayeef Adnan</div>`;
        
        // Satisfaction Buttons
        if (data.has_web_data) {
            html += `
                <div class="feedback-btns">
                    <p style="width:100%; font-size:13px; margin-bottom:5px;">আপনি কি এই তথ্যে সন্তুষ্ট?</p>
                    <button class="btn-small btn-yes" onclick="finishChat(this)">হ্যাঁ, সন্তুষ্ট</button>
                    <button class="btn-small btn-no" onclick="loadNext(this)">না!</button>
                </div>`;
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

    function finishChat(btn) {
        btn.parentElement.innerHTML = "<b style='color:#4CAF50;'>ধন্যবাদ! আপনার সন্তুষ্টিই আমাদের কাম্য।</b><br><small>Build by Sayeef Adnan</small>";
    }

    function loadNext(btn) {
        btn.parentElement.innerHTML = "<i> তথ্য সংগ্রহ করা হচ্ছে...</i>";
        currentIndex++; // Increment index to get next link
        processSearch(lastQuery, true);
    }
</script>

</body>
</html>
"""

# ==========================================
# ⚙️ ব্যাকএন্ড লজিক
# ==========================================

def get_web_links(query):
    """DuckDuckGo থেকে লিংকের লিস্ট সংগ্রহ করা।"""
    url = "https://html.duckduckgo.com/html/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        res = requests.post(url, data={'q': query}, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = []
        for a in soup.find_all('a', class_='result__a'):
            href = a['href']
            # অপ্রয়োজনীয় অ্যাড বা ডাইরেক্ট লিংক ফিল্টার করা
            if "duckduckgo.com" not in href:
                links.append(href)
        return links
    except Exception as e:
        print(f"Link fetch error: {e}")
        return []

def scrape_site_content(url):
    """নির্দিষ্ট ওয়েবসাইট থেকে টেক্সট এবং ছবি সংগ্রহ করা।"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # ক্লিনআপ
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            s.decompose()

        # ছবি সংগ্রহ (প্রথম 20টি পরিষ্কার ছবি)
        images_html = ""
        count = 0
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src and (src.startswith('http') or src.startswith('//')):
                if src.startswith('//'): src = 'https:' + src
                # লোগো বা ছোট আইকন বাদ দেওয়ার চেষ্টা
                images_html += f'<img src="{src}" class="scraped-img" onerror="this.style.display=\'none\'">'
                count += 1
            if count >= 20: break

        # টেক্সট সংগ্রহ
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
        text_content = ""
        for p in paragraphs:
            txt = p.text.strip()
            if len(txt) > 30: # ছোট লাইন বাদ দিয়ে মূল প্যারাগ্রাফ নেয়া
                text_content += f"<p>{txt}</p>"
        
        if len(text_content) < 100: # যদি খুব কম তথ্য থাকে
            return None, None

        return text_content[:6000], images_html 
    except Exception as e:
        print(f"Scraping error at {url}: {e}")
        return None, None

def search_cinefreak(query):
    """CineFreak থেকে মুভি খোঁজা।"""
    url = f"https://www.cinefreak.net/?s={urllib.parse.quote_plus(query)}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        results = []
        for post in soup.find_all('article')[:5]:
            title_tag = post.find(['h1', 'h2', 'h3'])
            link_tag = post.find('a')
            if title_tag and link_tag:
                results.append({
                    'title': title_tag.text.strip(),
                    'link': link_tag['href']
                })
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
    
    # নতুন সার্চ হলে লিংকের লিস্ট রিফ্রেশ করা
    if not is_next or not links:
        links = get_web_links(query)
        index = 0

    scraped_text = ""
    scraped_imgs = ""
    success = False
    current_idx = index

    # যতক্ষণ না কোনো ওয়েবসাইট থেকে ডেটা পাওয়া যায়, লুপ চলবে
    while current_idx < len(links):
        target_url = links[current_idx]
        text, imgs = scrape_site_content(target_url)
        
        if text and len(text) > 200: # পর্যাপ্ত তথ্য পেলে ব্রেক করবে
            scraped_text = text
            scraped_imgs = imgs
            success = True
            break
        else:
            current_idx += 1 # পরের লিংকে যাবে

    # রেসপন্স তৈরি
    content = ""
    if success:
        content = scraped_imgs + scraped_text
    else:
        content = f"দুঃখিত, '{query}' সম্পর্কিত কোনো বিস্তারিত তথ্য এই মুহূর্তে পাওয়া যাচ্ছে না। অনুগ্রহ করে অন্যভাবে চেষ্টা করুন। Communicate with, iamadtul@gmail.com "

    # CineFreak এর তথ্য সবসময় শেষে
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
        
