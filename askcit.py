from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

# Database Connection Function
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="rexmax543213",  # Use your actual MySQL password
        database="student_db"
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName")
    parameters = req.get("queryResult", {}).get("parameters", {})

    if intent_name == "grade_cgpa1":
        return get_student_cgpa(parameters)
    elif intent_name == "Facultyinfo":
        return get_faculty_info(parameters)
    elif intent_name == "DepartmentFaculty":
        return get_faculty_by_department(parameters)
    else:
        return jsonify({'fulfillmentText': "I'm not sure how to handle that request."})

# Function to fetch student CGPA
def get_student_cgpa(parameters):
    roll_number = parameters.get('roll_number')

    if not roll_number:
        return jsonify({'fulfillmentText': "Please provide a valid roll number."})

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT student_name, cgpa FROM students WHERE roll_number = %s", (roll_number,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        student_name, cgpa = result
        response_text = f"{student_name} has a CGPA of {cgpa}."
    else:
        response_text = "Roll number not found in the database."

    return jsonify({'fulfillmentText': response_text})

# Function to fetch faculty information by faculty_id or name
def get_faculty_info(parameters):
    # Print parameters for debugging
    print("Received parameters:", parameters)
    
    faculty_id = parameters.get('faculty_id')
    # Try different possible parameter names for faculty name
    faculty_name = parameters.get('faculty_name') or parameters.get('name') or parameters.get('person')
    
    print(f"Extracted faculty_id: {faculty_id}, faculty_name: {faculty_name}")

    conn = connect_db()
    cursor = conn.cursor()

    if faculty_id:
        cursor.execute("SELECT faculty_name, department, roles, qualification, email FROM faculty WHERE faculty_id = %s", (faculty_id,))
    elif faculty_name:
        # Use a more flexible LIKE query for name matching
        search_name = "%" + str(faculty_name).strip().replace("Dr.", "").strip() + "%"
        print(f"Searching with pattern: {search_name}")
        cursor.execute("""
            SELECT faculty_name, department, roles, qualification, email 
            FROM faculty
            WHERE LOWER(faculty_name) LIKE LOWER(%s)
        """, (search_name,))
    else:
        return jsonify({'fulfillmentText': "Please provide a faculty ID or faculty name."})

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        faculty_name, department, roles, qualification, email = result
        response_text = f"{faculty_name} from {department} department has the role of {roles} with {qualification} qualification. They can be contacted at {email}."
    else:
        # Add more detailed error message for debugging
        if faculty_name:
            response_text = f"Faculty with name similar to '{faculty_name}' not found in the database."
        elif faculty_id:
            response_text = f"Faculty with ID '{faculty_id}' not found in the database."
        else:
            response_text = "Faculty not found in the database."

    return jsonify({'fulfillmentText': response_text})

# Function to fetch faculty names by department
def get_faculty_by_department(parameters):
    # Print parameters for debugging
    print("Received parameters for department query:", parameters)
    
    # Try different possible parameter names for department
    department = parameters.get('department') or parameters.get('Department') or parameters.get('department-name') or parameters.get('department_name')
    
    # Print all keys in parameters for debugging
    print("All parameter keys:", list(parameters.keys()))
    
    if not department:
        # If no department parameter found, check if any parameter contains a department name
        possible_departments = [
            "Computer Science Engineering", "Civil Engineering", "Food Engineering Technology",
            "Electronics and Communication Engineering", "Instrumentation Engineering", 
            "Electrical Engineering", "Mechanical Engineering", "Multimedia Communication and Design",
            "Chemistry", "Physics", "Mathematics", "Humanities and Social Science"
        ]
        
        # Check all parameters for any value that might be a department
        for key, value in parameters.items():
            if isinstance(value, str):
                for dept in possible_departments:
                    if dept.lower() in value.lower():
                        department = dept
                        print(f"Found department '{department}' in parameter '{key}'")
                        break
                if department:
                    break
    
    if not department:
        return jsonify({'fulfillmentText': "Please specify a department name. For example, 'Computer Science Engineering' or 'Electrical Engineering'."})
    
    print(f"Searching for faculty in department: {department}")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Use LIKE for more flexible matching of department names
    search_dept = "%" + str(department).strip() + "%"
    cursor.execute("""
        SELECT faculty_name, roles 
        FROM faculty 
        WHERE LOWER(department) LIKE LOWER(%s)
        ORDER BY faculty_name
    """, (search_dept,))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if results:
        # Format the response with all faculty members
        faculty_list = []
        for faculty_name, role in results:
            faculty_list.append(f"{faculty_name} ({role})")
        
        if len(faculty_list) == 1:
            response_text = f"There is 1 faculty member in the {department} department: {faculty_list[0]}."
        else:
            faculty_text = ", ".join(faculty_list[:-1]) + " and " + faculty_list[-1] if len(faculty_list) > 1 else faculty_list[0]
            response_text = f"There are {len(faculty_list)} faculty members in the {department} department: {faculty_text}."
    else:
        response_text = f"No faculty members found in the {department} department."
    
    return jsonify({'fulfillmentText': response_text})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
