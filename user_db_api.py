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
def create_users_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_tables (
            task_id SERIAL,
            user_id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            team TEXT NOT NULL
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()

create_users_table_if_not_exists()

bcrypt = Bcrypt()

def encode_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(hashed_password,password):
    return bcrypt.check_password_hash(hashed_password,password)


@app.route('/create_user', methods=['POST'])
def create_user():
    task_id = request.json['task_id']
    username = request.json['username']
    password = request.json['password']
    hashed_password = encode_password(password)
    team = request.json['team']

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users_tables (task_id, username, password, team) 
        VALUES (%s, %s, %s, %s);
    """, (task_id, username, hashed_password, team))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "User created successfully"}), 201

@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users_tables;")
    users = cursor.fetchall()
    cursor.close()
    connection.close()

    result = [
        {
            "task_id": each_user[0],
            "user_id": each_user[1],
            "username": each_user[2],
            "password": each_user[3],
            "team": each_user[4]
        }
        for each_user in users
    ]
    return jsonify(result), 200

@app.route('/update_user', methods=['PUT'])
def update_user():
    task_id = request.args.get('task_id')
    user_id = request.args.get('user_id')
    username = request.json.get('username')
    password = request.json.get('password')
    team = request.json.get('team')

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE users_tables 
        SET username = %s, password = %s, team = %s 
        WHERE task_id = %s  AND user_id = %s
    """
    cursor.execute(query, (username, password, team, task_id, user_id))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "User updated successfully"}), 200

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    task_id = request.args.get('task_id')
    user_id = request.args.get('user_id')

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "DELETE FROM users_tables WHERE task_id = " + task_id + " AND user_id = " + user_id
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "User deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
