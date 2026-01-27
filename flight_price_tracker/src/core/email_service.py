import os
import secrets

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ──────────────────────────────────────────────────────────────
# Email Configuration
# Pulls SendGrid credentials and app URL from environment
# variables. SENDER_EMAIL must be a verified sender in your
# SendGrid account or emails will be rejected.
# ──────────────────────────────────────────────────────────────

# Email config
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')  # used to build verification and unsubscribe links


# ──────────────────────────────────────────────────────────────
# Helper: Build the path to an HTML email template
# All email templates live in src/web/templates/ alongside
# the page templates. This helper resolves the path relative
# to this file so it works regardless of the working directory.
# ──────────────────────────────────────────────────────────────


def _get_template_path(template_name):
    """Return the absolute path to an email template file."""
    return os.path.join(
        os.path.dirname(__file__), '..', 'web', 'templates', template_name
    )


def _build_return_date_html(alert_details):
    """Return an HTML snippet for the return date, or empty string if one-way."""
    if alert_details.get('return_date'):
        return f"<p style='margin: 8px 0;'><strong>Return:</strong> {alert_details.get('return_date')}</p>"
    return ""


# ──────────────────────────────────────────────────────────────
# Token Generation
# ──────────────────────────────────────────────────────────────


# generates random verification token.
# Creates a 32-byte URL-safe token using Python's secrets module.
# This token is stored in the database and embedded in the
# verification email link so we can match the click back to
# the correct alert.
def generate_verification_token():
    """Generate a secure random verification token."""
    return secrets.token_urlsafe(32)


# ──────────────────────────────────────────────────────────────
# Email Sending Functions
# Each function below loads an HTML template, fills in the
# placeholders with alert/flight data, and sends it via
# SendGrid. They all return True on success, False on failure.
# ──────────────────────────────────────────────────────────────


# sends email verification link
# Called from the /alerts/create route in app.py right after
# a new alert is saved to the database. The email contains a
# unique link the user must click to activate their alert.
def send_verification_email(to_email, verification_token, alert_details):
    """Send email verification link to user."""
    try:
        # Build the full verification URL that the user will click
        verification_link = f"{BASE_URL}/verify-email?token={verification_token}"

        # reads HTML template
        template_path = _get_template_path('verification_email.html')
        with open(template_path, 'r') as f:
            html_template = f.read()

        # Handle return date HTML
        return_date_html = _build_return_date_html(alert_details)

        # replace placeholders
        html_content = html_template.format(
            origin=alert_details.get('origin'),
            destination=alert_details.get('destination'),
            departure_date=alert_details.get('departure_date'),
            return_date_html=return_date_html,
            price_threshold=alert_details.get('price_threshold'),
            trip_type=alert_details.get('trip_type', '').replace('-', ' ').title(),
            verification_link=verification_link,
        )

        # Construct the email message via SendGrid's Mail helper
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=to_email,
            subject='Verify Your Flight Price Alert',
            html_content=html_content,
        )

        # Send through the SendGrid API
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Verification email sent to {to_email}")
        print(f"SendGrid Response Status Code: {response.status_code}")
        print(f"SendGrid Response Body: {response.body}")
        print(f"SendGrid Response Headers: {response.headers}")
        return True

    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


# Sends a price drop notification to the user when the background
# checker finds a flight below their price threshold.
# Includes the current price, how much they'd save, and a direct
# link to the search results page plus an unsubscribe link.
def send_price_drop_notification(to_email, alert_details, flight_details):
    """Send price drop notification email to user."""
    try:
        # Build search results URL so the user can view flights directly
        search_params = f"origin={alert_details['origin']}&destination={alert_details['destination']}"
        search_params += f"&departure_date={alert_details['departure_date']}"
        if alert_details.get('return_date'):
            search_params += f"&return_date={alert_details['return_date']}"
        search_params += f"&trip_type={alert_details['trip_type']}"

        results_link = f"{BASE_URL}/search?{search_params}"
        unsubscribe_link = f"{BASE_URL}/unsubscribe?alert_id={alert_details['alert_id']}"

        # Read HTML template
        template_path = _get_template_path('price_drop_email.html')
        with open(template_path, 'r') as f:
            html_template = f.read()

        # Handle return date HTML
        return_date_html = _build_return_date_html(alert_details)

        # Calculate savings (threshold minus the actual price found)
        savings = alert_details['price_threshold'] - flight_details['price']

        # Replace placeholders
        html_content = html_template.format(
            origin=alert_details['origin'],
            destination=alert_details['destination'],
            departure_date=alert_details['departure_date'],
            return_date_html=return_date_html,
            price_threshold=alert_details['price_threshold'],
            current_price=flight_details['price'],
            savings=savings,
            airline=flight_details.get('airline', 'Unknown'),
            trip_type=alert_details.get('trip_type', '').replace('-', ' ').title(),
            results_link=results_link,
            unsubscribe_link=unsubscribe_link,
        )

        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=to_email,
            subject=f'Price Drop Alert: ${flight_details["price"]} - {alert_details["origin"]} → {alert_details["destination"]}',
            html_content=html_content,
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Price drop notification sent to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending price drop notification: {e}")
        return False


# Notifies the user that their alert has expired because the
# departure date has already passed. Includes a link back to
# the app so they can create a new alert if they want.
def send_alert_expired_notification(to_email, alert_details):
    """Send notification that alert has expired due to departure date passing."""
    try:
        # Read HTML template
        template_path = _get_template_path('alert_expired_email.html')
        with open(template_path, 'r') as f:
            html_template = f.read()

        # handle return date HTML
        return_date_html = _build_return_date_html(alert_details)

        # replace placeholders
        html_content = html_template.format(
            origin=alert_details['origin'],
            destination=alert_details['destination'],
            departure_date=alert_details['departure_date'],
            return_date_html=return_date_html,
            price_threshold=alert_details['price_threshold'],
            trip_type=alert_details.get('trip_type', '').replace('-', ' ').title(),
            base_url=BASE_URL,
        )

        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=to_email,
            subject=f'Price Alert Expired - {alert_details["origin"]} → {alert_details['destination']}',
            html_content=html_content,
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Alert expired notification sent to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending alert expired notification: {e}")
        return False


# Confirms to the user that their alert has been deleted
# (unsubscribed). Called from the /unsubscribe route in app.py
# right before the alert row is removed from the database.
def send_deleted_alert_notification(to_email, alert_details):
    """Send notifications that alert has been deleted from the database"""
    try:
        # read HTML template
        template_path = _get_template_path('alert_deleted_email.html')
        with open(template_path, 'r') as f:
            html_template = f.read()

        # handles the return date html
        return_date_html = _build_return_date_html(alert_details)

        # replace placeholders
        html_content = html_template.format(
            origin=alert_details['origin'],
            destination=alert_details['destination'],
            departure_date=alert_details['departure_date'],
            return_date_html=return_date_html,
            price_threshold=alert_details['price_threshold'],
            trip_type=alert_details.get('trip_type', '').replace('-', ' ').title(),
            base_url=BASE_URL,
        )

        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=to_email,
            subject=f"Alert Deleted - {alert_details['origin']} → {alert_details['destination']}",
            html_content=html_content,
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Alert deleted confirmation sent to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending alert deleted notification: {e}")
        return False


# Sends a confirmation email after the user clicks the
# verification link and their email is marked as verified.
# Called from the /verify-email route in app.py. Includes
# a search link and an unsubscribe link.
def send_alert_activated_notification(to_email, alert_details):
    """Send notification that alert has been activated."""
    try:
        # Build search results URL so the user can check current prices
        search_params = f"origin={alert_details['origin']}&destination={alert_details['destination']}"
        search_params += f"&departure_date={alert_details['departure_date']}"
        if alert_details.get('return_date'):
            search_params += f"&return_date={alert_details['return_date']}"
        search_params += f"&trip_type={alert_details['trip_type']}"

        results_link = f"{BASE_URL}/search?{search_params}"
        unsubscribe_link = f"{BASE_URL}/unsubscribe?alert_id={alert_details['alert_id']}"

        # Read HTML template
        template_path = _get_template_path('alert_activated_email.html')
        with open(template_path, 'r') as f:
            html_template = f.read()

        # handle return date HTML
        return_date_html = _build_return_date_html(alert_details)

        # replace placeholders
        html_content = html_template.format(
            origin=alert_details['origin'],
            destination=alert_details['destination'],
            departure_date=alert_details['departure_date'],
            return_date_html=return_date_html,
            price_threshold=alert_details['price_threshold'],
            trip_type=alert_details.get('trip_type', '').replace('-', ' ').title(),
            results_link=results_link,
            unsubscribe_link=unsubscribe_link,
        )

        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=to_email,
            subject=f'Alert Activated - {alert_details["origin"]} → {alert_details["destination"]}',
            html_content=html_content,
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Alert activated notification sent to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending alert activated notification: {e}")
        return False


# ──────────────────────────────────────────────────────────────
# Function Reference
#   1. generate_verification_token() - Creates a secure random URL-safe token
#   2. send_verification_email()     - Sends the "please verify your email" link
#   3. send_price_drop_notification()- Alerts the user that a price dropped below threshold
#   4. send_alert_expired_notification() - Tells the user their alert expired
#   5. send_deleted_alert_notification() - Confirms the alert was unsubscribed/deleted
#   6. send_alert_activated_notification() - Confirms the alert is now active
# ──────────────────────────────────────────────────────────────
