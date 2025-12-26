import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

WHOOP_EMAIL = os.getenv("WHOOP_EMAIL")
WHOOP_PASSWORD = os.getenv("WHOOP_PASSWORD")
WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_KEY = os.getenv("WHATSAPP_KEY")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

# Chrome options for headless mode
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

try:
    print("🌍 Opening WHOOP...")
    driver.get("https://app.whoop.com/login")
    time.sleep(5)

    driver.find_element(By.ID, "email").send_keys(WHOOP_EMAIL)
    driver.find_element(By.ID, "password").send_keys(WHOOP_PASSWORD)
    driver.find_element(By.ID, "password").submit()

    print("🔓 Logging in...")
    time.sleep(10)

    # Go to Recovery page
    driver.get("https://app.whoop.com/recovery")
    time.sleep(8)

    print("📸 Taking screenshot...")
    screenshot_path = "/app/recovery.png"
    driver.save_screenshot(screenshot_path)

    # WhatsApp send
    message = "Your daily WHOOP Recovery update is ready 💪📊"
    print("📩 Sending via WhatsApp...")

    payload = {
        "api_key": WHATSAPP_KEY,
        "phone": PHONE_NUMBER,
        "message": message
    }

    r = requests.post(WHATSAPP_URL, json=payload)
    print("Response:", r.text)

    print("✅ Completed automation successfully!")

except Exception as e:
    print("❌ Error:", e)

finally:
    driver.quit()
