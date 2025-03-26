from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="rexmax543213", 
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


def get_faculty_info(parameters):
    
    print("Received parameters:", parameters)
    
    faculty_id = parameters.get('faculty_id')
   
    # Try different possible parameter names for faculty name and clean up the value
    faculty_name = None
    possible_name_params = ['faculty_name', 'name', 'person', 'any']
    
    for param in possible_name_params:
        if param in parameters and parameters[param]:
            # Clean up the faculty name
            faculty_name = str(parameters[param]).strip()
            # Remove common prefixes and suffixes
            faculty_name = faculty_name.replace("Dr.", "").replace("Dr", "").replace("Professor", "").replace("Prof.", "").replace("Mr.", "").replace("Mrs.", "").strip()
            # Remove any extra whitespace
            faculty_name = " ".join(faculty_name.split())
            if faculty_name:
                break
    
    print(f"Extracted faculty_id: {faculty_id}, faculty_name: {faculty_name}")

    conn = connect_db()
    cursor = conn.cursor()

    if faculty_id:
        cursor.execute("SELECT faculty_name, department, roles, qualification, email FROM faculty WHERE faculty_id = %s", (faculty_id,))
    elif faculty_name:
        # Use a more flexible LIKE query for name matching
        search_name = "%" + faculty_name + "%"
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
        if faculty_name:
            response_text = f"Faculty with name similar to '{faculty_name}' not found in the database."
        elif faculty_id:
            response_text = f"Faculty with ID '{faculty_id}' not found in the database."
        else:
            response_text = "Faculty not found in the database."

    return jsonify({'fulfillmentText': response_text})


def get_faculty_by_department(parameters):
   
    print("Received parameters for department query:", parameters)
    print("Raw parameters:", parameters)
    
    # Try different possible parameter names for department
    department = parameters.get('department') or parameters.get('Department') or parameters.get('department-name') or parameters.get('department_name')
    
    # Print all parameter keys for debugging
    print("All parameter keys:", list(parameters.keys()))
    
    # Department mappings to handle abbreviations
    department_mappings = {
        "cse": "Computer Science Engineering",
        "computer science": "Computer Science Engineering",
        "cs": "Computer Science Engineering",
        "civil": "Civil Engineering",
        "food": "Food Engineering Technology",
        "fet": "Food Engineering Technology",
        "ece": "Electronics and Communication Engineering",
        "electronics": "Electronics and Communication Engineering",
        "ie": "Instrumentation Engineering",
        "instrumentation": "Instrumentation Engineering",
        "ee": "Electrical Engineering",
        "electrical": "Electrical Engineering",
        "me": "Mechanical Engineering",
        "mechanical": "Mechanical Engineering",
        "mcd": "Multimedia Communication and Design",
        "multimedia": "Multimedia Communication and Design",
        "chem": "Chemistry",
        "chemistry": "Chemistry",
        "physics": "Physics",
        "math": "Mathematics",
        "maths": "Mathematics",
        "mathematics": "Mathematics",
        "hss": "Humanities and Social Science",
        "humanities": "Humanities and Social Science"
    }
    
    # Check all text parameters for department keywords
    if not department:
        # Check the entire query text if available
        query_text = parameters.get('text') or ""
        if isinstance(query_text, str):
            query_text = query_text.lower()
            for abbr, full_dept in department_mappings.items():
                if abbr in query_text:
                    department = full_dept
                    print(f"Found department '{department}' in query text")
                    break
    
    # If still no department, check all parameters for department names or abbreviations
    if not department:
        for key, value in parameters.items():
            if isinstance(value, str):
                value_lower = value.lower()
                # Check if any known department abbreviation is in the value
                for abbr, full_dept in department_mappings.items():
                    if abbr in value_lower:
                        department = full_dept
                        print(f"Found department '{department}' in parameter '{key}'")
                        break
                if department:
                    break
    
    # If still no department, fall back to checking for standard department names
    if not department:
        possible_departments = [
            "Computer Science Engineering", "Civil Engineering", "Food Engineering Technology",
            "Electronics and Communication Engineering", "Instrumentation Engineering", 
            "Electrical Engineering", "Mechanical Engineering", "Multimedia Communication and Design",
            "Chemistry", "Physics", "Mathematics", "Humanities and Social Science"
        ]
        
        for key, value in parameters.items():
            if isinstance(value, str):
                value_lower = value.lower()
                for dept in possible_departments:
                    if dept.lower() in value_lower:
                        department = dept
                        print(f"Found department '{department}' in parameter '{key}'")
                        break
                if department:
                    break
    
    if not department:
        return jsonify({'fulfillmentText': "Please specify a department name. For example, 'Computer Science Engineering' or 'Electrical Engineering'. You can also use abbreviations like CSE, ECE, ME, etc."})
    
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
