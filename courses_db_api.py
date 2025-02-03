from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import sql

app = Flask (__name__)

#Database connection configuration
DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = '2525'

#Function to get a database connection
def get_db_connection():
    connection = psycopg2.connect(
        host= DB_HOST,
        database= DB_NAME,
        user= DB_USER,
        password= DB_PASSWORD
    )
    return connection

# Create the 'courses' table if it doesn't exist
def create_courses_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute ("""
                    CREATE TABLE IF NOT EXISTS courses (
                    id SERIAL PRIMARY KEY,
                    course_name TEXT NOT NULL,
                    course_code TEXT NOT NULL UNIQUE
                    );
                    """)
    connection.commit()
    cursor.close()
    connection.close()

create_courses_table_if_not_exists()

@app.route('/register_course', methods=['POST'])
def register_course():
    course_name = request.json['course_name']
    course_code = request.json['course_code']
  

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
                   INSERT INTO courses (course_name, course_code) VALUES (%s, %s);
                   """, (course_name, course_code))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Course registered successfully"}), 201

@app.route('/get-all-courses', methods=['GET'])
def get_all_courses():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
                   SELECT * FROM courses;
                   """)

    courses = cursor.fetchall()
    cursor.close()
    connection.close()

    result = [
        {"id": course[0], "course_name": course[1], "course_code": course[2]} 
        for course in courses
    ]
    return jsonify(result), 200


@app.route("/delete-by-id", methods=['DELETE'])
def delete_course():
    id = request.args.get('id')  # Get the 'id' parameter from the query string
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "DELETE FROM courses WHERE id = %s"
    cursor.execute(query, (id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Successfully deleted given course"})

@app.route("/get-single-course", methods=['GET'])
def get_single_course():
    id = request.args.get('id')  # Get the 'id' parameter from the query string
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM courses WHERE id = %s"
    cursor.execute(query, (id,))
    course = cursor.fetchone()
    cursor.close()
    connection.close()
    if course:
        result = {
            "id": course[0],
            "course_name": course[1],
            "course_code": course[2]
        }
        return jsonify(result), 200
    else:
        return jsonify({"error": "Course not found"}), 404

@app.route('/update_course', methods=['PUT'])
def update_course():
    id = request.args.get['id'] 
    course_name = request.json['course_name']
    course_code = request.json['course_code']

    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
                   UPDATE courses
                   SET course_name = %s, course_code = %s
                   WHERE id = %s;
                   """, (course_name, course_code, id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Course updated successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
