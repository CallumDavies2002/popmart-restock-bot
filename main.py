from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json
import datetime
import requests

# ========== CONFIG ==========
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1377667687739822136/xOfWCnW9sZ17Wqkg3zcMS9EBmdVB5a0pwLiR4r1IC3O25DleLiUkECICfuTJTPLyUkO4"  # Replace with your actual webhook URL
CHECK_INTERVAL = 30  # Seconds

# ========== LOAD PRODUCTS ==========
with open("products.json", "r") as f:
    PRODUCTS = json.load(f)

# ========== SETUP SELENIUM ==========
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

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
        time.sleep(3)  # Let JavaScript load

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

# ========== MAIN LOOP ==========
def monitor():
    print("🔁 Monitoring started...\n")
    product_states = {name: False for name in PRODUCTS}

    while True:
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

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        monitor()
    finally:
        driver.quit()