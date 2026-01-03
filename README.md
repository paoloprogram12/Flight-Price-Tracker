# Flight-Price-Tracker

A web application to track and compare flight prices, with price alert notifications.

## Features

- **Flight Search**: Search for flights by origin, destination, and dates
- **Airport Autocomplete**: Search airports by code, city, state, or country
- **Price Alerts**: Set up email and SMS notifications when prices drop
- **Trip Types**: Support for both one-way and round-trip flights
- **Responsive Design**: Dark blue theme with airplane background imagery

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **APIs**:
  - Amadeus Flight Offers API (flight search and pricing)
  - Twilio (SMS notifications)
- **Notifications**: Email and SMS alerts

## Current Status

The core functionality is implemented with a working UI for the home page and results page. The alerts system is in place but SMS requires Twilio phone verification.

## TODO / Future Enhancements

### High Priority
- [x] ~~Fix/replace Travelpayouts API~~ - **Migrated to Amadeus API (Jan 2026)**
- [ ] Verify Twilio phone number for SMS alerts
- [ ] Style the alerts page CSS

### Medium Priority
- [ ] Integrate real-time currency conversion API to display prices in USD
- [ ] Update button color scheme across the site
- [ ] Add flight filters (price range, number of stops, airlines)
- [ ] Improve error handling and user feedback

### Low Priority
- [ ] Add user accounts and saved searches
- [ ] Price history charts and trends
- [ ] Email receipt/confirmation for alerts
- [ ] Mobile app version

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. **Set up Amadeus API:**
   - Create a free account at https://developers.amadeus.com/register
   - Create a new app in your Amadeus dashboard
   - Get your API Key and API Secret (use Test environment)
4. Create a `.env` file in `flight_price_tracker/` directory with required API keys:
   ```
   AMADEUS_API_KEY=your_api_key_here
   AMADEUS_API_SECRET=your_api_secret_here
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=your_twilio_number
   FLASK_SECRET_KEY=your_secret_key
   ```
5. **macOS Users Only:** Install SSL certificates for Python:
   ```bash
   /Applications/Python\ 3.12/Install\ Certificates.command
   ```
   (Adjust Python version to match your installation)
6. Run the app: `python flight_price_tracker/src/web/app.py`
7. Navigate to `http://localhost:5000`

## Notes

- **Amadeus API**: Using the free Test environment which provides access to real flight data with a limit of 2,000 API calls/month
- **SSL Certificates**: macOS users must install Python SSL certificates (see setup step 5) to avoid connection errors
- **SMS Alerts**: Require a verified Twilio phone number
- **Currency**: All prices are displayed in USD (configurable in the API call)
