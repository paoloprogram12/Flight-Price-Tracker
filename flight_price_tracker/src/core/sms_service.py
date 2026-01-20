import os
import random
from twilio.rest import Client
from dotenv import load_dotenv


load_dotenv()

# Twilio config
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

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

        # build search results URL
        search_params = f"origin={alert_details['origin']}&destination={alert_details['destination']}"
        search_params += f"&departure_date={alert_details['departure_date']}"
        if alert_details.get('return_date'):
            search_params += f"&return_date={alert_details['return_date']}"
        search_params += f"&trip_type={alert_details['trip_type']}"
        results_link = f"{BASE_URL}/search?{search_params}"

        # unsubscribe link
        unsubscribe_link = f"{BASE_URL}/unsubscribe?alert_id={alert_details['alert_id']}"

        message_body = (
            f"PRICE DROP!\n"
            f"{alert_details['origin']} → {alert_details['destination']} ${flight_details['price']} (Save ${savings:.0f})\n"
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

        # build unsubscribe link
        unsubscribe_link = f"{BASE_URL}/unsubscribe?alert_id={alert_details['alert_id']}"

        message_body = (
            f"Alert Active!\n"
            f"{alert_details['origin']} → {alert_details['destination']}\n"
            f"Watching prices under ${alert_details['price_threshold']}\n"
            f"Stop: {unsubscribe_link}"
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
            f"Alert Deleted\n"
            f"{alert_details['origin']} → {alert_details['destination']}\n"
            f"Unsubscribed - info removed.\n"
        )
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )

        print(f"Alert deleted SMS sent to {to_phone}")
        return True
    except Exception as e:
        print(f"Error sending alert deleted SMS: {e}")
        return False
    
def send_alert_expired_sms(to_phone, alert_details):
    """Send SMS when alert expires"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message_body = (
            f"Alert Expired\n"
            f"{alert_details['origin']} → {alert_details['destination']}\n"
            f"Alert removed - departure date passed.\n"
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