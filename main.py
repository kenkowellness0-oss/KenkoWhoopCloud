import requests
import json

url = "https://your-base-url.com/api/send"  # replace {{base_url}}

payload = {
    "phone": "+19680825846",  # use only digits with country code if your API requires that
    "message": "Hello John, how are you?"
}

headers = {
    "Content-Type": "application/json"
    # add auth headers here, e.g. "x-api-key": "YOUR_KEY"
}

response = requests.post(url, headers=headers, json=payload)

print(response.status_code)
print(response.text)
