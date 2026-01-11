# Flight-Price-Tracker

A web application to track and compare flight prices, with automated email notifications when prices drop below your target threshold.

## Features

- **Flight Search**: Search for flights by origin, destination, and dates using Amadeus API
- **Airport Autocomplete**: Search airports by code, city, state, or country
- **Email Verification**: Secure email verification system using SendGrid
- **Price Alerts**: Automated email notifications when flight prices drop below your threshold
- **Smart Notifications**: Only notifies when prices drop even lower than previous notifications
- **Unsubscribe System**: Easy one-click unsubscribe from price alerts
- **Trip Types**: Support for both one-way and round-trip flights
- **Responsive Design**: Modern gradient theme with clean UI

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL
- **APIs**:
  - Amadeus Flight Offers API (flight search and pricing)
  - SendGrid API (email notifications and verification)
  - Twilio (SMS notifications - planned)
- **Notifications**: Email alerts with automated price monitoring

## Current Status

Currently working on the automated price checker script that monitors flight prices and sends email notifications. The email verification system is fully functional.

## TODO / Priorities

### High Priority
- [ ] **Complete and test automated price checker script**
- [ ] **SMS notification integration with Twilio**
- [ ] **Test email notification system end-to-end**
- [ ] **Fix bugs in price monitoring workflow**
- [ ] **Update alerts page layout** (make email/phone both optional instead of one required)
- [ ] **Implement alert deletion notification email** (notify users when alert is deleted after flight date passes)

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

### 5. Set up MySQL Database
- Install MySQL if not already installed
- Create a database named `flight_tracker`
- Run the database initialization:
  ```bash
  python flight_price_tracker/src/core/db.py
  ```

### 6. Configure Environment Variables
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

# Twilio SMS (Optional - for future SMS notifications)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number

# Flask
FLASK_SECRET_KEY=your_secret_key_here
```

### 7. macOS Users Only
Install SSL certificates for Python:
```bash
/Applications/Python\ 3.12/Install\ Certificates.command
```
(Adjust Python version to match your installation)

### 8. Run the application
```bash
python flight_price_tracker/src/web/app.py
```

### 9. Run the price checker (optional - for automated notifications)
In a separate terminal:
```bash
python flight_price_tracker/src/core/price_checker.py
```

### 10. Navigate to the app
Open your browser and go to `http://localhost:5000`

## How It Works

1. **User creates a price alert** on the `/alerts` page with flight details and target price
2. **System sends verification email** via SendGrid with a unique verification link
3. **User clicks verification link** to activate the alert
4. **Price checker script runs** every 6 hours (configurable) checking all active alerts
5. **When price drops below threshold**:
   - System sends email notification with flight details
   - Updates threshold to new lower price (only notifies on further drops)
6. **Alert auto-deletes** when departure date passes
7. **User can unsubscribe** anytime via link in notification emails

## Important Notes

### Email Verification Links
When testing locally, if clicking the verification link in the email doesn't work, try manually changing the URL from `http://localhost:5000` to `http://127.0.0.1:5000` in your browser. This resolves some browser caching issues during development.

### API Limits
- **Amadeus API**: Free Test environment provides 2,000 API calls/month with real flight data
- **SendGrid**: Free tier allows 100 emails/day

### Future Plans
- May acquire a custom domain for production deployment
- Planning to set up a live server running 24/7 for continuous price monitoring
- SMS notifications via Twilio integration

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
