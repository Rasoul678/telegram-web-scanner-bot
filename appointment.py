import requests
from bs4 import BeautifulSoup
import os
import json
# from lxml import html

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://appointment.bmeia.gv.at/"

CACHE_FILE = ".cache_office.json"   # در Cache کار می‌کند، نه در ریپو

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    print("Telegram status:", r.status_code)


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {"options": []}


def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)


def fetch_options():
    resp = requests.get(URL)
    resp.raise_for_status()

    # tree = html.fromstring(resp.content)
    #
    # options = tree.xpath('//select[@id="Office"]/option/text()')
    # print(options)
    # return options

    soup = BeautifulSoup(resp.text, "html.parser")
    select = soup.find("select", {"id": "Office"})

    if not select:
        raise Exception("Select with id=Office not found!")

    return [opt.get_text(strip=True) for opt in select.find_all("option")]


def main():
    print("Checking Office list...")

    options = fetch_options()
    cache = load_cache()
    old = cache["options"]

    print("Old:", old)
    print("New:", options)

    if "BANGKOK" in options:
        send_telegram("BANGKOK!")

    # چک اضافه شدن TEHERAN
    if "TEHERAN" in options and "TEHERAN" not in old:
        send_telegram("🟢 گزینه TEHERAN در لیست Office اضافه شد!")

    # چک حذف شدن TEHERAN
    if "TEHERAN" not in options and "TEHERAN" in old:
        send_telegram("🔴 گزینه TEHERAN از لیست Office حذف شد!")

    # ذخیره وضعیت جدید
    save_cache({"options": options})


if __name__ == "__main__":
    main()