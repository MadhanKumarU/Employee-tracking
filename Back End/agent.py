import time, json, socket, os, threading
import requests
import win32gui, win32process, psutil
from collections import defaultdict
from datetime import datetime
import ctypes

API_URL = "http://127.0.0.1:8000/ingest"
SYSTEM_NAME = socket.gethostname()
EMPLOYEE_CODE = SYSTEM_NAME

CACHE_FILE = "agent_cache.json"
SEND_INTERVAL = 10
AGGREGATION_INTERVAL = 1

# ---------------------------
# GET ACTIVE WINDOW
# ---------------------------
def get_active_application():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == 0:
        return None
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        p = psutil.Process(pid)
        return p.name()
    except:
        return None

# ---------------------------
# GET IDLE TIME (seconds)
# ---------------------------
def get_idle_time():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    liinfo = LASTINPUTINFO()
    liinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(liinfo))
    millis = ctypes.windll.kernel32.GetTickCount() - liinfo.dwTime
    return millis // 1000  # seconds

# ---------------------------
# Safe cache (offline store)
# ---------------------------
def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_cache(queue):
    with open(CACHE_FILE, "w") as f:
        json.dump(queue, f)

def post_payload(payload):
    try:
        resp = requests.post(API_URL, json=payload, timeout=5)
        return resp.status_code in (200, 201)
    except:
        return False

# ---------------------------
# Background sending thread
# ---------------------------
def sender_thread(store):
    last_sent = time.time()
    queue = load_cache()

    while True:
        now = time.time()
        if now - last_sent >= SEND_INTERVAL:

            apps_snapshot = dict(store)
            apps_payload = {k: int(v) for k, v in apps_snapshot.items() if v > 0}

            if apps_payload:
                payload = {
                    "employee_code": EMPLOYEE_CODE,
                    "system_name": SYSTEM_NAME,
                    "timestamp": datetime.utcnow().isoformat(),
                    "apps": apps_payload
                }

                ok = post_payload(payload)
                if ok:
                    # remove sent values
                    for k in apps_payload:
                        store[k] -= apps_payload[k]
                        if store[k] <= 0:
                            del store[k]
                else:
                    queue.append(payload)
                    save_cache(queue)

            # Try flushing queue
            if queue:
                remaining = []
                for item in queue:
                    if not post_payload(item):
                        remaining.append(item)
                queue = remaining
                save_cache(queue)

            last_sent = now

        time.sleep(1)

# ---------------------------
# MAIN LOOP
# ---------------------------
def main():
    print("Agent started. System:", SYSTEM_NAME)

    store = defaultdict(int)
    current_app = None

    threading.Thread(target=sender_thread, args=(store,), daemon=True).start()

    while True:
        active_app = get_active_application()
        idle_seconds = get_idle_time()

        if idle_seconds >= 30:
            store["__IDLE_TIME__"] += 1
            print(f"Idle… {store['__IDLE_TIME__']} sec")
        else:
            if active_app:
                store[active_app] += 1
                if active_app != current_app:
                    print(f"\nACTIVE APP: {active_app}  Total Sec: {store[active_app]}")
                    current_app = active_app

        time.sleep(AGGREGATION_INTERVAL)

if __name__ == "__main__":
    main()
