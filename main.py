import os
import requests
import json

WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")

headers = {
    "Authorization": f"Bearer {WHATSAPP_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "phone": f"+{WHATSAPP_PHONE}",
    "message": "👋 Automated test from GitHub Actions! 🚀"
}

response = requests.post(WHATSAPP_URL, headers=headers, data=json.dumps(payload))

print("Status:", response.status_code)
print("Response:", response.text)
