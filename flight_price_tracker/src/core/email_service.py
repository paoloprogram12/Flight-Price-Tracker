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
        print(f"SendGrid Response Status Code: {response.status_code}")
        print(f"SendGrid Response Body: {response.body}")
        print(f"SendGrid Response Headers: {response.headers}")
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False
    
def send_price_drop_notification(to_email, alert_details, flight_details):
    """Send price drop notification email to user."""
    try:
        # Build search results URL
        search_params = f"origin={alert_details['origin']}&destination={alert_details['destination']}"
        search_params +=f"&departure_date={alert_details['departure_date']}"
        if alert_details.get('return_date'):
            search_params += f"&return_date={alert_details['return_date']}"
        search_params += f"&trip_type={alert_details['trip_type']}"

        results_link = f"{BASE_URL}/search?{search_params}"
        unsubscribe_link = f"{BASE_URL}/unsubscribe?alert_id={alert_details['alert_id']}"

        # Read HTML template
        template_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'templates', 'price_drop_email.html')
        with open(template_path, 'r') as f:
            html_template = f.read()

        # Handle return date HTML
        return_date_html = ""
        if alert_details.get('return_date'):
            return_date_html = f"<p style='margin: 8px 0;'><strong>Return:</strong> {alert_details.get('return_date')}</p>"

        # Calculate savings
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
            unsubscribe_link=unsubscribe_link
        )

        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=to_email,
            subject=f'Price Drop Alert: ${flight_details["price"]} - {alert_details["origin"]} → {alert_details["destination"]}',
            html_content=html_content
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Price drop notification sent to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending price drop notification: {e}")
        return False
    
def send_alert_expired_notification(to_email, alert_details):
    """Send notification that alert has expired due to departure date passing."""
    try:
        # Read HTML template
        template_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'templates', 'alert_expired_email.html')
        with open(template_path, 'r') as f:
            html_template = f.read()

        # handle return date HTML
        return_date_html = ""
        if alert_details.get('return_date'):
            return_date_html = f"<p style='margin: 8px 0;'><strong>Return:</strong> {alert_details.get('return_date')}</p>"

        # replace placeholders
        html_content = html_template.format(
            origin=alert_details['origin'],
            destination=alert_details['destination'],
            departure_date=alert_details['departure_date'],
            return_date_html=return_date_html,
            price_threshold=alert_details['price_threshold'],
            trip_type=alert_details.get('trip_type', '').replace('-', ' ').title(),
            base_url=BASE_URL
        )

        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=to_email,
            subject=f'Price Alert Expired - {alert_details["origin"]} → {alert_details['destination']}',
            html_content=html_content
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Alert expired notification sent to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending alert expired notification: {e}")
        return False