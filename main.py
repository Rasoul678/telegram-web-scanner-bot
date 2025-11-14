import requests
import hashlib
import os
import json
from datetime import datetime
import pytz

EMBASSY_URL = "https://www.bmeia.gv.at/oeb-teheran"
VFS_URL = "https://visa.vfsglobal.com/irn/en/aut"

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ACCESS_KEY = os.getenv("APIFLASH_ACCESS_KEY")

EMB_CACHE_FILE = "/tmp/emb_last_hash.json"
VFS_CACHE_FILE = "/tmp/vfs_last_hash.json"
EMB_SCREENSHOT_FILE = "embassy_screenshot.png"
VFS_SCREENSHOT_FILE = "vfs_screenshot.png"

TARGET_TIMES = ["01:00","06:00","09:00","12:00","14:00","16:00","18:00","20:00","22:00","23:00","00:00","00:30"]

def get_site_hash(url):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return hashlib.sha256(r.text.encode()).hexdigest()
    except Exception as e:
        print(f"❌ Error fetching site: {e}")
        send_telegram(f"❌ Error fetching site: {e}")
        return None


def read_cached_hash(cache:str):
    if os.path.exists(cache):
        with open(cache, "r") as f:
            return json.load(f).get("hash")
    return None


def write_cached_hash(cache:str,hash_value):
    with open(cache, "w") as f:
        json.dump({"hash": hash_value}, f)


def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("⚠️ Missing Telegram credentials.")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10,
        )
        print("📨 Telegram message sent.")
    except Exception as e:
        print(f"❌ Telegram send failed: {e}")
        send_telegram(f"❌ Telegram send failed: {e}")

def send_image_to_telegram(image_path, caption):
    """Send image to telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(image_path, "rb") as photo:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": photo})

def take_screenshot(url: str, is_vfs:bool=False):
    """Take picture"""
    apiflash_url = "https://api.apiflash.com/v1/urltoimage"
    params = {
        "access_key": ACCESS_KEY,
        "url": url,
        "format":"jpeg" ,
        "fresh":"true" ,
        "response_type":"image",
        "no_cookie_banners":"true",
        "full_page":"true",
        "scroll_page":"true",
        "wait_until":"network_idle"
    }

    if is_vfs:
        params["css"] = "body%7Bbackground-color%3A%23000%3B%7D%0Ap%2Ch2%2Ch3%20%7Bcolor%3A%23FFF%20!important%3B%7D"

    r = requests.get(apiflash_url, params=params)

    file_name = VFS_SCREENSHOT_FILE if is_vfs else EMB_SCREENSHOT_FILE

    with open(file_name, "wb") as f:
        f.write(r.content)

def refresh_screenshots(url:str):
    take_screenshot(url)
    take_screenshot(url=VFS_URL, is_vfs=True)

def check_site(url:str,cache:str,time:str):
    new_hash = get_site_hash(url)
    if not new_hash:
        return

    old_hash = read_cached_hash(cache)

    if not old_hash:
        print("🆕 First run, saving hash.")
        send_telegram(f"🟢 Started monitoring \n{url}")
        write_cached_hash(cache, new_hash)
        return

    if new_hash != old_hash:
        refresh_screenshots(url)

        print("⚠️ Site changed!")
        send_telegram(f"⚠️ Website changed!\n{url}")
        send_image_to_telegram(EMB_SCREENSHOT_FILE, "⚠️❌❌❌ سایت سفارت تغییر کرد!❌❌❌⚠️")
        send_image_to_telegram(VFS_SCREENSHOT_FILE, "سایت vfs ایران-اتریش")
    else:
        if time in TARGET_TIMES:
            print("✅ تغییری در سایت ایجاد نشد!")
            send_telegram(f"✅ تغییری در سایت ایجاد نشد!\n{url}")
            if time in ["09:00","23:00"]:
                refresh_screenshots(url)
                send_image_to_telegram(EMB_SCREENSHOT_FILE, "سایت سفارت 🇦🇹")
                send_image_to_telegram(VFS_SCREENSHOT_FILE, "سایت vfs ایران-اتریش")


    write_cached_hash(EMB_CACHE_FILE, new_hash)


def main():
    """Check site changes"""
    iran_tz = pytz.timezone("Asia/Tehran")
    now = datetime.now(iran_tz).strftime("%H:%M")

    if now == "06:00":
        send_telegram(f"🟢 Started monitoring: \n{EMBASSY_URL}\n{VFS_URL}")

    check_site(url=EMBASSY_URL,cache=EMB_CACHE_FILE,time=now)
    # check_site(url=VFS_URL,cache=VFS_CACHE_FILE,time=now) // 403 Forbidden issue

    if now == "01:00":
        send_telegram(f"🔴 Stopped monitoring: \n{EMBASSY_URL}\n{VFS_URL}")

if __name__ == "__main__":
    main()
