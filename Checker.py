import requests
import time
import os
import keyboard

INFO_FILE = "info.txt"

if os.path.exists(INFO_FILE):
    with open(INFO_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        if len(lines) >= 2:
            API_KEY = lines[0]
            BLOCKER_FILTER = lines[1]
        else:
            API_KEY = input("Enter your API key: ").strip()
            BLOCKER_FILTER = input("Enter your blocker filter: ").strip()
            with open(INFO_FILE, "w", encoding="utf-8") as fw:
                fw.write(f"{API_KEY}\n{BLOCKER_FILTER}\n")
else:
    API_KEY = input("Enter your API key: ").strip()
    BLOCKER_FILTER = input("Enter your blocker filter: ").strip()
    with open(INFO_FILE, "w", encoding="utf-8") as fw:
        fw.write(f"{API_KEY}\n{BLOCKER_FILTER}\n")

API_URL = "https://live.glseries.net/api/v1/check"

INPUT_FILE = "links.txt"
OUTPUT_FILE = "progress.txt"
CHECKPOINT_FILE = "checkpoint.txt"

REQUEST_DELAY = 1.0 
RETRIES = 3

blocked = 0
unblocked = 0
errors = 0

def stop_script():
    print("\nF8 pressed. Stopping immediately.")
    os._exit(0)

keyboard.add_hotkey("F8", stop_script)

def load_urls():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return [x.strip() for x in f if x.strip()]

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content.isdigit():
                return int(content)  
            else:
                return 0  
    return 0  

def save_checkpoint(i):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(str(i))

def check_url(url):
    for attempt in range(RETRIES):
        try:
            r = requests.get(
                API_URL,
                params={
                    "token": API_KEY,
                    "url": url,
                    "filter": BLOCKER_FILTER
                },
                timeout=10
            )

            data = r.json()

            if "blocked" in data:
                return "blocked" if data["blocked"] else "unblocked"

            return "error"

        except Exception:
            if attempt < RETRIES - 1:
                time.sleep(2)
            else:
                return "error"

urls = load_urls()
start_index = load_checkpoint()

print(f"Loaded {len(urls)} URLs")
print(f"Resuming from index {start_index}")

for i in range(start_index, len(urls)):
    url = urls[i]
    result = check_url(url)

    if result == "blocked":
        blocked += 1
    elif result == "unblocked":
        unblocked += 1
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(url + "\n")
    else:
        errors += 1

    print(f"{i+1}/{len(urls)}  {url} → {result}")
    save_checkpoint(i + 1)
    time.sleep(REQUEST_DELAY)

print("\n--- Summary ---")
print(f"Total: {len(urls)}")
print(f"Blocked: {blocked}")
print(f"Unblocked: {unblocked}")
print(f"Errors: {errors}")
