from src.app import app
from flask import request, Response
from src.helpers.json_response import asJsonResponse
import re
from src.database import db

# http://localhost:3000/v2/company/facebook


@app.route("/v2/company/<companyNameQuery>")
@asJsonResponse
def searchCompanyV2(companyNameQuery):

    if not companyNameQuery:
        # Set status code to 400 BAD REQUEST
        return {
            "status": "error",
            "message": "Empty company name, please specify one"
        }, 400

    # Search a company in mongodb database
    projection = {"name": 1, "category_code": 1, "description": 1}
    searchRE = re.compile(f"{companyNameQuery}", re.IGNORECASE)
    foundCompany = db["crunchbase"].find_one(
        {"name": searchRE}, projection)

    if not foundCompany:
        # Set status code to 404 NOT FOUND
        return {
            "status": "not found",
            "message": f"No company found with name {companyNameQuery} in database"
        }, 404

    return {
        "status": "OK",
        "searchQuery": companyNameQuery,
        "company": foundCompany
    }
