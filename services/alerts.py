from twilio.rest import Client




def send_sms(message: str):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    client.messages.create(
        body=message,
        from_=FROM_NUMBER,
        to=TO_NUMBER
    )