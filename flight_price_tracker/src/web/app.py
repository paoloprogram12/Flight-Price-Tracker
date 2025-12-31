from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import sys
import os

load_dotenv()

# add parent directory to path to import from src.core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) # shows where to find db.py

from src.core.db import create_alert, get_active_alerts

# creates app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-dev-key')

# home page
@app.route('/')
def home():
    return render_template('index.html')

# display alerts signup form
@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

# handle alert form submission
@app.route('/alerts/create', methods=['POST'])
def create_alert_route():
    try:
        phone = request.form.get('phone')
        email = request.form.get('email')
        origin = request.form.get('origin').upper()
        destination = request.form.get('destination').upper()
        departure_date = request.form.get('departure_date')
        return_date = request.form.get('return_date')
        price_threshold = float(request.form.get('price_threshold'))
        trip_type = request.form.get('trip_type')

        # if one-way, return date is none
        if trip_type == 'one-way':
            return_date = None

        # validate phone number format (basic check)
        if not phone.startswith('+'):
            flash('Phone number must include country code (e.g., +15551234567)', 'error')
            return redirect(url_for('alerts'))
        
        # Save to database
        alert_id = create_alert(
            phone=phone,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            price_threshold=price_threshold,
            trip_type=trip_type,
            email=email
        )

        flash(f'Price alert created successfully. We\'ll notify you at {phone} when prices drop below ${price_threshold}', 'success')
        return redirect(url_for('alerts'))
    
    except Exception as e:
        flash(f'Error creating alert: {str(e)}', 'error')
        return redirect(url_for('alerts'))

# runs the app
if __name__ == '__main__':
    app.run(debug=True, port=5000)