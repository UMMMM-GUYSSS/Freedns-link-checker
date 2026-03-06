import requests
import json
import time

API_TEMPLATE = "https://live.glseries.net/api/v1/check?token=Example_Api_Token&url={}"

INPUT_FILE = "links.txt"
OUTPUT_FILE = "progress.txt"

def check_url(url):
    try:
        api_url = API_TEMPLATE.format(url)
        r = requests.get(api_url, timeout=10)
        r.raise_for_status()

        data = r.json()

        for item in data.get("results", []):
            if item.get("name") == "Lightspeed":
                return item.get("blocked")

    except Exception as e:
        print(f"Error checking {url}: {e}")

    return None


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

for url in urls:
    print(f"Checking: {url}")

    blocked = check_url(url)

    if blocked is False:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
            out.write(f"{url} unblocked\n")
        print(f"{url} → unblocked")


    time.sleep(0.5)  # small delay to avoid API spam

