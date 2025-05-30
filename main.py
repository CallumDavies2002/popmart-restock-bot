from flask import Flask
import threading
import time
import json
import datetime
import requests
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# ========== CONFIG ==========
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CHECK_INTERVAL = 30  # Seconds

# ========== FLASK SETUP ==========
app = Flask(__name__)

@app.route("/")
def index():
    return "Pop Mart monitor is running!"

# ========== LOAD PRODUCTS ==========
with open("products.json", "r") as f:
    PRODUCTS = json.load(f)

# ========== SETUP SELENIUM (undetected-chromedriver) ==========
options = uc.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options)

# ========== STOCK CHECK ==========
def send_discord_alert(product_name, url):
    message = {
        "content": f"🚨 **{product_name} is in stock!** 👉 {url}"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=message)
    except Exception as e:
        print(f"⚠️ Failed to send Discord alert: {e}")

def is_in_stock_popmart(url):
    try:
        driver.get(url)
        time.sleep(3)
        buttons = driver.find_elements(By.TAG_NAME, "div")
        for btn in buttons:
            text = btn.text.strip().lower()
            if "add to bag" in text:
                return True
            if "notify me" in text:
                return False
        return False
    except Exception as e:
        print(f"⚠️ Error checking {url}: {e}")
        return False

def within_time_window():
    now = datetime.datetime.now().time()
    return datetime.time(19, 0) <= now <= datetime.time(22, 0)

# ========== MONITORING LOOP ==========
def monitor():
    print("🔁 Monitoring started...\n")
    product_states = {name: False for name in PRODUCTS}

    while True:
        if within_time_window():
            for name, url in PRODUCTS.items():
                in_stock = is_in_stock_popmart(url)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if in_stock and not product_states[name]:
                    print(f"[{timestamp}] ✅ {name} is IN STOCK!")
                    send_discord_alert(name, url)
                    product_states[name] = True
                elif not in_stock and product_states[name]:
                    print(f"[{timestamp}] ❌ {name} went OUT of stock.")
                    product_states[name] = False
                else:
                    print(f"[{timestamp}] ❌ {name} still out of stock.")
        else:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏳ Outside 7–10 PM. Sleeping...")
        time.sleep(CHECK_INTERVAL)

# ========== RUN ==========
if __name__ == "__main__":
    threading.Thread(target=monitor, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))