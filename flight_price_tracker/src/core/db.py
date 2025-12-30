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
            