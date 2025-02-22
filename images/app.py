from flask import Flask, request, jsonify
import requests
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["TabTracker"]
tabs_collection = db["tabs"]
users_collection = db["users"]

# Scoring System
CATEGORY_SCORES = {
    "Education": 5,
    "Productivity": 5,
    "Technology & Development": 2,
    "Finance & Investments": 2,
    "Health & Wellness": 2,
    "Social Media": -5,
    "Entertainment": -5,
    "Gaming": -5
}

API_KEY = "YOUR_WHOISXML_API_KEY"
API_URL = "https://website-categorization.whoisxmlapi.com/api/v2"

@app.route('/process-tabs', methods=['POST'])
def process_tabs():
    data = request.json
    urls = data["urls"]
    user_id = data.get("user_id", "default_user")

    total_score = 0
    tab_entries = []

    for url in urls:
        # Get category from API
        response = requests.get(API_URL, params={"apiKey": API_KEY, "url": url})
        category = response.json().get("categories", ["Unknown"])[0]

        # Assign score based on category
        score = CATEGORY_SCORES.get(category, 0)

        # Check if tab has been open for 2+ days
        existing_tab = tabs_collection.find_one({"url": url})
        if existing_tab:
            days_open = (datetime.datetime.utcnow() - existing_tab["timestamp"]).days
            if days_open >= 2:
                score -= 2  # Deduct points for being open too long

        # Store in DB
        tab_entry = {
            "url": url,
            "category": category,
            "score": score,
            "timestamp": datetime.datetime.utcnow()
        }
        tabs_collection.update_one({"url": url}, {"$set": tab_entry}, upsert=True)
        tab_entries.append(tab_entry)

        total_score += score

    # Update user score
    users_collection.update_one({"_id": user_id}, {"$inc": {"total_score": total_score}}, upsert=True)

    return jsonify({"status": "success", "tabs": tab_entries, "total_score": total_score})

if __name__ == "__main__":
    app.run(debug=True)
