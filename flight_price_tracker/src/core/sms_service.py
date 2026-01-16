import os
import random
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Twilio config
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

def generate_verification_code():
    """Generate a random 6-digit verification code."""
    return str(random.randint(100000, 999999))

def send_verification_sms(to_phone, verification_code):
    """Send SMS with verification code to user's phone."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body=f"Your Flight Price Tracker verification code is: {verification_code}",
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )

        print(f"Verification SMS sent to {to_phone}")
        print(f"Message SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Error sending verification SMS: {e}")
        return False
    
def send_price_drop_sms(to_phone, alert_details, flight_details):
    """Send SMS when price drops below threshold."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        savings = alert_details['price_threshold'] - flight_details['price']

        message_body = (
            f"✈️ PRICE DROP ALERT!\n\n"
            f"{alert_details['origin']} → {alert_details['destination']}\n"
            f"New Price: ${flight_details['price']}\n"
            f"You save: ${savings:.2f}\n\n"
            f"Check flights now!"
        )

        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )

        print(f"Price drop SMS sent to {to_phone}")
        print(f"Message SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Error sending price drop SMS: {e}")
        return False
    
def send_alert_activated_sms(to_phone, alert_details):
    """Send SMS confirmation when alert is activated."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message_body = (
            f"✅ Your Flight Price Alert is Active!\n\n"
            f"{alert_details['origin']} → {alert_details['destination']}\n"
            f"Departure: {alert_details['departure_date']}\n"
            f"Watching for prices below ${alert_details['price_threshold']}\n\n"
            f"We'll notify you when we find a deal!"
        )

        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )

        print(f"Alert activated SMS sent to {to_phone}")
        return True
    except Exception as e:
        print(f"Error sending alert activated SMS: {e}")
        return False
    
def send_alert_deleted_sms(to_phone, alert_details):
    """Send SMS confirmation when alert is deleted."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message_body = (
            f"🗑️ Alert Deleted\n\n"
            f"{alert_details['origin']} → {alert_details['destination']}\n"
            f"You've been unsubscribed and your info has been removed.\n\n"
            f"Thanks for using Flight Price Tracker!"
        )

        print(f"Alert deleted SMS sent to {to_phone}")
        return True
    except Exception as e:
        print(f"Error sending alert deleted SMS: {e}")
        return False
    
def send_alert_expiredZ_sms(to_phone, alert_details):
    """Send SMS when alert expires"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message_body = (
            f"⏰ Alert Expired\n\n"
            f"{alert_details['origin']} → {alert_details['destination']}\n"
            f"Your alert has been removed because the departure date has passed.\n\n"
            f"Create a new alert anytime!"
        )

        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )

        print(f"Alert expired SMS sent to {to_phone}")
        return True
    except Exception as e:
        print(f"Error sending alert expired SMS: {e}")
        return False