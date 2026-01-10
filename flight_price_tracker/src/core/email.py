import os
import secrets
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

# Email config
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

# generates random verification token.
def generate_verification_token():
    """Generate a secure random verification token."""
    return secrets.token_urlsafe(32)

# sends email verification link
def send_verification_email(to_email, verification_token, alert_details):
    """Send email verification link to user."""
    try:
        verification_link = f"{BASE_URL}/verify-email?token={verification_token}"

        # reads HTML template
        template_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'templates', 'verification_email.html')
        with open(template_path, 'r') as f:
            html_template = f.read()

        # Handle return date HTML
        return_date_html = ""
        if alert_details.get('return_date'):
            return_date_html = f"<p style='margin: 8px 0;'><strong>Return:</strong> {alert_details.get('return_date')}</p>"

        # replace placeholders
        html_content = html_template.format(
            origin=alert_details.get('origin'),
            destination=alert_details.get('destination'),
            departure_date=alert_details.get('departure_date'),
            return_date_html=return_date_html,
            price_threshold=alert_details.get('price_threshold'),
            trip_type=alert_details.get('trip_type', '').replace('-', ' ').title(),
            verification_link=verification_link
        )

        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=to_email,
            subject='Verify Your Flight Price Alert',
            html_content=html_content
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Verification email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False