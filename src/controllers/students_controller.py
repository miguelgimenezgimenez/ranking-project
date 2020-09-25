from src.app import app
from flask import request, Response
from src.helpers.json_response import asJsonResponse
import re
from src.database import db

# http://localhost:3000/v2/company/facebook


@app.route("/students/create/<student_name>")
@asJsonResponse
def create_student(student_name):
    if not student_name:
        # Set status code to 400 BAD REQUEST
        return {
            "status": "error",
            "message": "Empty student name, please specify one"
        }, 400

    existing_student = db['students'].find_one({"student_name": student_name})
    if existing_student:
        return {
            "status": "error",
            "message": "There is allready a student with this name on the database"
        }, 409
    student = db['students'].insert({"student_name": student_name})

    return {
        "status": "OK",
        "response": student
    }


@app.route("/students/all")
@asJsonResponse
def get_students():
    limit = int(request.args.get("limit", 50))
    page = int(request.args.get("page", 0))
    students = db['students'].find({}, {'_id': 0}).limit(limit).skip(page)
    return {
        "status": "OK",
        "response": list(students)
    }
