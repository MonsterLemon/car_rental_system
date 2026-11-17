from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)
DB_NAME = "car_rental.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')
# 1. Get All Available Cars
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

# 2. Add New Customer
@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Customer (First_Name, Last_Name, Email, Phone, Driver_License_Number, Address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['first_name'], data['last_name'], data['email'], data['phone'], data['license'], data['address']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Customer added successfully!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# 3. Rent a Car
@app.route('/api/rentals', methods=['POST'])
def rent_car():
    data = request.json
    car_id = data['car_id']
    customer_id = data['customer_id']
    rental_date = data['rental_date']
    return_date = data['return_date']
    days = int(data['days'])

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT Daily_Rate, Status FROM Car WHERE Car_ID = ?", (car_id,))
    car = cursor.fetchone()
    
    if not car or car['Status'] != 'Available':
        conn.close()
        return jsonify({"status": "error", "message": "Car not available or found!"}), 400
        
    total_cost = car['Daily_Rate'] * days

    try:
        cursor.execute('''
            INSERT INTO Rental_Transaction (Car_ID, Customer_ID, Rental_Date, Return_Date, Total_Cost, Payment_Status)
            VALUES (?, ?, ?, ?, ?, 'Paid')
        ''', (car_id, customer_id, rental_date, return_date, total_cost))
        
        cursor.execute("UPDATE Car SET Status = 'Rented' WHERE Car_ID = ?", (car_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "total_cost": total_cost}), 201
    except Exception as e:
        conn.close()
        return jsonify({"status": "error", "message": str(e)}), 500

# 4. Monthly Revenue Report
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