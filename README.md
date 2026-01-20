# Flight-Price-Tracker

A web application to track and compare flight prices, with automated email and SMS notifications when prices drop below your target threshold.

## Features

- **Flight Search**: Search for flights by origin, destination, and dates using Amadeus API
- **Airport Autocomplete**: Search airports by code, city, state, or country
- **Complete Email Notification System**:
  - Secure email verification with SendGrid
  - Price drop alerts when flights fall below your threshold
  - Alert activation confirmation emails
  - Alert deleted confirmation emails
  - Alert expired notifications
- **Complete SMS Notification System**:
  - Phone verification with 6-digit codes via Twilio
  - Price drop SMS alerts
  - Alert activation confirmation SMS
  - Alert deleted confirmation SMS
  - Alert expired SMS notifications
- **Flexible Alert Options**: Create alerts with email only, phone only, or both
- **Smart Notifications**: Only notifies when prices drop even lower than previous notifications
- **Automated Price Monitoring**: Background script checks prices every 6 hours
- **Unsubscribe System**: Easy one-click unsubscribe from price alerts with confirmation
- **Trip Types**: Support for both one-way and round-trip flights
- **Responsive Design**: Modern gradient theme with clean UI across all pages and emails

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL
- **APIs**:
  - Amadeus Flight Offers API (flight search and pricing)
  - SendGrid API (email notifications and verification)
  - Twilio API (SMS notifications and verification)
- **Notifications**: Email and SMS alerts with automated price monitoring

## Current Status

✅ **Email notification system is 100% complete!** Including:
- Email verification system
- Price drop notifications
- Alert activated confirmations
- Alert deleted confirmations
- Alert expired notifications

✅ **SMS notification system is 100% complete!** Including:
- Phone verification with 6-digit codes
- Price drop SMS alerts
- Alert activated confirmations
- Alert deleted confirmations
- Alert expired SMS notifications

✅ **Automated price checker running every 6 hours**

## TODO / Priorities

### High Priority
- [ ] **Update alerts page layout** (make email/phone both optional instead of one required)

### Medium Priority
- [ ] Improve error handling and user feedback
- [ ] Update button color scheme across the site

### Low Priority
- [ ] Code readability improvements and refactoring

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/Flight-Price-Tracker.git
cd Flight-Price-Tracker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Amadeus API
- Create a free account at https://developers.amadeus.com/register
- Create a new app in your Amadeus dashboard
- Get your API Key and API Secret (use Test environment)

### 4. Set up SendGrid API
- Create a free account at https://sendgrid.com
- Verify a sender email address in SendGrid settings
- Create an API key with full Mail Send permissions

### 5. Set up Twilio API
- Create a free account at https://www.twilio.com/try-twilio
- Get your Account SID and Auth Token from the Twilio console
- Get a Twilio phone number (free with trial account)
- **Important**: For trial accounts, verify your phone number in Twilio console to receive SMS

### 6. Set up MySQL Database
- Install MySQL if not already installed
- Create a database named `flight_tracker`
- Run the database initialization:
  ```bash
  python flight_price_tracker/src/core/db.py
  ```

### 7. Configure Environment Variables
Create a `.env` file in `flight_price_tracker/` directory:
```env
# Amadeus API
AMADEUS_API_KEY=your_api_key_here
AMADEUS_API_SECRET=your_api_secret_here

# SendGrid Email
SENDGRID_API_KEY=your_sendgrid_api_key
SENDER_EMAIL=your_verified_email@example.com
BASE_URL=http://localhost:5000

# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=flight_tracker

# Twilio SMS
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number

# Flask
FLASK_SECRET_KEY=your_secret_key_here
```

### 8. macOS Users Only
Install SSL certificates for Python:
```bash
/Applications/Python\ 3.12/Install\ Certificates.command
```
(Adjust Python version to match your installation)

### 9. Run the application
```bash
python flight_price_tracker/src/web/app.py
```

### 10. Run the price checker (for automated notifications)
In a separate terminal:
```bash
python flight_price_tracker/src/core/price_checker.py
```

### 11. Navigate to the app
Open your browser and go to `http://localhost:5000`

## How It Works

1. **User creates a price alert** on the `/alerts` page with email, phone, or both
2. **System sends verification**:
   - Email: Unique verification link via SendGrid
   - Phone: 6-digit code via Twilio SMS
3. **User verifies** their contact method(s) to activate the alert
4. **Price checker script runs** every 6 hours checking all active alerts
5. **When price drops below threshold**:
   - System sends email and/or SMS notification with flight details
   - Updates threshold to new lower price (only notifies on further drops)
6. **Alert auto-deletes** when departure date passes (with notification)
7. **User can unsubscribe** anytime via link in notifications

## Important Notes

### ⚠️ Gmail Delivery Issue
**IMPORTANT**: Emails sent to Gmail addresses currently do not work because the app does not have a custom domain. Gmail's spam filters block emails from non-domain senders via SendGrid.

**Workarounds for testing**:
- Use a non-Gmail email address (Yahoo, Outlook, etc.)
- Check SendGrid activity logs to confirm emails are being sent
- Production deployment with a custom domain will resolve this issue

### ⚠️ Twilio Trial Account Limitations
**IMPORTANT**: SMS notifications are currently limited due to using a free Twilio trial account:
- **Message length restrictions**: Long messages are truncated or fail to send
- **Verified numbers only**: Trial accounts can only send SMS to phone numbers verified in the Twilio console
- **Current implementation**: SMS alerts are shortened to work within trial limits (no detailed flight info or full URLs)
- **Temporary solution**: Full SMS functionality with links and detailed information will be available after upgrading Twilio account or deploying to production with a domain

**For full SMS functionality**, either:
- Upgrade your Twilio account (usually comes with free credit)
- Deploy to production with a custom domain and upgraded account

### Email Verification Links
When testing locally, if clicking the verification link in the email doesn't work, try manually changing the URL from `http://localhost:5000` to `http://127.0.0.1:5000` in your browser. This resolves some browser caching issues during development.

### API Limits
- **Amadeus API**: Free Test environment provides 2,000 API calls/month with real flight data
- **SendGrid**: Free tier allows 100 emails/day
- **Twilio**: Trial account has message length limits and can only send to verified numbers

### Future Plans
- Acquire a custom domain for production deployment (needed for Gmail delivery and full SMS functionality)
- Set up a live server running 24/7 for continuous price monitoring
- Upgrade Twilio account for full SMS functionality without length restrictions

### Database Schema
The `price_alerts` table includes:
- Flight details (origin, destination, dates, trip type)
- Contact info (email, phone)
- Price threshold
- Verification status (email_verified, phone_verified)
- Verification token for security
- Timestamps (created_at, last_checked, token_created_at)

## Troubleshooting

**SSL Certificate Errors (macOS)**
- Run the certificate installation command from setup step 7

**Email not sending**
- Verify SendGrid API key is correct
- Check that sender email is verified in SendGrid dashboard
- Check Flask terminal for error messages

**Database connection errors**
- Ensure MySQL is running
- Verify credentials in `.env` file
- Check that database `flight_tracker` exists

**Verification link doesn't work**
- Try using `127.0.0.1:5000` instead of `localhost:5000`
- Hard refresh the browser (Cmd+Shift+R / Ctrl+Shift+R)

## Contributing

This is a personal project but suggestions and bug reports are welcome!

## License

MIT License - Feel free to use and modify for your own projects.
