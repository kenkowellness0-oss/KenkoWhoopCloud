import os	
import requests	
	
WHATSAPP_URL = os.getenv("WHATSAPP_URL")	
API_KEY = os.getenv("WHATSAPP_API_KEY")	
PHONE = os.getenv("PHONE_NUMBER")	
	
if PHONE.startswith("91"):	
PHONE = "+" + PHONE	
	
# SMART URL FIX for template endpoint	
if "/api/send" in WHATSAPP_URL:	
template_url = WHATSAPP_URL.replace("/api/send", "/api/send/template")	
else:	
template_url = f"{WHATSAPP_URL.rstrip('/')}/api/send/template"	
	
print("Using URL:", template_url)	
	
headers = {	
Authorization: f"Bearer {API_KEY}",	
Content-Type: "application/json",	
}	
	
# TODO: replace with real WHOOP values	
name = "Himanshu"	
recovery = 78	
hrv = 85	
rhr = 54	
sleep = 7.2	
	
payload = {	
phone: PHONE,	
template: {	
name: "daily_wellness_update",  # approved template	
language: {"code": "en"},	
components: [	
{	
type: "body",	
parameters: [	
{"type": "text", "text": str(name)},	
{"type": "text", "text": str(recovery)},	
{"type": "text", "text": str(hrv)},	
{"type": "text", "text": str(rhr)},	
{"type": "text", "text": str(sleep)},	
],	
}	
],	
},	
}	
	
response = requests.post(template_url, headers=headers, json=payload)	
print("Status:", response.status_code)	
print("Response:", response.text)	
