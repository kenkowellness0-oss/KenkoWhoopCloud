import os
import time
import json
import requests
from datetime import datetime
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

print("🚀 WHOOP Automation Starting...") 

# WhatsApp API ENV Vars
WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

# WHOOP Credentials
WHOOP_EMAIL = os.getenv("WHOOP_EMAIL")
WHOOP_PASSWORD = os.getenv("WHOOP_PASSWORD")

def fetch_whoop_data():
    print("STEP 1️⃣ Launching browser...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print("STEP 2️⃣ Opening WHOOP login page...")
            page.goto("https://account.whoop.com/login", timeout=60000)
            page.wait_for_selector('input[type="email"]', timeout=30000)

            # Updated Selectors
            page.fill('input[type="email"]', WHOOP_EMAIL)
            page.fill('input[type="password"]', WHOOP_PASSWORD)
            page.click('button:has-text("Log In")')

            print("STEP 3️⃣ Waiting after login...")
            page.wait_for_timeout(15000)

            # Debug screenshot *after login*
            page.screenshot(path="login_page.png")
            print("📸 Saved login screenshot → login_page.png")

            print("STEP 4️⃣ Navigating to Performance page...")
            page.goto("https://app.whoop.com/performance", timeout=60000)
            page.wait_for_timeout(10000)

            print("STEP 5️⃣ Scraping metrics...")

            # Capture full HTML for selector debugging
            html = page.content()
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("📄 Saved WHOOP HTML → debug_page.html")

            # TEMP fallback selectors — will adjust once we see HTML
            recovery = page.locator("text=Recovery").locator("xpath=..//span").last.inner_text().replace("%", "")
            hrv = page.locator("text=HRV").locator("xpath=..//span").nth(1).inner_text()
            rhr = page.locator("text=RHR").locator("xpath=..//span").nth(1).inner_text()
            sleep = page.locator("text=Sleep").locator("xpath=..//span").nth(1).inner_text()
            deep_sleep = page.locator("text=Deep").locator("xpath=..//span").nth(1).inner_text()
            strain = page.locator("text=Strain").locator("xpath=..//span").nth(1).inner_text()

            browser.close()
            print("STEP 6️⃣ WHOOP Data Fetch Success ✓")

            return recovery, hrv, rhr, sleep, deep_sleep, strain

        except Exception as e:
            print("❌ ERROR: Scraping failed:", str(e))
            page.screenshot(path="error_screenshot.png")
            print("📸 Saved error screenshot → error_screenshot.png")
            browser.close()
            return None


def send_whatsapp(values):
    if values is None:
        print("⚠️ WhatsApp not sent (No WHOOP data)")
        return
    
    print("STEP 7️⃣ Sending WhatsApp message...")

    recovery, hrv, rhr, sleep, deep_sleep, strain = values

    payload = {
        "phone": PHONE_NUMBER,
        "template_name": "performance_update",
        "language": "en_US",
        "variables": [
            "Kenko User",
            str(recovery),
            str(hrv),
            str(rhr),
            str(sleep),
            str(deep_sleep),
            str(strain),
            "Keep up the amazing progress!"
        ]
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(WHATSAPP_URL, json=payload, headers=headers)
    print("📲 WhatsApp Status:", response.status_code)
    print("📩 WhatsApp Response:", response.text)


def job():
    print("\n====== WHOOP Sync Started ======\n")
    values = fetch_whoop_data()
    send_whatsapp(values)
    print("\n====== Job Finished ======\n")


# Test mode: Run WHOOP once and exit
job()

