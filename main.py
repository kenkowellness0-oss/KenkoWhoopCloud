import os
import requests
import json

# Get secrets
WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

print("Sending WhatsApp message...")

headers = {
    "Authorization": f"Bearer {WHATSAPP_API_KEY}",  # ← Bearer token from cURL!
    "Content-Type": "application/json"
}

payload = {
    "phone": PHONE_NUMBER,
    "message": "Hello John, how are you?",
    "header": "Test header",
    "footer": "Test footer",
    "buttons": [
        {
            "id": "id_1",
            "title": "Fine"
        },
        {
            "id": "id_2",
            "title": "Not well"
        }
    ]
}

response = requests.post(f"{WHATSAPP_URL}/api/send", headers=headers, json=payload)

print("Status:", response.status_code)
print("Response:", response.text)
