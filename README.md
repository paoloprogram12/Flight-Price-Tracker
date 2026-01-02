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
  - Travelpayouts (flight data)
  - Twilio (SMS notifications)
- **Notifications**: Email and SMS alerts

## Current Status

The core functionality is implemented with a working UI for the home page and results page. The alerts system is in place but SMS requires Twilio phone verification.

## TODO / Future Enhancements

### High Priority
- [ ] Fix/replace Travelpayouts API (currently has limited/unreliable flight data, especially for round-trip searches)
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
3. Create a `.env` file with required API keys:
   - `TRAVELPAYOUTS_TOKEN`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`
   - `FLASK_SECRET_KEY`
4. Run the app: `python flight_price_tracker/src/web/app.py`
5. Navigate to `http://localhost:5000`

## Notes

- The Travelpayouts API (free tier) has spotty data coverage - some routes may not return results
- SMS alerts require a verified Twilio phone number
- One-way searches tend to work better than round-trip with the current API
