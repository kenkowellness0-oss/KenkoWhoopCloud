import os
import requests

WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")

headers = {
    "Authorization": f"Bearer {WHATSAPP_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "phone": WHATSAPP_PHONE,
    "type": "text",
    "message": "👋 Hello from GitHub Actions automation test! 🚀"
}

response = requests.post(WHATSAPP_URL, json=payload, headers=headers)

print("Status:", response.status_code)
print("Response:", response.text)

