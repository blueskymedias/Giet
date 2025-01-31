from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# Database connection configuration
DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = '1616'

# Function to get a database connection
def get_db_connection():
    connection = psycopg2.connect(
        host= DB_HOST,
        database= DB_NAME,
        user= DB_USER,
        password= DB_PASSWORD
    )
    return connection

# Create the 'tasks' table if it doesn't exist
def create_tasks_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tasks (
                   task_id SERIAL PRIMARY KEY,
                   task_title TEXT NOT NULL,
                   task_description TEXT NOT NULL,
                   task_status TEXT NOT NULL
                   );
                   """)
    connection.commit()
    cursor.close()
    connection.close()

create_tasks_table_if_not_exists()

@app.route('/create_task', methods=['POST'])
def create_task():
    task_title = request.json['task_title']
    task_description = request.json['task_description']
    task_status = request.json['task_status']

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
                   INSERT INTO tasks (task_title, task_description, task_status) VALUES (%s, %s, %s);
                   """, (task_title, task_description, task_status))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Task created successfully"}), 201

@app.route('/get_all_tasks', methods=['GET'])
def get_all_tasks():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
                   SELECT * FROM tasks;
                   """)
    
    tasks = cursor.fetchall()
    cursor.close()
    connection.close()

    result = [{"task_id": each_task[0], "task_title": each_task[1], "task_description": each_task[2], "task_status": each_task[3]} for each_task in tasks]
    return jsonify(result), 200

@app.route('/update_task_status', methods=['PUT'])
def update_task_status():
    task_id = request.args.get('task_id')
    task_status = request.json['task_status']

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "UPDATE tasks SET task_status = %s WHERE task_id = %s"
    cursor.execute(query, (task_status, task_id))
    
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Task status updated successfully"}), 200

@app.route('/delete_task', methods=['DELETE'])
def delete_task():
    task_id = request.args.get('task_id')

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "DELETE FROM tasks WHERE task_id = %s"
    cursor.execute(query, (task_id,))
    
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Task deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
