import os
import requests
import json

# Get YOUR exact secret names
WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")  # Your PHONE_NUMBER secret

print("Sending WhatsApp message...")

headers = {
    "x-api-key": WHATSAPP_API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "number": PHONE_NUMBER,  # Uses your PHONE_NUMBER secret
    "type": "text",
    "message": "🚀 Hey! Automated test from GitHub Actions!"
}

response = requests.post(WHATSAPP_URL, headers=headers, json=payload)

print("Status:", response.status_code)
print("Response:", response.text)
