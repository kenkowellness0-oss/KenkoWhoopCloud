import os
import requests
import json

WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

print("Raw PHONE_NUMBER:", repr(PHONE_NUMBER))

# Fix Indian number format: 91xxxxxxxxxx → +91xxxxxxxxxx
if PHONE_NUMBER and PHONE_NUMBER.startswith('91'):
    clean_phone = '+' + PHONE_NUMBER  # Add +91 prefix
else:
    clean_phone = PHONE_NUMBER

print("WhatsApp phone:", clean_phone)

headers = {
    "Authorization": f"Bearer {WHATSAPP_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "phone": clean_phone,  # ← +91989913****
    "message": "✅ WhatsApp from GitHub Actions - SUCCESS!"
}

if not WHATSAPP_URL.endswith('/api/send'):
    full_url = f"{WHATSAPP_URL.rstrip('/')}/api/send"
else:
    full_url = WHATSAPP_URL

response = requests.post(full_url, headers=headers, json=payload)

print("Status:", response.status_code)
print("Response:", response.text)

