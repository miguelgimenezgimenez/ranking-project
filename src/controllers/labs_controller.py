from src.app import app
from flask import request, Response
from src.helpers.json_response import asJsonResponse
import re
from src.database import db
from bson.objectid import ObjectId


@app.route("/lab/create", methods=['POST'])
@asJsonResponse
def create_lab():
    lab_prefix = request.json.get("lab_prefix")
    if not lab_prefix:
        # Set status code to 400 BAD REQUEST
        return {
            "status": "error",
            "message": "Empty lab name, please specify one"
        }, 400

    existing_lab = db['labs'].find_one({"lab_prefix": lab_prefix})
    if existing_lab:

        return {
            "status": "error",
            "message": "There is allready a lab with this name on the database"
        }, 409
    lab = db['students'].insert({"lab_prefix": lab_prefix})

    return {
        "status": "OK",
        "response": lab
    }


@app.route("/lab/all")
@asJsonResponse
def get_labs():
    labs = db['labs'].find()
    return {
        'status': "OK",
        'response': labs
    }


@app.route("/lab/search")
@asJsonResponse
def search_lab():
    github_user_id = int(request.args.get("github_user_id", 0))
    lab_id = request.args.get("lab_id", None)
    state = request.args.get("state", None)

    query = {}
    if github_user_id:
        query['github_user_id'] = github_user_id
    if lab_id:
        query['lab_id'] = ObjectId(lab_id)
    if state:
        query['state'] = state

    lab = db['pull_requests'].aggregate([
        {
            '$match': query
        },
        {'$lookup':
            {
                'from': "labs",
                'localField': "lab_id",
                'foreignField': "_id",
                'as': "lab_title"
            }
         },
        {
            "$project": {
                'title': 1,
                'lab_title.title': 1,
                'lab_id': 1,
                'state': 1,
                '_id': 0
            }
        }

    ])
    return {'response': list(lab)}


@ app.route("/lab/<lab_id>/details")
@ asJsonResponse
def lab_details(lab_id):
    query = {}
    projection = {
        'total_time': 1,
        '_id': 0,
        'lab_id': 1,
        'min_time': 1,
        'max_time': 1,
        'average_time_spent': 1,
        'open': 1,
        'closed': 1,
        'lab_title.title': 1
    }
    if lab_id != 'all':
        query['lab_id'] = ObjectId(lab_id)
    github_user_id = int(request.args.get("github_user_id", 0))
    if github_user_id:
        query['github_user_id'] = github_user_id
        projection = {
            'total_time': 1,
            '_id': 0,
            'lab_id': 1,
            'open': 1,
            'closed': 1,
            'lab_title.title': 1
        }
    lab = db['pull_requests'].aggregate([
        {
            '$match': query
        },
        {
            '$project': {
                'time_spent': {
                    '$subtract': ["$closed_at", "$last_commit"]
                },
                'lab_id':1,
                'state':1,
            },
        },
        {
            '$project': {
                'hours_spent': {'$divide': ['$time_spent', 3600000]},
                'lab_id':1,
                'state':1,

            },
        },
        {
            '$group': {
                '_id': "$lab_id",
                'open': {
                    '$sum': {
                        '$cond': [
                            {'$eq': ["$state", 'open']},
                            1,
                            0
                        ]
                    }
                },
                'closed': {
                    '$sum': {
                        '$cond': [
                            {'$eq': ["$state", 'closed']},
                            1,
                            0
                        ]
                    }
                },
                'min_time': {'$min': "$hours_spent"},
                'max_time': {'$max': "$hours_spent"},
                'average_time_spent': {'$avg': "$hours_spent"},
                'total_time': {
                    '$sum': '$hours_spent'
                },
            }
        },
        {'$lookup':
            {
                'from': "labs",
                'localField': "_id",
                'foreignField': "_id",
                'as': "lab_title"
            }
         },
        {
            "$project": {
                **projection
            }
        }
    ])

    return {
        'response': lab
    }


@ app.route("/lab/<lab_id>/memes")
@ asJsonResponse
def lab_memes(lab_id):
    query = {}
    if lab_id != 'all':
        query['lab_id'] = ObjectId(lab_id)
    memes = db['pull_requests'].aggregate([
        {
            '$match': query
        },
        {
            "$project": {
                'images': 1,
                '_id': 0
            }
        }
    ])
    response = [img for meme in memes for img in meme['images']]

    return {'response': response}
