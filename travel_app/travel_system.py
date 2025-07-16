import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()
connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME")
)
cursor = connection.cursor()

class User:
    def __init__(self, username, password, balance=0):
        self.username = username
        self.password = password
        self.balance = balance

   
    def add_balance(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        self.balance += amount
        print(f"Balance updated: {self.balance}")

    def view_balance(self):
        print(f"Your current balance is: {self.balance}")


class Admin:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def manage_trips(self):
        
        print("Managing trips...")


class Trip:
    def __init__(self, trip_id, cost, start_time, end_time, active=True):
        self.trip_id = trip_id
        self.cost = cost
        self.start_time = start_time
        self.end_time = end_time
        self.active = active

    def deactivate_trip(self):
        self.active = False


class TravelSystem:
    def __init__(self):
        self.db_connection = self.connect_db()
        self.cursor = self.db_connection.cursor()
        self.setup_database()
        self.users = {}
        self.admins = {}
        self.trips = {}
    def connect_db(self):
       
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT")),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                dbname=os.getenv("DB_NAME")
            )
            print("connected ")
            return conn
        except psycopg2.Error as e:
            print(f": {e}")
            return None


    def setup_database(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                username TEXT PRIMARY KEY,
                                password TEXT NOT NULL,
                                balance REAL DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                                username TEXT PRIMARY KEY,
                                password TEXT NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS trips (
                                trip_id SERIAL PRIMARY KEY,
                                cost REAL NOT NULL,
                                start_time TEXT NOT NULL,
                                end_time TEXT NOT NULL,
                                active BOOLEAN DEFAULT TRUE)''')
        self.db_connection.commit()
        self.add_default_admin()

    def add_default_admin(self):
        try:
            self.cursor.execute("INSERT INTO admins (username, password) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING", ("admin", "admin123"))
            self.db_connection.commit()
            print("Default admin added: Username: admin, Password: admin123")
        except Exception as e:
            print(f"Error adding default admin: {e}")

    def register_user(self):
        
        username = input("Enter a username: ")
        password = input("Enter a password: ")
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            self.db_connection.commit()
            print("User registered successfully.")
        except psycopg2.IntegrityError:
            print("User already exists.")
        except Exception as e:
            print(f"Error registering user: {e}")

    def admin_login(self):
        
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        self.cursor.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
        admin = self.cursor.fetchone()
        if admin:
            print("Admin logged in.")
            Admin(username, password).manage_trips()
        else:
            print("Invalid credentials.")

    def user_login(self):
        
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        self.cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = self.cursor.fetchone()
        if user:
            user_instance = User(username, password, user[2])
            print("User logged in.")
            self.user_dashboard(user_instance)
        else:
            print("Invalid credentials.")

    def user_dashboard(self, user):
        while True:
            print("\nUser Dashboard")
            print("1. View Balance")
            print("2. Add Balance")
            print("3. Logout")
            choice = input("Choose an option: ")
            if choice == "1":
                user.view_balance()
            elif choice == "2":
                try:
                    amount = float(input("Enter amount to add: "))
                    user.add_balance(amount)
                    self.cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (user.balance, user.username))
                    self.db_connection.commit()
                except Exception:
                    print("Invalid input. Please enter a number.")
                
            elif choice == "3":
                break
            else:
                print("Invalid choice. Try again.")

    def main_menu(self):
        while True:
            print("\nTravel System Main Menu")
            print("1. Register User")
            print("2. User Login")
            print("3. Admin Login")
            print("4. Exit")
            choice = input("Choose an option: ")
            if choice == "1":
                self.register_user()
            elif choice == "2":
                self.user_login()
            elif choice == "3":
                self.admin_login()
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Try again.")

if __name__ == "__main__":
    system = TravelSystem()
    system.main_menu()
