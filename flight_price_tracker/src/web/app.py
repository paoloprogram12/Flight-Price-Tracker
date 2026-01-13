from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import sys
import os
import json

load_dotenv()

# load airport data at startup
base_dir = os.path.dirname(os.path.abspath(__file__))
airports_path = os.path.join(base_dir, 'static', 'airports.json')
airlines_path = os.path.join(base_dir, 'static', 'airlines.json')

with open(airports_path) as f:
    # airports
    airports_data = json.load(f)
    airports = {a['code']: a for a in airports_data}

with open(airlines_path) as f:
    airlines_data = json.load(f)
    airlines = {a['code']: a for a in airlines_data}

# add parent directory to path to import from src.core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) # shows where to find db.py

from src.core.db import create_alert, get_active_alerts
from src.core.email_service import generate_verification_token, send_verification_email

# creates app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-dev-key')

# home page
@app.route('/')
def home():
    return render_template('index.html')

# handle flight search
@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        # import API function
        from src.api.travelpayouts import prices_for_dates

        # get form data (email first)
        if request.method == 'GET':
            origin = request.args.get('origin').upper()
            destination = request.args.get('destination').upper()
            departure_date = request.args.get('departure_date')
            return_date = request.args.get('return_date')
            trip_type = request.args.get('trip_type')
            adults = int(request.args.get('adults', 1))
            children = int(request.args.get('children', 0))
            infant = int(request.args.get('infant', 0))
        else:
            origin = request.form.get('origin').upper()
            destination = request.form.get('destination').upper()
            departure_date = request.form.get('departure_date')
            return_date = request.form.get('return_date')
            trip_type = request.form.get('trip_type')
            adults = int(request.form.get('adults', 1))
            children = int(request.form.get('children', 0))
            infant = int(request.form.get('infant', 0))

        # determine if it's one way
        one_way = (trip_type == 'one-way')

        # calls the Travelpayouts API
        flights = prices_for_dates(
            origin=origin,
            destination=destination,
            departure_at=departure_date,
            return_at=return_date if not one_way else None,
            one_way=one_way,
            limit=10,
            adults=adults,
            children=children,
            infants=infant
        )

        # assign cities and airline info
        for flight in flights:
            flight['origin_city'] = airports.get(flight['origin'], {}).get('city', flight['origin'])
            flight['destination_city'] = airports.get(flight['destination'], {}).get('city', flight['destination'])
            flight['origin_country'] = airports.get(flight['origin'], {}).get('country', flight['origin'])
            flight['destination_country'] = airports.get(flight['destination'], {}).get('country', flight['destination'])

            airline_info = airlines.get(flight['airline'], {})
            flight['airline_name'] = airline_info.get('name', flight['airline'])
            flight['airline_img'] = airline_info.get('img', None)

            # return airline info
            if flight.get('return_airline'):
                return_airline_info = airlines.get(flight['return_airline'], {})
                flight['return_airline_name'] = return_airline_info.get('name', flight['return_airline'])
                flight['return_airline_img'] = return_airline_info.get('img', None)


        # calculate total passengers
        total_passengers = adults + children + infant

        # Look up city names for the search summary
        origin_city = airports.get(origin, {}).get('city', origin)
        origin_country = airports.get(origin, {}).get('country', '')
        destination_city = airports.get(destination, {}).get('city', destination)
        destination_country = airports.get(destination, {}).get('country', '')

        # pass data to the template
        return render_template('results.html',
                               flights=flights,
                               origin=origin,
                               destination=destination,
                               origin_city=origin_city,
                               origin_country=origin_country,
                               destination_city=destination_city,
                               destination_country=destination_country,
                               departure_date=departure_date,
                               return_date=return_date,
                               trip_type=trip_type,
                               total_passengers=total_passengers)
    except Exception as e:
        flash(f'Error searching flights: {str(e)}', 'error')
        return redirect(url_for('home'))


# display alerts signup form
@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

# handle alert form submission
@app.route('/alerts/create', methods=['POST'])
def create_alert_route():
    try:
        print("DEBUG: Form submitted")
        phone = request.form.get('phone') or None  # Convert empty string to None
        email = request.form.get('email')
        print(f"DEBUG: Email = {email}, Phone = {phone}")
        origin = request.form.get('origin').upper()
        destination = request.form.get('destination').upper()
        departure_date = request.form.get('departure_date')
        return_date = request.form.get('return_date')
        price_threshold = float(request.form.get('price_threshold'))
        trip_type = request.form.get('trip_type')

        # if one-way, return date is none
        if trip_type == 'one-way':
            return_date = None

        # validate phone number format (basic check) - only if phone is provided
        if phone and not phone.startswith('+'):
            flash('Phone number must include country code (e.g., +15551234567)', 'error')
            return redirect(url_for('alerts'))

        # Generate verification token
        print("DEBUG: Generating token")
        verification_token = generate_verification_token()
        print(f"DEBUG: Token = {verification_token}")

        # Save to database
        print("DEBUG: Saving to database")
        alert_id = create_alert(
            phone=phone,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            price_threshold=price_threshold,
            trip_type=trip_type,
            email=email,
            verification_token=verification_token
        )
        print(f"DEBUG: Alert created with ID = {alert_id}")

        # send verification mail
        alert_details = {
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'return_date': return_date,
            'price_threshold': price_threshold,
            'trip_type': trip_type
        }

        print("DEBUG: Sending verification email")
        if send_verification_email(email, verification_token, alert_details):
            print("DEBUG: Email sent successfully")
            flash(f"Verification email sent to {email}. Please check your inbox to activate your alert.", 'success')
        else:
            print("DEBUG: Email failed to send")
            flash(f"Alert created bbut failed to send verification email. Please contact support.", 'warning')

        return redirect(url_for('alerts'))

    except Exception as e:
        print(f"DEBUG: Exception caught: {e}")
        flash(f'Error creating alert: {str(e)}', 'error')
        return redirect(url_for('alerts'))
    
# handles email verification
@app.route('/verify-email')
def verify_email():
    print("DEBUG: Verify email route hit")
    token = request.args.get('token')
    print(f"DEBUG: Token received = {token}")

    if not token:
        print("DEBUG: No token provided")
        flash('Invalid verification link.', 'error')
        return redirect(url_for('home'))

    # Import verify function
    from src.core.db import verify_email_token, get_alert_by_id, get_connection # checks if token is valid
    from src.core.email_service import send_alert_activated_notification

    print("DEBUG: Calling verify_email_token")
    result = verify_email_token(token)
    print(f"DEBUG: verify_email_token returned {result}")

    if result:
        print("DEBUG: Verification successful")
        print("DEBUG: About to fetch alert with token")

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM price_alerts WHERE verification_token = %s", (token,))
        alert = cursor.fetchone()
        alert_id = alert['id']
        connection.close()

        print(f"DEBUG: Found alert_id = {alert_id}")

        alert = get_alert_by_id(alert_id)

        alert_details = {
            'alert_id': alert_id,
            'origin': alert['origin'],
            'destination': alert['destination'],
            'departure_date': str(alert['departure_date']),
            'return_date': str(alert['return_date']) if alert['return_date'] else None,
            'price_threshold': float(alert['price_threshold']),
            'trip_type': alert['trip_type'],
        }

        user_email = alert['email']

        print(f"DEBUG: Alert details = {alert_details}")
        print(f"DEBUG: Sending activation email to {user_email}")

        send_alert_activated_notification(user_email, alert_details)

        print("DEBUG: After sending activation email")

        flash('Email verified successfully! Your price alert is now active.', 'success')
    else:
        print("DEBUG: Verification failed")
        flash('Invalid or expired verification link.', 'error')

    print("DEBUG: Redirecting to alerts")
    if result:
        return render_template('email_verified.html')
    else:
        return redirect(url_for('alerts'))
    
# handle unsubscribe from alerts
@app.route('/unsubscribe')
def unsubscribe():
    alert_id = request.args.get('alert_id')

    if not alert_id:
        flash('Invalid unsubscribe link.', 'error')
        return redirect(url_for('home'))
    
    # import deactivate function
    from src.core.db import delete_alert, get_alert_by_id
    from src.core.email_service import send_deleted_alert_notification

    try:
        alert = get_alert_by_id(alert_id)

        alert_details = {
            'origin': alert['origin'],
            'destination': alert['destination'],
            'departure_date': str(alert['departure_date']),
            'return_date': str(alert['return_date']) if alert['return_date'] else None,
            'price_threshold': float(alert['price_threshold']),
            'trip_type': alert['trip_type'],
        }

        user = alert['email']
        send_deleted_alert_notification(user, alert_details)
        delete_alert(alert_id)

        return render_template('unsubscribe.html')
    except Exception as e:
        print(f"Error unsubscribing: {e}")
        flash('Error unsubscribing from alert.', 'error')
        return redirect(url_for('home'))

# TEMPORARY TESTING
@app.route('/test-verified')
def test_verified():
    return render_template('email_verified.html')
@app.route('/test-unsubscribe')
def test_unsubscribe():
    return render_template('unsubscribe.html')

# runs the app
if __name__ == '__main__':
    app.run(debug=True, port=5000)