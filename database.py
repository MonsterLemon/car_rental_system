import mysql.connector

def get_connection():
    """Establish and return a connection to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",          # Default XAMPP MySQL username
        password="",          # Leave empty if no password is set in XAMPP
        database="car_rental" # Your phpMyAdmin database name
    )

if __name__ == "__main__":
    # Test the database connection
    try:
        conn = get_connection()
        if conn.is_connected():
            print("Successfully connected to the MySQL database (car_rental)!")
        conn.close()
    except Exception as e:
        print("Database connection failed:", e)