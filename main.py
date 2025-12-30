import os
import time
import json
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ========= ENV VARS =========
WHOOP_EMAIL = os.getenv("WHOOP_EMAIL")
WHOOP_PASSWORD = os.getenv("WHOOP_PASSWORD")

WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE = os.getenv("PHONE_NUMBER")  # e.g. 91xxxxxxxxxx
USER_NAME = os.getenv("USER_NAME", "Himanshu")

if PHONE and PHONE.startswith("91"):
    PHONE = "+" + PHONE

if not WHOOP_EMAIL or not WHOOP_PASSWORD:
    raise RuntimeError("WHOOP_EMAIL and WHOOP_PASSWORD must be set")
if not WHATSAPP_URL or not WHATSAPP_API_KEY or not PHONE:
    raise RuntimeError("WHATSAPP_URL, WHATSAPP_API_KEY, PHONE_NUMBER must be set")

# ========= SELENIUM SETUP =========
def create_driver(headless: bool = True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,800")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def wait_for_any(driver, timeout, locators):
    """Return first visible element that matches any of the given locators."""
    end = time.time() + timeout
    last_error = None
    while time.time() < end:
        for by, value in locators:
            try:
                elem = driver.find_element(by, value)
                if elem.is_displayed():
                    return elem
            except Exception as e:
                last_error = e
        time.sleep(0.5)
    raise TimeoutException(str(last_error) if last_error else "Element not found for any locator")

# ========= LOGIN TO WHOOP (WEB) =========
def login_to_whoop(driver):
    wait = WebDriverWait(driver, 30)

    driver.get("https://app.whoop.com")
    print("Opened WHOOP app; initial URL:", driver.current_url)
    time.sleep(3)
    print("URL after redirect:", driver.current_url)

    # Email field (generic selectors) [web:142]
    email_input = wait_for_any(
        driver,
        timeout=25,
        locators=[
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input#email"),
            (By.CSS_SELECTOR, "input[name='email']"),
            (By.CSS_SELECTOR, "input[type='text']"),
        ],
    )

    # Password field
    password_input = wait_for_any(
        driver,
        timeout=25,
        locators=[
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input#password"),
            (By.CSS_SELECTOR, "input[name='password']"),
        ],
    )

    print("Located email and password inputs")

    email_input.clear()
    email_input.send_keys(WHOOP_EMAIL)
    password_input.clear()
    password_input.send_keys(WHOOP_PASSWORD)

    # Login button [web:142]
    login_button = wait_for_any(
        driver,
        timeout=20,
        locators=[
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(., 'Sign in')]"),
            (By.XPATH, "//button[contains(., 'Log in')]"),
        ],
    )

    login_button.click()
    print("Clicked login button, waiting for app to load...")

    # Wait for app shell / home screen [web:150][web:266]
    try:
        wait.until(lambda d: "app.whoop.com" in d.current_url)
    except TimeoutException:
        pass

    try:
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(., 'Recovery') or contains(., 'Sleep') or contains(., 'Strain')]")
            )
        )
    except TimeoutException:
        print("Warning: timed out waiting for main widgets; URL:", driver.current_url)

    print("Login finished. Final URL:", driver.current_url)

# ========= HELPERS FOR SCRAPING =========
def safe_get_text(driver, description, xpath_list):
    for xp in xpath_list:
        try:
            elem = driver.find_element(By.XPATH, xp)
            txt = elem.text.strip()
            if txt:
                print(f"{description}: {txt}")
                return txt
        except Exception:
            continue
    print(f"{description}: NOT FOUND")
    return None

def parse_number(value, remove_chars=None):
    if value is None:
        return None
    s = value.lower()
    if remove_chars:
        for c in remove_chars:
            s = s.replace(c, "")
    s = s.strip()
    try:
        return float(s)
    except ValueError:
        return None

def parse_sleep_hours(s: str) -> float | None:
    if not s:
        return None
    s = s.lower().replace("hours", "").replace("hour", "").replace("hrs", "").replace("hr", "")
    s = s.replace("h", "").strip()
    # formats: "7:30", "7.5", "7 30m"
    if ":" in s:
        parts = s.split(":", 1)
        try:
            h = float(parts[0])
            m = float(parts[1])
            return round(h + m / 60.0, 2)
        except ValueError:
            return None
    if "m" in s:
        s = s.replace("m", "")
        parts = s.split()
        if len(parts) == 2:
            try:
                h = float(parts[0])
                m = float(parts[1])
                return round(h + m / 60.0, 2)
            except ValueError:
                return None
    try:
        return round(float(s), 2)
    except ValueError:
        return None

# ========= SCRAPE WHOOP DASHBOARD METRICS =========
def fetch_whoop_metrics(driver):
    # Make sure we are on the Overview / Home screen showing Recovery, Sleep, Strain. [web:150][web:266]
    time.sleep(5)

    print("====== RAW METRICS (TEXT) ======")

    # Recovery %, HRV, RHR
    recovery_raw = safe_get_text(
        driver,
        "Recovery dial",
        [
            "//*[contains(., 'Recovery')]/descendant::*[contains(@class,'value') or contains(@class,'score')][1]",
        ],
    )
    hrv_raw = safe_get_text(
        driver,
        "HRV",
        [
            "//*[contains(., 'HRV') or contains(., 'Heart Rate Variability')]/following::span[1]",
        ],
    )
    rhr_raw = safe_get_text(
        driver,
        "Resting HR",
        [
            "//*[contains(., 'Resting Heart Rate') or contains(., 'RHR')]/following::span[1]",
        ],
    )

    # Sleep total & deep sleep – you may need to click into Sleep tab if not visible directly. [web:150][web:257]
    sleep_total_raw = safe_get_text(
        driver,
        "Sleep total",
        [
            "//*[contains(., 'Time Asleep') or contains(., 'Sleep Duration')]/following::span[1]",
            "//*[contains(., 'Slept') and contains(., 'h')][1]",
        ],
    )
    deep_sleep_raw = safe_get_text(
        driver,
        "Deep Sleep",
        [
            "//*[contains(., 'Deep Sleep')]/following::span[1]",
            "//*[contains(., 'SWS')]/following::span[1]",
        ],
    )

    # Strain score [web:150][web:263]
    strain_raw = safe_get_text(
        driver,
        "Strain",
        [
            "//*[contains(., 'Strain')]/descendant::*[contains(@class,'value') or contains(@class,'score')][1]",
        ],
    )

    print("================================")

    # Parse numbers
    recovery = parse_number(recovery_raw, remove_chars=["%"])
    hrv = parse_number(hrv_raw, remove_chars=["ms"])
    rhr = parse_number(rhr_raw, remove_chars=["bpm"])

    sleep_hours = parse_sleep_hours(sleep_total_raw)
    deep_sleep_hours = parse_sleep_hours(deep_sleep_raw)

    strain_score = parse_number(strain_raw)

    print("=== PARSED METRICS (FOR TEMPLATE) ===")
    print("Recovery %:", recovery)
    print("HRV ms:", hrv)
    print("RHR bpm:", rhr)
    print("Sleep hrs:", sleep_hours)
    print("Deep Sleep hrs:", deep_sleep_hours)
    print("Strain score:", strain_score)
    print("=====================================")

    return recovery, hrv, rhr, sleep_hours, deep_sleep_hours, strain_score

# ========= RECOMMENDATION TEXT (SIMPLE) =========
def build_recommendation(recovery, strain, sleep_hours, deep_sleep_hours):
    # Rough guidance influenced by how WHOOP uses these metrics. [web:157][web:160]
    if recovery is None:
        return "Could not read full data today. Go by feel and keep training moderate."

    if recovery >= 67:
        if strain and strain < 10:
            return "Recovery is high but strain is low. Good day to push a bit harder if you want."
        return "Recovery is high. You are ready for challenging training or a strong performance."
    elif recovery >= 34:
        return "Recovery is moderate. Aim for balanced training and prioritize good sleep tonight."
    else:
        return "Recovery is low. Keep strain light, focus on rest, hydration, and quality sleep."

# ========= WHATSAPP TEMPLATE SEND =========
def send_whatsapp_template(
    name,
    recovery,
    hrv,
    rhr,
    sleep_hours,
    deep_sleep_hours,
    strain_score,
    recommendation,
):
    # Use /api/send/template endpoint
    if "/api/send" in WHATSAPP_URL:
        template_url = WHATSAPP_URL.replace("/api/send", "/api/send/template")
    else:
        template_url = f"{WHATSAPP_URL.rstrip('/')}/api/send/template"

    print("WhatsApp template URL:", template_url)

    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_KEY}",
        "Content-Type": "application/json",
    }

    body_params = [
        {"type": "text", "text": str(name)},                      # {{1}}
        {"type": "text", "text": str(recovery)},                  # {{2}}
        {"type": "text", "text": str(hrv)},                       # {{3}}
        {"type": "text", "text": str(rhr)},                       # {{4}}
        {"type": "text", "text": str(sleep_hours)},               # {{5}}
        {"type": "text", "text": str(deep_sleep_hours)},          # {{6}}
        {"type": "text", "text": str(strain_score)},              # {{7}}
        {"type": "text", "text": str(recommendation)},            # {{8}}
    ]

    payload = {
        "phone": PHONE,
        "template": {
            "name": "29dec",  # your template name
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": body_params,
                }
            ],
        },
    }

    print("Sending WhatsApp payload:", json.dumps(payload, indent=2))
    resp = requests.post(template_url, headers=headers, json=payload, timeout=30)
    print("WhatsApp Status:", resp.status_code)
    print("WhatsApp Response:", resp.text)

# ========= MAIN =========
def main():
    # Set headless=False while debugging locally so you can see the browser.
    headless = False
    driver = create_driver(headless=headless)

    try:
        login_to_whoop(driver)
        recovery, hrv, rhr, sleep_hours, deep_sleep_hours, strain_score = fetch_whoop_metrics(driver)

        recommendation = build_recommendation(
            recovery=recovery,
            strain=strain_score,
            sleep_hours=sleep_hours,
            deep_sleep_hours=deep_sleep_hours,
        )

        print("\n=== FINAL VALUES THAT WILL GO IN TEMPLATE ===")
        print("Name:", USER_NAME)
        print("Recovery %:", recovery)
        print("HRV ms:", hrv)
        print("RHR bpm:", rhr)
        print("Sleep hrs:", sleep_hours)
        print("Deep Sleep hrs:", deep_sleep_hours)
        print("Strain Score:", strain_score)
        print("Recommendation:", recommendation)

        send_whatsapp_template(
            USER_NAME,
            recovery,
            hrv,
            rhr,
            sleep_hours,
            deep_sleep_hours,
            strain_score,
            recommendation,
        )

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
