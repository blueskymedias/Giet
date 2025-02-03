from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import sql

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

# Create the 'students' table if it doesn't exist
def create_students_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS studentdeatils (
                    id SERIAL PRIMARY KEY,
                    student_name TEXT NOT NULL,
                    roll_number TEXT NOT NULL UNIQUE,
                    course_name TEXT NOT NULL,
                    course_code TEXT NOT NULL
                    );
                    """)
    connection.commit()
    cursor.close()
    connection.close()

create_students_table_if_not_exists()




@app.route('/register_student', methods=['POST'])
def register_student():
    student_name = request.json['student_name']
    roll_number = request.json['roll_number']
    course_name = request.json['course_name']
    course_code = request.json['course_code']

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
                   INSERT INTO studentdeatils (student_name, roll_number, course_name, course_code) 
                   VALUES (%s, %s, %s, %s);
                   """, (student_name, roll_number, course_name, course_code))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Student registered successfully"}), 201

@app.route('/get-all-students', methods=['GET'])
def get_all_students():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
                   SELECT * FROM studentdeatils;
                   """)

    studentdeatils = cursor.fetchall()
    cursor.close()
    connection.close()

    result = [
        {"id": student[0], "student_name": student[1], "roll_number": student[2], 
         "course_name": student[3], "course_code": student[4]} 
        for student in studentdeatils
    ]
    return jsonify(result), 200

@app.route("/delete-student", methods=['DELETE'])
def delete_student():
    id = request.args.get('id')  # Get the 'id' parameter from the query string
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "DELETE FROM studentdeatils WHERE id = %s"
    cursor.execute(query, (id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Successfully deleted the student"})

@app.route("/get-single-student", methods=['GET'])
def get_single_student():
    id = request.args.get('id')  # Get the 'id' parameter from the query string
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM studentdeatils WHERE id = %s"
    cursor.execute(query, (id,))
    student = cursor.fetchone()
    cursor.close()
    connection.close()
    if student:
        result = {
            "id": student[0],
            "student_name": student[1],
            "roll_number": student[2],
            "course_name": student[3],
            "course_code": student[4]
        }
        return jsonify(result), 200
    else:
        return jsonify({"error": "Student not found"}), 404

@app.route('/update_student', methods=['PUT'])
def update_student():
    id = request.args.get('id') 
   
    course_name = request.json['course_name']

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
                   UPDATE studentdeatils
                   SET course_name = %s
                   WHERE id = %s;
                   """, ( course_name, id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Student details updated successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
