import os
import requests

WHATSAPP_URL = f"{os.getenv('WHATSAPP_URL').rstrip('/')}/api/send/template"
API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE = os.getenv("PHONE_NUMBER")

if PHONE.startswith("91"):
    PHONE = "+" + PHONE

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

response = requests.post(WHATSAPP_URL, headers=headers, json=payload)

print("Status:", response.status_code)
print("Response:", response.text)
