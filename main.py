import os
import time
import json
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========= ENV VARS =========
WHOOP_EMAIL = os.getenv("WHOOP_EMAIL")
WHOOP_PASSWORD = os.getenv("WHOOP_PASSWORD")

WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE = os.getenv("PHONE_NUMBER")  # e.g. 91xxxxxxxxxx

USER_NAME = os.getenv("USER_NAME", "Himanshu")

if PHONE and PHONE.startswith("91"):
    PHONE = "+" + PHONE

# ========= SELENIUM SETUP =========
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# ========= HELPER TO SAFE‑GET TEXT =========
def safe_get_text(driver, description, xpath_list):
    for xp in xpath_list:
        try:
            elem = driver.find_element(By.XPATH, xp)
            text = elem.text.strip()
            print(f"{description}: {text}")
            return text
        except Exception:
            continue
    print(f"{description}: NOT FOUND")
    return None

def dump_all_possible_metrics(driver):
    print("====== RAW WHOOP DASHBOARD METRICS (TEXT) ======")

    # Core dials
    safe_get_text(driver, "Recovery score dial", [
        "//*[contains(., 'Recovery')]/descendant::*[@role='img' or contains(@class,'value')][1]",
        "//*[contains(@aria-label,'Recovery')][1]"
    ])
    safe_get_text(driver, "Strain score dial", [
        "//*[contains(., 'Strain')]/descendant::*[contains(@class,'value')][1]"
    ])
    safe_get_text(driver, "Sleep score dial", [
        "//*[contains(., 'Sleep') and contains(., '%')][1]"
    ])

    # Sleep details
    safe_get_text(driver, "Total sleep", [
        "//*[contains(., 'Time Asleep') or contains(., 'Sleep Duration')]/following::span[1]",
        "//*[contains(., 'Slept') and contains(., 'h')][1]"
    ])
    safe_get_text(driver, "Sleep need", [
        "//*[contains(., 'Sleep Need')]/following::span[1]"
    ])
    safe_get_text(driver, "Sleep debt", [
        "//*[contains(., 'Sleep Debt')]/following::span[1]"
    ])

    # Recovery components
    safe_get_text(driver, "HRV (ms)", [
        "//*[contains(., 'HRV')]/following::span[1]",
        "//*[contains(., 'Heart Rate Variability')]/following::span[1]"
    ])
    safe_get_text(driver, "Resting HR (bpm)", [
        "//*[contains(., 'Resting Heart Rate') or contains(., 'RHR')]/following::span[1]"
    ])
    safe_get_text(driver, "Respiratory rate", [
        "//*[contains(., 'Respiratory Rate')]/following::span[1]"
    ])

    # Health Monitor vitals [web:156]
    safe_get_text(driver, "Live Heart rate", [
        "//*[contains(., 'Heart Rate')]/following::span[1]"
    ])
    safe_get_text(driver, "SpO2", [
        "//*[contains(., 'Blood Oxygen') or contains(., 'SpO2')]/following::span[1]"
    ])
    safe_get_text(driver, "Skin temperature", [
        "//*[contains(., 'Skin Temperature')]/following::span[1]"
    ])

    # Movement / activity [web:165]
    safe_get_text(driver, "Steps", [
        "//*[contains(., 'Steps')]/following::span[1]"
    ])
    safe_get_text(driver, "Calories", [
        "//*[contains(., 'Calories')]/following::span[1]"
    ])

    print("================================================")

# ========= WHOOP SCRAPING (NON‑API) =========
def parse_sleep_to_hours(s: str) -> float:
    s = s.lower()
    s = s.replace("hours", "").replace("hour", "").replace("hrs", "").replace("hr", "")
    s = s.replace("h", "").strip()
    if ":" in s:
        h, m = s.split(":", 1)
        return float(h) + float(m) / 60.0
    if "m" in s:
        parts = s.replace("m", "").split()
        if len(parts) == 2:
            h, m = parts
            return float(h) + float(m) / 60.0
    return float(s)

def fetch_whoop_values():
    driver = create_driver()
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://app.whoop.com")
        print("Opened WHOOP web app login page")

        # Login – update selectors if WHOOP changes login form [web:145]
        email_input = wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = wait.until(
            EC.presence_of_element_located((By.NAME, "password"))
        )

        email_input.clear()
        email_input.send_keys(WHOOP_EMAIL)
        password_input.clear()
        password_input.send_keys(WHOOP_PASSWORD)

        login_button = driver.find_element(
            By.XPATH,
            "//button[contains(., 'Log in') or contains(., 'Sign in')]"
        )
        login_button.click()
        print("Submitted login form; waiting for dashboard...")

        # Wait for dashboard / home to load [web:159]
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Recovery')]")
            )
        )
        time.sleep(5)

        # Dump ALL metrics raw text for manual exploration
        dump_all_possible_metrics(driver)

        # Now extract a few key ones robustly

        # Recovery %
        recovery_raw = safe_get_text(driver, "Recovery (for use)", [
            "//*[contains(., 'Recovery')]/descendant::*[contains(@class,'value')][1]",
            "//*[contains(@aria-label,'Recovery')][1]"
        ])
        recovery_score = None
        if recovery_raw:
            recovery_score = float(
                recovery_raw.replace("%", "").strip()
            )

        # HRV ms
        hrv_raw = safe_get_text(driver, "HRV (for use)", [
            "//*[contains(., 'HRV')]/following::span[1]",
            "//*[contains(., 'Heart Rate Variability')]/following::span[1]"
        ])
        hrv_ms = None
        if hrv_raw:
            hrv_ms = float(
                hrv_raw.lower().replace("ms", "").strip()
            )

        # Resting HR bpm
        rhr_raw = safe_get_text(driver, "Resting HR (for use)", [
            "//*[contains(., 'Resting Heart Rate') or contains(., 'RHR')]/following::span[1]"
        ])
        rhr_bpm = None
        if rhr_raw:
            rhr_bpm = float(
                rhr_raw.lower().replace("bpm", "").strip()
            )

        # Sleep hours
        sleep_raw = safe_get_text(driver, "Sleep duration (for use)", [
            "//*[contains(., 'Time Asleep') or contains(., 'Sleep Duration')]/following::span[1]",
            "//*[contains(., 'Slept') and contains(., 'h')][1]"
        ])
        sleep_hours = None
        if sleep_raw:
            sleep_hours = round(parse_sleep_to_hours(sleep_raw), 2)

        print("=== WHOOP VALUES FOR MANUAL CHECK (PARSED) ===")
        print("Recovery %:", recovery_score)
        print("HRV (ms):", hrv_ms)
        print("Resting HR (bpm):", rhr_bpm)
        print("Sleep (hours):", sleep_hours)
        print("==============================================")

        return recovery_score, hrv_ms, rhr_bpm, sleep_hours

    finally:
        driver.quit()

# ========= WHATSAPP TEMPLATE SEND =========
def send_whatsapp_template(name, recovery, hrv, rhr, sleep_hours):
    if "/api/send" in WHATSAPP_URL:
        template_url = WHATSAPP_URL.replace("/api/send", "/api/send/template")
    else:
        template_url = f"{WHATSAPP_URL.rstrip('/')}/api/send/template"

    print("WhatsApp template URL:", template_url)

    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "phone": PHONE,
        "template": {
            "name": "daily_wellness_update",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(name)},        # {{1}}
                        {"type": "text", "text": str(recovery)},    # {{2}}
                        {"type": "text", "text": str(hrv)},         # {{3}}
                        {"type": "text", "text": str(rhr)},         # {{4}}
                        {"type": "text", "text": str(sleep_hours)}, # {{5}}
                    ],
                }
            ],
        },
    }

    print("Sending WhatsApp payload:", json.dumps(payload, indent=2))
    resp = requests.post(template_url, headers=headers, json=payload, timeout=30)
    print("WhatsApp Status:", resp.status_code)
    print("WhatsApp Response:", resp.text)

# ========= MAIN =========
if __name__ == "__main__":
    rec, hrv, rhr, sleep_hrs = fetch_whoop_values()
    # At this point you manually compare these with WHOOP app. [web:159][web:162]
    send_whatsapp_template(USER_NAME, rec, hrv, rhr, sleep_hrs)
