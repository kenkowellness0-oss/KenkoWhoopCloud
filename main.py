import os
import requests

API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE = os.getenv("PHONE_NUMBER")

# Fix Indian phone format
if PHONE and PHONE.startswith("91"):
    PHONE = "+" + PHONE

BASE_URL = "https://wa.nyife.chat"
template_url = f"{BASE_URL}/api/send/template"
print("Template URL:", template_url)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Example WHOOP values – replace with real ones
name = "Himanshu"
recovery = 78
hrv = 85
rhr = 54
sleep = 7.2

payload = {
    "phone": PHONE,
    "template": {
        "name": "report1",      # EXACT template name from dashboard
        "language": {"code": "en"},
        "components": [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": str(name)},      # {{1}}
                    {"type": "text", "text": str(recovery)},  # {{2}}
                    {"type": "text", "text": str(hrv)},       # {{3}}
                    {"type": "text", "text": str(rhr)},       # {{4}}
                    {"type": "text", "text": str(sleep)},     # {{5}}
                ],
            }
        ],
    },
}

response = requests.post(template_url, headers=headers, json=payload)
print("Status:", response.status_code)
print("Response:", response.text)
