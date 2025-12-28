import os
import requests

WHATSAPP_URL = os.getenv("WHATSAPP_URL")
API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE = os.getenv("PHONE_NUMBER")

if PHONE.startswith("91"):
    PHONE = "+" + PHONE

# ✅ SMART URL FIX
if "/api/send" in WHATSAPP_URL:
    # Already has endpoint, replace with template endpoint
    template_url = WHATSAPP_URL.replace("/api/send", "/api/send/template")
else:
    # Base domain only
    template_url = f"{WHATSAPP_URL.rstrip('/')}/api/send/template"

print("Using URL:", template_url)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "phone": PHONE,
    "template": {
        "name": "himanshuautomation",
        "language": {"code": "en"},
        "components": []
    }
}

response = requests.post(template_url, headers=headers, json=payload)
print("Status:", response.status_code)
print("Response:", response.text)
