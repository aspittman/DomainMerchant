from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
FROM_NUMBER = os.getenv("FROM_NUMBER")
TO_NUMBER = os.getenv("TO_NUMBER")

def send_sms(message: str):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    client.messages.create(
        body=message,
        from_=FROM_NUMBER,
        to=TO_NUMBER
    )