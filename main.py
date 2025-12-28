import os
import requests
import json

# Get secrets FIRST
WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

# NOW debug works
print("WHATSAPP_URL:", repr(WHATSAPP_URL))      # ← Add this
print("WHATSAPP_API_KEY:", repr(WHATSAPP_API_KEY[:10]) + "...")  # First 10 chars
print("PHONE_NUMBER:", repr(PHONE_NUMBER))

# Rest of your code...
