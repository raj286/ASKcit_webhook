from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Database Connection Function
def connect_db():
    return mysql.connector.connect(
        host="localhost",  # Change if using a remote MySQL server
        user="root",
        password="rexmax543213",
        database="student_db"
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()

    # Extract roll number from Dialogflow request
    parameters = req['queryResult']['parameters']
    roll_number = parameters.get('roll_number')

    if not roll_number:
        return jsonify({'fulfillmentText': "Please provide a valid roll number."})

    # Fetch CGPA from MySQL
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT student_name, cgpa FROM students WHERE roll_number = %s", (roll_number,))
    result = cursor.fetchone()
    
    if result:
        student_name, cgpa = result
        response_text = f"{student_name} has a CGPA of {cgpa}."
    else:
        response_text = "Roll number not found in the database."

    cursor.close()
    conn.close()

    return jsonify({'fulfillmentText': response_text})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
