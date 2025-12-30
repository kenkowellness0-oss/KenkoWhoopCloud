import os
import time
import json
import requests
from datetime import datetime
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()

# WhatsApp Gateway ENV Vars
WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

# WHOOP Login Creds
WHOOP_EMAIL = os.getenv("WHOOP_EMAIL")
WHOOP_PASSWORD = os.getenv("WHOOP_PASSWORD")

def fetch_whoop_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 1️⃣ Login
        driver.get("https://app.whoop.com/login")
        time.sleep(6)

        driver.find_element(By.NAME, "email").send_keys(WHOOP_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(WHOOP_PASSWORD)
        driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(10)

        # 2️⃣ Navigate to performance dashboard
        driver.get("https://app.whoop.com/performance")
        time.sleep(8)

        # 3️⃣ Extract Performance Metrics (update selectors during first test)
        recovery = driver.find_element(By.XPATH, "//span[contains(@class,'recovery')]").text.replace("%", "")
        hrv = driver.find_element(By.XPATH, "//span[contains(@class,'hrv')]").text.replace("ms", "")
        rhr = driver.find_element(By.XPATH, "//span[contains(@class,'rhr')]").text.replace("bpm", "")
        sleep = driver.find_element(By.XPATH, "//span[contains(@class,'sleep-duration')]").text.replace("h", "")
        deep_sleep = driver.find_element(By.XPATH, "//span[contains(@class,'deep')]").text.replace("h", "")
        strain = driver.find_element(By.XPATH, "//span[contains(@class,'strain')]").text

        # Recommendation Logic
        rec_val = float(recovery)
        if rec_val > 70:
            rec = "High performance day. Push training."
        elif rec_val > 40:
            rec = "Balanced day. Maintain consistency."
        else:
            rec = "Recovery focus day. Prioritize hydration and sleep."

        return recovery, hrv, rhr, sleep, deep_sleep, strain, rec

    except Exception as e:
        print("Scrape Error:", e)
        return None

    finally:
        driver.quit()


def send_message(data):
    recovery, hrv, rhr, sleep, deep_sleep, strain, rec = data

    clean_phone = '+' + PHONE_NUMBER if PHONE_NUMBER.startswith("91") else PHONE_NUMBER

    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "phone": clean_phone,
        "template_name": "29dec",
        "language": "en_US",
        "params": [
            "Athlete",     # {{1}} - can later be dynamic user name
            recovery,      # {{2}}
            hrv,           # {{3}}
            rhr,           # {{4}}
            sleep,         # {{5}}
            deep_sleep,    # {{6}}
            strain,        # {{7}}
            rec            # {{8}}
        ]
    }

    url = WHATSAPP_URL.rstrip('/') + "/api/send"
    response = requests.post(url, headers=headers, json=payload)

    print("WhatsApp Status:", response.status_code)
    print("WhatsApp Response:", response.text)


def job():
    print("\n--- Running WHOOP Automation Job ---")
    data = fetch_whoop_data()
    if data:
        send_message(data)
    print("--- Job Completed ---\n")


# Schedule 7:00 AM IST
scheduler = BlockingScheduler()
ist = pytz.timezone("Asia/Kolkata")
scheduler.add_job(job, 'cron', hour=7, minute=0, timezone=ist)

print("Automation Scheduler Active — waiting for 7:00 AM IST...")
scheduler.start()
