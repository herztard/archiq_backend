import requests

from archiq_backend import settings


class SmsClient:
    def __init__(self):
        self.url = f"https://api.mobizon.kz/service/message/sendsmsmessage?apiKey={settings.MOBIZON_KEY}"

    def send_message(self, message: str, phone):
        # Convert PhoneNumber object to string using str() function
        phone_str = str(phone)
        
        body = {"recipient": phone_str}
        body["text"] = message
        resp = requests.post(url=self.url, json=body)
        resp_json = resp.json()
        return resp_json, resp.status_code


sms_client = SmsClient()
