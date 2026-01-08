from flask import Flask, request, jsonify, render_template_string
import requests
import cloudscraper
from bs4 import BeautifulSoup
import urllib.parse
import random

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Mobile Safari/604.1"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "*/*",
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SAI v3</title>
<style>
body {background:#000;color:#fff;font-family:Arial;margin:0;padding:0;}
.header{text-align:center;padding:12px;background:#111;border-bottom:1px solid #222;}
.chat{padding:12px;height:80vh;overflow-y:auto;}
.msg{padding:10px;border-radius:10px;margin:8px 0;max-width:85%;}
.user{background:#5a2dff;margin-left:auto;}
.bot{background:#222;margin-right:auto;}
.input-box{display:flex;background:#111;padding:10px;gap:10px;}
input{flex:1;padding:10px;border-radius:6px;border:1px solid #333;background:#000;color:#fff;}
button{padding:10px 15px;background:#5a2dff;color:#fff;border:none;border-radius:6px;cursor:pointer;}
</style>
</head>
<body>
<div class="header">SAI v3 - Render Deploy</div>
<div class="chat" id="chatBox">
<div class="msg bot">হ্যালো! Movie নাম বা কিছু লিখো।</div>
</div>
<div class="input-box">
<input id="input" placeholder="Type...">
<button onclick="send()">Send</button>
</div>
<script>
async function send(){
 let text=document.getElementById('input').value;
 if(!text) return;
 document.getElementById('input').value='';
 addMsg(text,'user');
 let r=await fetch('/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:text})});
 let d=await r.json();
 addMsg(d.content,'bot');
}
function addMsg(t,c){
 let div=document.createElement('div');
 div.className='msg '+c;
 div.innerText=t;
 document.getElementById('chatBox').appendChild(div);
 let el=document.getElementById('chatBox');
 el.scrollTop=el.scrollHeight;
}
</script>
</body>
</html>
"""

def get_links(query):
    scraper = cloudscraper.create_scraper()
    url="https://duckduckgo.com/html/?q="+urllib.parse.quote(query)
    try:
        res=scraper.get(url,headers=get_headers(),timeout=10)
        soup=BeautifulSoup(res.text,'html.parser')
        links=[]
        for a in soup.find_all('a',class_='result__a'):
            href=a.get('href')
            if href and "duckduckgo.com" not in href:
                links.append(href)
        return links[:10]
    except:
        return []

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search',methods=['POST'])
def search():
    data=request.get_json()
    q=data.get('query','')
    links=get_links(q)
    if links:
        return jsonify({"content":"সবচেয়ে মিল পাওয়া লিঙ্ক:\n"+links[0]})
    return jsonify({"content":"কিছু পাওয়া যায়নি 😢"})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
