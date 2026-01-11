import os
import pymysql
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# MYSQL configuration from .env
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    """Create and returns a db connection"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise

def init_db():
    """Initialize db and create tables if they don't exist"""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # creates price_alerts table if DNE
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_alerts (
                           id INT AUTO_INCREMENT PRIMARY KEY,
                           email VARCHAR(255) NOT NULL,
                           phone VARCHAR(20),
                           origin VARCHAR(10) NOT NULL,
                           destination VARCHAR(10) NOT NULL,
                           departure_date DATE NOT NULL,
                           return_date DATE,
                           price_threshold DECIMAL(10,2) NOT NULL,
                           trip_type VARCHAR(20) NOT NULL,
                           is_active BOOLEAN DEFAULT TRUE,
                           email_verified BOOLEAN DEFAULT FALSE,
                           phone_verified BOOLEAN DEFAULT FALSE,
                           verification_token VARCHAR(255),
                           token_created_at TIMESTAMP NULL,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           last_checked TIMESTAMP NULL
                            )
                        """)
            connection.commit()
            print("Database initialized successfully.")
    except pymysql.Error as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        connection.close()

def create_alert(phone, origin, destination, departure_date, return_date, price_threshold, trip_type, email=None, verification_token=None):
    """
      Create a new price alert.
      
      Args:
          phone: User's phone number (E.164 format, e.g., +15551234567)
          origin: Origin airport code (e.g., "LAX")
          destination: Destination airport code (e.g., "TYO")
          departure_date: Departure date (YYYY-MM-DD)
          return_date: Return date (YYYY-MM-DD) or None for one-way
          price_threshold: Maximum price user wants to pay
          trip_type: "one-way" or "round-trip"
          email: Optional email address
      
      Returns:
          The ID of the created alert
      """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO price_alerts
                (phone, email, origin, destination, departure_date, return_date,
                price_threshold, trip_type, is_active, verification_token, token_created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (phone, email, origin, destination, departure_date, return_date,
                                price_threshold, trip_type, True, verification_token, datetime.now() if verification_token else None))
            connection.commit()
            return cursor.lastrowid
    except pymysql.Error as e:
        print(f"Error creating alert: {e}")
        raise
    finally:
        connection.close()

def get_active_alerts():
    """Get all active price alerts."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM price_alerts
                WHERE is_active = TRUE
                ORDER BY created_at DESC
            """)
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching alerts: {e}")
        raise
    finally:
        connection.close()

def update_last_checked(alert_id):
    """Update the last chekced timestamp for an alert."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE price_alerts
                SET last_checked = %s
                WHERE id = %s
            """, (datetime.now(), alert_id))
            connection.commit()
    except pymysql.Error as e:
        print(f"Error updating last_checked: {e}")
        raise
    finally:
        connection.close()

def deactivate_alert(alert_id):
      """Deactivate an alert (set is_active to False)."""
      connection = get_connection()
      try:
          with connection.cursor() as cursor:
              cursor.execute("""
                  UPDATE price_alerts 
                  SET is_active = FALSE 
                  WHERE id = %s
              """, (alert_id,))
              connection.commit()
      except pymysql.Error as e:
          print(f"Error deactivating alert: {e}")
          raise
      finally:
          connection.close()

def get_alert_by_id(alert_id):
      """Get a specific alert by ID."""
      connection = get_connection()
      try:
          with connection.cursor() as cursor:
              cursor.execute("""
                  SELECT * FROM price_alerts 
                  WHERE id = %s
              """, (alert_id,))
              return cursor.fetchone()
      except pymysql.Error as e:
          print(f"Error fetching alert: {e}")
          raise
      finally:
          connection.close()

# tokens are used to store a specific alert
# email verified sets email_verified=TRUE for alert
# tokens are used for security and uniqueness
def verify_email_token(token):
    """
    Verify an email using the verification token.
    
    Args:
        token: The verification token from the email link

    Returns: True if verification successful, False otherwise
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Find alert with this token
            cursor.execute("""
                SELECT id FROM price_alerts
                WHERE verification_token = %s
                AND email_verified = FALSE
            """, (token,))

            alert = cursor.fetchone()
            if not alert:
                return False
            
            # Mark email as verified
            cursor.execute("""
                UPDATE price_alerts
                SET email_verified = TRUE
                WHERE id = %s
            """, (alert['id'],))

            connection.commit()
            return True
    except pymysql.Error as e:
        print(f"Error verifying email token: {e}")
        return False
    finally:
        connection.close()

# initialize db when module is imported
if __name__ == "__main__":
    init_db()
    print("Database setup is completed.")


# 1. get_connection() - Creates a connection to your MySQL database using credentials from .env
#   2. init_db() - Creates the price_alerts table if it doesn't exist
#   3. create_alert() - Saves a new price alert to the database
#   4. get_active_alerts() - Retrieves all active alerts (for the background checker)
#   5. update_last_checked() - Updates when an alert was last checked
#   6. deactivate_alert() - Turns off an alert
#   7. get_alert_by_id() - Gets a specific alert by ID