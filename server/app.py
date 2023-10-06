#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

@app.get("/campers")
def get_all_campers():
    campers = Camper.query.all()
    campers_to_dict = [camper.to_dict(rules=("-signups",)) for camper in campers]

    return make_response(campers_to_dict, 200)

@app.get("/activities")
def get_all_activities():
    activities = Activity.query.all()
    activities_to_dict = [activity.to_dict(rules=("-signups",)) for activity in activities]

    return make_response(activities_to_dict, 200)

@app.delete("/activities/<int:id>")
def delete_activity_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()
    
    if not activity:
        return make_response({"error": "Activity not found"}, 404)

    db.session.delete(activity)
    db.session.commit()
    return make_response({}, 204)

@app.get("/campers/<int:id>")
def camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first() # instance of that row
    if not camper:
        return make_response({"error": "Camper not found"}, 404)
  
    camper_to_dict = camper.to_dict()
    return make_response(camper_to_dict, 200)

# @app.patch("/campers/<int:id>")
# def patch_camper_by_id(id):
#     camper = Camper.query.filter(Camper.id == id).first()

#     if not camper:
#         return make_response({"error": "Camper not found"}, 404)
    
#     data = request.get_json()
#     try:
#         for key in data:
#             setattr(camper, key, data[key])

#         db.session.add(camper)
#         db.session.commit()

#         return make_response(camper.to_dict(rules=("-signups",)), 202)
    
#     except:
#         return make_response({"errors"}, 400)

class CampersById(Resource):
    def patch(seld, id):
        camper = db.session.get(Camper, id)
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        
        try:
            for key in request.json:
                setattr(camper, key, request.json[key])
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict(), 202)
        except:
            return make_response({"errors": ["validation errors"]}, 400)        
api.add_resource(CampersById, "/campers/<int:id>")

@app.post("/campers")
def post_camper():
    # Retrieve the data sent from the POST request body
    data = request.get_json()

    try: 
        new_camper = Camper(
            name = data.get("name"),
            # name = request.json["name"]
            age = data.get("age"),
            # age = request.json["age"]
        )
        db.session.add(new_camper)
        db.session.commit()
        return make_response(new_camper.to_dict(rules=("-signups",)), 201)

    except ValueError:
        return make_response({"errors": ["validation errors"]}, 400)

@app.post("/signups")
def post_signups():
    data = request.get_json()

    try: 
        new_signup = Signup(
            time = data.get("time"),
            # time = request.json["camper_id"]
            # time = data["time"]
            camper_id = data.get("camper_id"),
            # camper_id = request.json["camper_id"]
            # camper_id = data["camper_id"]
            activity_id = data.get("activity_id")
            # activity_id = request.json["activity_id"]
            # activity_id = data["activity_id"]
        )
        db.session.add(new_signup)
        db.session.commit()
        return make_response(new_signup.to_dict(), 201)

    except:
        return make_response({"errors": ["validation errors"]}, 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
