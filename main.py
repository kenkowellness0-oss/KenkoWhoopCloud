import os
import requests
import json

# Get secrets from GitHub Actions
WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

# Debug - what we received (remove after testing)
print("WHATSAPP_URL:", repr(WHATSAPP_URL))
print("WHATSAPP_API_KEY:", repr(WHATSAPP_API_KEY[:10]) + "..." if WHATSAPP_API_KEY else "MISSING")
print("PHONE_NUMBER:", repr(PHONE_NUMBER))

print("Sending WhatsApp message...")

# Fix URL automatically (handles both cases)
if WHATSAPP_URL:
    if WHATSAPP_URL.endswith('/api/send'):
        full_url = WHATSAPP_URL
    else:
        full_url = f"{WHATSAPP_URL.rstrip('/')}/api/send"
else:
    print("ERROR: WHATSAPP_URL is missing!")
    exit(1)

print("Using URL:", full_url)

headers = {
    "Authorization": f"Bearer {WHATSAPP_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "phone": PHONE_NUMBER,
    "message": "🚀 Testing WhatsApp API from GitHub Actions! ✔"
}

response = requests.post(full_url, headers=headers, json=payload)

print("Status:", response.status_code)
print("Response:", response.text)
