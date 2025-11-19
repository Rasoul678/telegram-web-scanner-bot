from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Missing Telegram credentials.")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10,
        )
        print("📨 Telegram message sent.")
    except Exception as e:
        print(f"❌ Telegram send failed: {e}")
        send_telegram(f"❌ Telegram send failed: {e}")

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")   # Required in CI
    chrome_options.add_argument("--no-sandbox")     # Required in GitHub Actions
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Normal human-like user-agent
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Disable "Chrome is being controlled by automated test software"
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    return driver

def main():
    driver = create_driver()

    # Open the website
    driver.get("https://appointment.bmeia.gv.at")

    # Random wait to simulate human
    time.sleep(2 + random.random() * 2)

    # Wait for the select element #Office to load
    wait = WebDriverWait(driver, 30)
    office_select = wait.until(EC.presence_of_element_located((By.ID, "Office")))

    # Get all option texts
    options_list = office_select.find_elements(By.TAG_NAME, "option")

    # Extract options text
    all_options = [opt.text.strip() for opt in options_list]
    message_text = "Office options:\n\n" + "\n".join(all_options)

    if "TEHERAN" in all_options:
        # Send to Telegram
        send_telegram("🟢 گزینه TEHERAN در لیست Office اضافه شد!")

    print("=== Office Options ===")
    print(all_options)
    # send_telegram(message_text)

    driver.quit()

if __name__ == "__main__":
    main()
