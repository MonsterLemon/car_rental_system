import sqlite3

def get_connection():
    conn = sqlite3.connect("car_rental.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Branch Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Branch (
            Branch_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Branch_Name TEXT NOT NULL,
            City TEXT NOT NULL,
            Address TEXT,
            Phone_Number TEXT
        )
    ''')
    
    # Car Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Car (
            Car_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Branch_ID INTEGER,
            Make TEXT NOT NULL,
            Model TEXT NOT NULL,
            Year INTEGER,
            License_Plate TEXT UNIQUE NOT NULL,
            Daily_Rate REAL NOT NULL,
            Status TEXT CHECK(Status IN ('Available', 'Rented', 'Maintenance')) DEFAULT 'Available',
            FOREIGN KEY (Branch_ID) REFERENCES Branch(Branch_ID)
        )
    ''')
    
    # Customer Table (with password for login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customer (
            Customer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            First_Name TEXT NOT NULL,
            Last_Name TEXT NOT NULL,
            Email TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL,
            Phone TEXT,
            Driver_License_Number TEXT UNIQUE NOT NULL,
            Address TEXT
        )
    ''')

    # Admin Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Admin (
            Admin_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL
        )
    ''')
    
    # Rental Transaction Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Rental_Transaction (
            Rental_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Car_ID INTEGER,
            Customer_ID INTEGER,
            Rental_Date TEXT NOT NULL,
            Return_Date TEXT NOT NULL,
            Total_Cost REAL,
            Payment_Status TEXT DEFAULT 'Paid',
            FOREIGN KEY (Car_ID) REFERENCES Car(Car_ID),
            FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
        )
    ''')
    
    conn.commit()
    
    # Insert Default Admin (Username: admin, Password: 123)
    cursor.execute("SELECT COUNT(*) FROM Admin")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Admin (Username, Password) VALUES ('admin', '123')")
        conn.commit()

    # Insert Sample Branch & Cars if empty
    cursor.execute("SELECT COUNT(*) FROM Branch")
    if cursor.fetchone()[0] == 0:
        cursor.executescript('''
            INSERT INTO Branch (Branch_Name, City, Address, Phone_Number) VALUES 
            ('Central Hub', 'Dhaka', 'Gulshan-2', '01711000000'),
            ('Airport Branch', 'Dhaka', 'Uttara', '01822000000');

            INSERT INTO Car (Branch_ID, Make, Model, Year, License_Plate, Daily_Rate, Status) VALUES 
            (1, 'Toyota', 'Corolla', 2022, 'DHA-11-2233', 50.0, 'Available'),
            (1, 'Honda', 'Civic', 2023, 'DHA-22-4455', 65.0, 'Available'),
            (2, 'Hyundai', 'Tucson', 2021, 'DHA-33-8899', 90.0, 'Available');
        ''')
        conn.commit()

    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully with Admin support!")