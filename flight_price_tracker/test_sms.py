import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Get Twilio credentials from .env
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Your verified phone number
YOUR_PHONE = input("Enter your phone number +15551234567: ")

try:
    # Create Twilio Client
    client = Client(TWILIO_ACCOUNT_SID, TWILO_AUTH_TOKEN)

    # Send test message
    message = client.messages.create(
        body="Test from Flight Price Tracker. Your SMS alerts work.",
        from_=TWILIO_PHONE_NUMBER,
        to=YOUR_PHONE
    )

    print(f"SMS sent successfully!")
    print(f"Message SID: {message.sid}")
    print(f"Status: {message.status}")
    print(f"Check your phone fo the message.")

except Exception as e:
    print(f"Error sending SMS: {e}")