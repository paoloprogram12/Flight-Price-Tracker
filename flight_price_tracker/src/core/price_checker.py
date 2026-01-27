import sys
import os
import time
import schedule
from datetime import datetime, date

# ──────────────────────────────────────────────────────────────
# Module Imports
# Local imports from the core package (db, email, sms) and
# the Travelpayouts API wrapper.
# ──────────────────────────────────────────────────────────────

from db import get_connection, update_last_checked, delete_alert, update_price_threshold
from email_service import send_price_drop_notification, send_alert_expired_notification
from sms_service import send_price_drop_sms, send_alert_expired_sms

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.api.travelpayouts import prices_for_dates


# ──────────────────────────────────────────────────────────────
# Alert Fetching
# ──────────────────────────────────────────────────────────────


# Queries the database for alerts that are both active AND have
# at least one verified contact method (email or phone).
# Unverified alerts are ignored so we never send notifications
# to addresses/numbers the user hasn't confirmed.
def get_verified_active_alerts():
    """Get all active alerts that have verified emails."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Only fetch alerts where at least one contact method is verified
            cursor.execute("""
                SELECT * FROM price_alerts
                WHERE is_active = TRUE
                AND (email_verified = TRUE OR phone_verified = TRUE)
                ORDER BY created_at ASC
            """)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        return []
    finally:
        connection.close()


# ──────────────────────────────────────────────────────────────
# Price Checking Logic
# ──────────────────────────────────────────────────────────────


# The core function that processes a single alert:
#   1. Checks if the departure date has already passed — if so,
#      sends an expiration notice and deletes the alert.
#   2. Otherwise, calls the Travelpayouts API for current prices.
#   3. If any flight is below the user's threshold, sends a
#      price-drop notification (email and/or SMS) and lowers
#      the threshold to the new price so repeated notifications
#      only fire on further drops.
def check_prices_for_alert(alert):
    """Check if current prices are below threshold for a specific alert."""
    try:
        # ── Step 1: Check if departure date has passed ────────

        # Check if departure date has passed
        departure_date = alert['departure_date']
        # The date may come back as a string or a date object depending
        # on the MySQL driver, so normalise it to a date object.
        if isinstance(departure_date, str):
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()

        if departure_date < date.today():
            print(f"Alert ID {alert['id']} departure date passed. Deleting alert.")

            # send expired notification
            alert_details = {
                'origin': alert['origin'],
                'destination': alert['destination'],
                'departure_date': str(alert['destination']),
                'return_date': str(alert['return_date']) if alert['return_date'] else None,
                'price_threshold': float(alert['price_threshold']),
                'trip_type': alert['trip_type'],
            }

            # for email
            if alert['email']:
                send_alert_expired_notification(alert['email'], alert_details)

            # for phone
            if alert['phone']:
                send_alert_expired_sms(alert['phone'], alert_details)

            # Remove the alert entirely since it's no longer relevant
            delete_alert(alert['id'])
            return

        # ── Step 2: Fetch current prices from the API ─────────

        print(f"Checking alert ID {alert['id']}: {alert['origin']} -> {alert['destination']}")

        # determine if one-way
        one_way = (alert['trip_type'] == 'one-way')

        # call amadeus api to get current prices
        flights = prices_for_dates(
            origin=alert['origin'],
            destination=alert['destination'],
            departure_at=str(alert['departure_date']),
            return_at=str(alert['return_date']) if not one_way and alert['return_date'] else None,
            one_way=one_way,
            limit=10,
        )

        # ── Step 3: Compare prices against the threshold ──────

        # check if any flights are below the threshold
        for flight in flights:
            if flight['price'] < alert['price_threshold']:
                print(f"Price drop found! ${flight['price']} <= ${alert['price_threshold']}")

                # Build alert and flight detail dicts for the notification templates
                # send notification email
                alert_details = {
                    'alert_id': alert['id'],
                    'origin': alert['origin'],
                    'destination': alert['destination'],
                    'departure_date': str(alert['departure_date']),
                    'return_date': str(alert['return_date']) if alert['return_date'] else None,
                    'price_threshold': float(alert['price_threshold']),
                    'trip_type': alert['trip_type'],
                }

                flight_details = {
                    'price': flight['price'],
                    'airline': flight.get('airline', 'Unknown'),
                }

                # Send email notification if email exists and is verified
                if alert['email'] and alert['email_verified']:
                    if send_price_drop_notification(alert['email'], alert_details, flight_details):
                        print(f"Email notification sent to {alert['email']}")
                    else:
                        print(f"Failed to send email to {alert['email']}")

                # Send SMS if phone exists and is verified
                if alert['phone'] and alert['phone_verified']:
                    if send_price_drop_sms(alert['phone'], alert_details, flight_details):
                        print(f"SMS notification sent to {alert['phone']}")
                    else:
                        print(f"Failed to send SMS to {alert['phone']}")

                # update the price threshold to the new lower price
                # This way the user only gets notified again if the
                # price drops even further.
                update_price_threshold(alert['id'], flight['price'])
                print(f"Price threshold updated to ${flight['price']}")

                # only send one notification per alert check
                break
        else:
            # This else belongs to the for-loop — it runs only when
            # no flight triggered a break (i.e., no price drop found).
            print(f"No prices below ${alert['price_threshold']} found")
            # update last checked timestamp
            update_last_checked(['id'])

    except Exception as e:
        print(f"Error checking prices for alert {alert['id']}: {e}")


# ──────────────────────────────────────────────────────────────
# Main Check Loop
# Iterates over every verified alert and checks prices for
# each one, with a short delay between API calls.
# ──────────────────────────────────────────────────────────────


# Runs a single pass over all verified alerts.
# Called both on startup and on the recurring schedule.
# Prints a timestamped header/footer so you can see each
# run in the console output.
def check_all_alerts():
    """Main function to check all active alerts."""
    print(f"\n{'='*50}")
    print(f"Price Check Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    alerts = get_verified_active_alerts()
    print(f"Found {len(alerts)} active verified alerts\n")

    if not alerts:
        print("No alerts to check")
        return

    for alert in alerts:
        check_prices_for_alert(alert)
        time.sleep(2)  # wait 2 sec between api calls to avoid rate limiting

    print(f"\n{'='*50}")
    print(f"Price check completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")


# ──────────────────────────────────────────────────────────────
# Scheduler
# Uses the `schedule` library to run check_all_alerts() on a
# fixed interval. The while-loop keeps the process alive and
# polls every 60 seconds for pending jobs.
# ──────────────────────────────────────────────────────────────


# Sets up the recurring schedule and kicks off the first run
# immediately. This function blocks forever (until Ctrl+C).
def run_scheduler():
    """Run the price checker on a schedule."""
    # Schedule the job to run every 6 hours
    schedule.every(6).hours.do(check_all_alerts)

    # Also run immediately on startuo
    check_all_alerts()

    print("\nPrice checker is running...")
    print("Checking prices every 6 hours")
    print("Press Ctrl+C to stop\n")

    # keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # check every minute if a scheduled task needs to run


# ──────────────────────────────────────────────────────────────
# Entry Point
# Run this file directly (python price_checker.py) to start
# the background price checker. It will run immediately and
# then repeat every 6 hours until stopped with Ctrl+C.
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\n\n Price checker stopped by user")


# ──────────────────────────────────────────────────────────────
# Function Reference
#   1. get_verified_active_alerts() - Fetches all active alerts with at least one verified contact
#   2. check_prices_for_alert()     - Checks a single alert: expires it or sends price-drop notices
#   3. check_all_alerts()           - Loops through every alert and checks prices (one full pass)
#   4. run_scheduler()              - Starts the recurring 6-hour schedule and blocks forever
# ──────────────────────────────────────────────────────────────
