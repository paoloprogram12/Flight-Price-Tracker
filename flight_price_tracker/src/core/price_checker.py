import time
import schedule
from datetime import datetime, date
from db import get_connection, update_last_checked, delete_alert, update_price_threshold
from email import send_price_drop_notification
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.api.travelpayouts import prices_for_dates

def get_verified_active_alerts():
    """Get all active alerts that have verified emails."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM price_alerts
                WHERE is_active = TRUE
                AND email_verified = TRUE
                ORDER BY created_at ASC
            """)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        return []
    finally:
        connection.close()

def check_prices_for_alert(alert):
    """Check if current prices are below threshold for a specific alert."""
    try:
        # Check if departure date has passed
        departure_date = alert['departure_date']
        if isinstance(departure_date, str):
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()

        if departure_date < date.today():
            print(f"Alert ID {alert['id']} departure date passed. Deleting alert.")
            delete_alert(alert['id'])
            return
        
        print(f"Checking alert ID {alert['id']}: {alert['origin']} -> {alert['destination']}")

        # determine if one-way
        one_way = (alert['trip_type'] == 'one-way')

        # call amadeus api to get current prices
        flights = prices_for_dates(
            origin=alert['origin'],
            destination=alert['destination'],
            departure_date=str(alert['departure_date']),
            return_date=str(alert['return_date']) if not one_way and alert['return_date'] else None,
            limit=10
        )

        # check if any flights are below the threshold
        for flight in flights:
            if flight['price'] < alert['price_threshold']:
                print(f"Price drop found! ${flight['price']} <= ${alert['price_threshold']}")

                # send notification email
                alert_details = {
                    'alert_id': alert['id'],
                    'origin': alert['origin'],
                    'destination': alert['destination'],
                    'departure_date': str(alert['departure_date']),
                    'return_date': str(alert['return_date']) if alert['return_date'] else None,
                    'price_threshold': float(alert['price_threshold']),
                    'trip_type': alert['trip_type']
                }

                flight_details = {
                    'price': flight['price'],
                    'airline': flight.get('airline', 'Unknown')
                }

                # send the notification
                if send_price_drop_notification(alert['email'], alert_details, flight_details):
                    print (f"Notification sent to {alert['email']}")

                    # update the price threshold to the new lower price
                    from db import update_price_threshold
                    update_price_threshold(alert['id'], flight['price'])
                    print(f"Price threshold updated to ${flight['price']}")
                else:
                    print(f"Failed to send notification to {alert['email']}")

                # only send one notification per alert check
                break
        else:
            print(f"No prices below ${alert['price_threshold']} found")
            # update last checked timestamp
            update_last_checked(['id'])

    except Exception as e:
        print(f"Error checking prices for alert {alert['id']}: {e}")

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
        time.sleep(2) # wait 2 sec between api calls to avoid rate limiting
    
    print(f"\n{'='*50}")
    print(f"Price check completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

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
        time.sleep(60) # check every minute if a scheduled task needs to run

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\n\n Price checker stopped by user")