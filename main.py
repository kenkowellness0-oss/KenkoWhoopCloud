import os
import requests
import json

WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")

headers = {
    "Authorization": WHATSAPP_API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "number": WHATSAPP_PHONE,
    "type": "text",
    "message": "👋 Automated test from GitHub Actions! If you receive this, it works! 🚀"
}

response = requests.post(WHATSAPP_URL, headers=headers, data=json.dumps(payload))

print("Status:", response.status_code)
print("Response:", response.text)

