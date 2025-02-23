import bson
import pymongo

from flask import current_app, g
from werkzeug.local import LocalProxy

from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

# 🔹 Connect to MongoDB (Change URI if using MongoDB Atlas)
app.config["MONGO_URI"] = "mongodb://localhost:27017/userDataDB"
mongo = PyMongo(app)
users_collection = mongo.db.users  # Collection to store user data

# 🔹 Route to add a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    new_user = {
        "username": username,
        "tabs_open": [],  # List of tabs open
        "score": 0  # Initial score
    }
    result = users_collection.insert_one(new_user)
    return jsonify({"message": "User added", "user_id": str(result.inserted_id)})

# 🔹 Route to update a user's open tabs
@app.route('/update_tabs/<user_id>', methods=['PUT'])
def update_tabs(user_id):
    data = request.json
    tabs_open = data.get('tabs_open')

    if not isinstance(tabs_open, list):
        return jsonify({"error": "tabs_open must be a list"}), 400

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"tabs_open": tabs_open}}
    )
    return jsonify({"message": "Tabs updated"})

# 🔹 Route to update a user's score
@app.route('/update_score/<user_id>', methods=['PUT'])
def update_score(user_id):
    data = request.json
    new_score = data.get('score')

    if not isinstance(new_score, int):
        return jsonify({"error": "Score must be an integer"}), 400

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"score": new_score}}
    )
    return jsonify({"message": "Score updated"})

# 🔹 Route to get user details
@app.route('/get_user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"error": "User not found"}), 404

    user["_id"] = str(user["_id"])  # Convert ObjectId to string
    return jsonify(user)

# 🔹 Route to delete a user
@app.route('/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    users_collection.delete_one({"_id": ObjectId(user_id)})
    return jsonify({"message": "User deleted"})

if __name__ == '__main__':
    app.run(debug=True)