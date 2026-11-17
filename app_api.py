from flask import Flask, jsonify, request, render_template
import sqlite3
from database import create_tables

app = Flask(__name__)
DB_NAME = "car_rental.db"

# অ্যাপ স্টার্ট হওয়ার সাথে সাথে ডেটাবেজ ও টেবিল তৈরি বা আপডেট নিশ্চিত করা
create_tables()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

# --- 1. AUTHENTICATION (Login & Sign Up) ---

@app.route('/api/login/admin', methods=['POST'])
def admin_login():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Admin WHERE Username = ? AND Password = ?", (data.get('username'), data.get('password')))
    admin = cursor.fetchone()
    conn.close()
    if admin:
        return jsonify({"status": "success", "message": "Admin login successful"})
    return jsonify({"status": "error", "message": "Invalid admin credentials"}), 401

@app.route('/api/login/customer', methods=['POST'])
def customer_login():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customer WHERE Email = ? AND Password = ?", (data.get('email'), data.get('password')))
    customer = cursor.fetchone()
    conn.close()
    if customer:
        return jsonify({"status": "success", "customer_id": customer["Customer_ID"], "name": customer["First_Name"]})
    return jsonify({"status": "error", "message": "Invalid email or password"}), 401

@app.route('/api/signup/customer', methods=['POST'])
def customer_signup():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Customer (First_Name, Last_Name, Email, Password, Phone, Driver_License_Number, Address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['first_name'], data['last_name'], data['email'], data['password'], data['phone'], data['license'], data['address']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Customer registered successfully!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# --- 2. ADMIN FEATURES (Add Car, Price Update, Inventory) ---

@app.route('/api/admin/cars', methods=['POST'])
def add_car():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Car (Branch_ID, Make, Model, Year, License_Plate, Daily_Rate, Status)
            VALUES (?, ?, ?, ?, ?, ?, 'Available')
        ''', (data['branch_id'], data['make'], data['model'], data['year'], data['license_plate'], data['daily_rate']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Car added successfully!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/admin/cars/price', methods=['PUT'])
def update_car_price():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Car SET Daily_Rate = ? WHERE Car_ID = ?", (data['new_rate'], data['car_id']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Car price updated successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/admin/cars/all', methods=['GET'])
def get_all_cars_admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.Car_ID, c.Make, c.Model, c.Year, c.License_Plate, c.Daily_Rate, c.Status, b.Branch_Name
        FROM Car c
        JOIN Branch b ON c.Branch_ID = b.Branch_ID
    ''')
    cars = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(cars)

# --- 3. CUSTOMER & GENERAL FEATURES ---

@app.route('/api/cars/available', methods=['GET'])
def get_available_cars():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.Car_ID, c.Make, c.Model, c.Year, c.License_Plate, c.Daily_Rate, b.Branch_Name
        FROM Car c
        JOIN Branch b ON c.Branch_ID = b.Branch_ID
        WHERE c.Status = 'Available'
    ''')
    cars = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(cars)

@app.route('/api/rentals', methods=['POST'])
def rent_car():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT Daily_Rate, Status FROM Car WHERE Car_ID = ?", (data['car_id'],))
        car = cursor.fetchone()
        
        if not car or car['Status'] != 'Available':
            conn.close()
            return jsonify({"status": "error", "message": "Car not available!"}), 400
            
        total_cost = car['Daily_Rate'] * int(data['days'])

        cursor.execute('''
            INSERT INTO Rental_Transaction (Car_ID, Customer_ID, Rental_Date, Return_Date, Total_Cost, Payment_Status)
            VALUES (?, ?, ?, ?, ?, 'Paid')
        ''', (data['car_id'], data['customer_id'], data['rental_date'], data['return_date'], total_cost))
        
        cursor.execute("UPDATE Car SET Status = 'Rented' WHERE Car_ID = ?", (data['car_id'],))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "total_cost": total_cost}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reports/revenue', methods=['GET'])
def revenue_report():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            strftime('%Y-%m', Rental_Date) AS Rental_Month,
            COUNT(Rental_ID) AS Total_Rentals,
            SUM(Total_Cost) AS Gross_Revenue
        FROM Rental_Transaction
        GROUP BY Rental_Month
        ORDER BY Rental_Month DESC
    ''')
    reports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(reports)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    
# Admin: Manual Car Status Update (Available <-> Rented)
@app.route('/api/admin/cars/status', methods=['PUT'])
def update_car_status():
    data = request.json
    car_id = data.get('car_id')
    new_status = data.get('status') # 'Available', 'Rented', etc.
    
    if new_status not in ['Available', 'Rented', 'Maintenance']:
        return jsonify({"status": "error", "message": "Invalid status value!"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Car SET Status = ? WHERE Car_ID = ?", (new_status, car_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"Car ID {car_id} status updated to {new_status} successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400