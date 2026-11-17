from database import get_connection
import mysql.connector

def add_customer():
    print("\n--- Add New Customer ---")
    f_name = input("First Name: ")
    l_name = input("Last Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    license = input("Driver License Number: ")
    address = input("Address: ")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customer (First_Name, Last_Name, Email, Phone, Driver_License_Number, Address)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (f_name, l_name, email, phone, license, address))
        conn.commit()
        print("Customer added successfully!")
    except mysql.connector.Error as e:
        print("Error: This Email or Driver License already exists or database error!", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def view_available_cars():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.Car_ID, c.Make, c.Model, c.Year, c.License_Plate, c.Daily_Rate, b.Branch_Name
        FROM car c
        JOIN branch b ON c.Branch_ID = b.Branch_ID
        WHERE c.Status = 'Available'
    ''')
    cars = cursor.fetchall()
    
    print("\n--- Available Cars List ---")
    if not cars:
        print("No cars are currently available.")
    for car in cars:
        print(f"Car ID: {car[0]} | {car[1]} {car[2]} ({car[3]}) | Plate: {car[4]} | Rate: ${car[5]}/day | Branch: {car[6]}")
    
    cursor.close()
    conn.close()

def rent_car():
    print("\n--- Rent a Car ---")
    customer_id = input("Enter Customer ID: ")
    car_id = input("Enter Car ID to rent: ")
    rental_date = input("Rental Date (YYYY-MM-DD): ")
    return_date = input("Return Date (YYYY-MM-DD): ")
    days = int(input("Total Rental Days: "))

    conn = get_connection()
    cursor = conn.cursor()
    
    # Get daily rate to calculate total cost
    cursor.execute("SELECT Daily_Rate, Status FROM car WHERE Car_ID = %s", (car_id,))
    car = cursor.fetchone()
    
    if not car:
        print("Error: Car ID not found!")
        cursor.close()
        conn.close()
        return
    
    if car[1] != 'Available':
        print("Error: Selected car is not available for rent!")
        cursor.close()
        conn.close()
        return
        
    daily_rate = car[0]
    total_cost = float(daily_rate) * days

    try:
        # Insert rental transaction
        cursor.execute('''
            INSERT INTO rental_transaction (Car_ID, Customer_ID, Rental_Date, Return_Date, Total_Cost, Payment_Status)
            VALUES (%s, %s, %s, %s, %s, 'Paid')
        ''', (car_id, customer_id, rental_date, return_date, total_cost))
        
        # Update car status to Rented
        cursor.execute("UPDATE car SET Status = 'Rented' WHERE Car_ID = %s", (car_id,))
        
        conn.commit()
        print(f"Rental successful! Total Cost: ${total_cost}")
    except Exception as e:
        print("Error processing rental:", e)
    finally:
        cursor.close()
        conn.close()

def view_revenue_report():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            DATE_FORMAT(Rental_Date, '%Y-%m') AS Rental_Month,
            COUNT(Rental_ID) AS Total_Rentals,
            SUM(Total_Cost) AS Gross_Revenue
        FROM rental_transaction
        GROUP BY Rental_Month
        ORDER BY Rental_Month DESC
    ''')
    reports = cursor.fetchall()
    
    print("\n--- Monthly Revenue Report ---")
    if not reports:
        print("No rental transactions recorded yet.")
    for rep in reports:
        print(f"Month: {rep[0]} | Total Rentals: {rep[1]} | Gross Revenue: ${rep[2]}")
        
    cursor.close()
    conn.close()

def main_menu():
    while True:
        print("\n=== CAR RENTAL MANAGEMENT SYSTEM (MySQL) ===")
        print("1. Add Customer")
        print("2. View Available Cars")
        print("3. Rent a Car")
        print("4. View Monthly Revenue Report")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            add_customer()
        elif choice == '2':
            view_available_cars()
        elif choice == '3':
            rent_car()
        elif choice == '4':
            view_revenue_report()
        elif choice == '5':
            print("Exiting application... Goodbye!")
            break
        else:
            print("Invalid input! Please choose between 1 and 5.")

if __name__ == "__main__":
    main_menu()