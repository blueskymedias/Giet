from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import sql 
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Database connection configuration
DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = '1616'

# Function to get a database connection
def get_db_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return connection

# Create the 'users_tables' table if it doesn't exist
def create_app_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app (
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            job TEXT NOT NULL   
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()

create_app_table_if_not_exists()

bcrypt = Bcrypt()

def encode_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(hashed_password,password):
    return bcrypt.check_password_hash(hashed_password,password)

@app.route('/sign_up', methods=['POST'])
def sign_up():
    
        username = request.json['username']
        password = request.json['password']
        job = request.json['job']

        # Hash the password
        hashed_password = encode_password(password)

        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert user data into the database
        cursor.execute("""
            INSERT INTO app (username, password, job) 
            VALUES (%s, %s, %s);
        """, (username, hashed_password, job))
        connection.commit()
        cursor.close()
        connection.close()

        
@app.route("/login_user", methods=['GET'])
def login_user():
    username = request.json.get('username')  # Get username from JSON body
    password = request.json.get('password')  # Get plain-text password from JSON body

    # Establish a database connection
    connection = get_db_connection()
    cursor = connection.cursor()

    # Query to fetch username, hashed password, and job for the provided username
    query = "SELECT username, password, job FROM app WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()  # Fetch the first matching record
    cursor.close()
    connection.close()

    # Check if the user exists and validate the password
    if result:
        stored_username, stored_hashed_password, job = result  # Extract data from the query result

        # Use bcrypt to validate the plain-text password against the stored hashed password
        if check_password(stored_hashed_password, password):
            response = {
                "username": stored_username,
                "job": job,
                "message": "Login successful"
            }
            return jsonify(response), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    else:
        return jsonify({"error": "User not found"}), 404 


if __name__ == '__main__':
    app.run(debug=True)
