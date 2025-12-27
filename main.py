import os
import requests
import json

WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")

headers = {
    "x-api-key": WHATSAPP_API_KEY,   # Correct header name
    "Content-Type": "application/json"
}

payload = {
    "number": WHATSAPP_PHONE,  # Correct field name
    "type": "text",
    "message": "🚀 Hey! This is your automated test message from GitHub Actions!"
}

response = requests.post(WHATSAPP_URL, headers=headers, data=json.dumps(payload))

print("Status:", response.status_code)
print("Response:", response.text)

