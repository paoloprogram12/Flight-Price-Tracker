import os
import random

from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ──────────────────────────────────────────────────────────────
# Twilio Configuration
# Pulls Twilio credentials from environment variables.
# TWILIO_PHONE_NUMBER is the Twilio-owned number that appears
# as the sender on every outgoing SMS.
# ──────────────────────────────────────────────────────────────

# Twilio config
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')  # used to build unsubscribe links in SMS messages


# ──────────────────────────────────────────────────────────────
# Code Generation
# ──────────────────────────────────────────────────────────────


# Generates a random 6-digit numeric code (100000–999999).
# This code is stored in the database and sent to the user via
# SMS so they can type it into the verification form to prove
# they own the phone number.
def generate_verification_code():
    """Generate a random 6-digit verification code."""
    return str(random.randint(100000, 999999))


# ──────────────────────────────────────────────────────────────
# SMS Sending Functions
# Each function below creates a Twilio Client, builds a short
# text message, and sends it via the Twilio API.
# They all return True on success, False on failure.
# ──────────────────────────────────────────────────────────────


# Sends the 6-digit verification code to the user's phone.
# Called from the /alerts/create route in app.py right after
# the alert is saved to the database. The user enters this
# code on the /verify-phone page to activate their alert.
def send_verification_sms(to_phone, verification_code):
    """Send SMS with verification code to user's phone."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body=f"Your Flight Price Tracker verification code is: {verification_code}",
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone,
        )

        print(f"Verification SMS sent to {to_phone}")
        print(f"Message SID: {message.sid}")
        return True

    except Exception as e:
        print(f"Error sending verification SMS: {e}")
        return False


# Sends a price-drop notification when the background checker
# (price_checker.py) finds a flight below the user's threshold.
# Includes the route, the new price, and how much they'd save.
def send_price_drop_sms(to_phone, alert_details, flight_details):
    """Send SMS when price drops below threshold."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Calculate how much cheaper this flight is vs. the threshold
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

        # Keep the message short — SMS has a 160-character limit per segment
        message_body = (
            f"PRICE DROP!\n"
            f"{alert_details['origin']} → {alert_details['destination']} "
            f"${flight_details['price']} (Save ${savings:.0f})\n"
        )

        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone,
        )

        print(f"Price drop SMS sent to {to_phone}")
        print(f"Message SID: {message.sid}")
        return True

    except Exception as e:
        print(f"Error sending price drop SMS: {e}")
        return False


# Sends a confirmation SMS after the user successfully verifies
# their phone number on the /verify-phone page. Lets them know
# the alert is live and includes an unsubscribe link.
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
            to=to_phone,
        )

        print(f"Alert activated SMS sent to {to_phone}")
        return True

    except Exception as e:
        print(f"Error sending alert activated SMS: {e}")
        return False


# Confirms to the user that their alert has been deleted
# (unsubscribed). Called from the /unsubscribe route in app.py
# when the user clicks the unsubscribe link.
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
            to=to_phone,
        )

        print(f"Alert deleted SMS sent to {to_phone}")
        return True

    except Exception as e:
        print(f"Error sending alert deleted SMS: {e}")
        return False


# Notifies the user that their alert has expired because the
# departure date has already passed. Called from the background
# price checker (price_checker.py) when it detects a stale alert.
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
            to=to_phone,
        )

        print(f"Alert expired SMS sent to {to_phone}")
        return True

    except Exception as e:
        print(f"Error sending alert expired SMS: {e}")
        return False


# ──────────────────────────────────────────────────────────────
# Function Reference
#   1. generate_verification_code()  - Creates a random 6-digit numeric code
#   2. send_verification_sms()       - Sends the verification code to the user's phone
#   3. send_price_drop_sms()         - Alerts the user that a price dropped below threshold
#   4. send_alert_activated_sms()    - Confirms the alert is now active after phone verification
#   5. send_alert_deleted_sms()      - Confirms the alert was unsubscribed/deleted
#   6. send_alert_expired_sms()      - Tells the user their alert expired (departure date passed)
# ──────────────────────────────────────────────────────────────
