import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.json_util import dumps

# MongoDB connection URI
uri = "mongodb+srv://bear_hello:bear_necessities3!@tabs.kdrkq.mongodb.net/?retryWrites=true&w=majority&appName=tabs"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['userDataDB']
users_collection = db['users']
tabs_collection = db['user_tabs']

def merge_and_store_data(usernames_file, results_file):
    # Load usernames.json
    with open(usernames_file, 'r') as f:
        users = json.load(f)

    # Load results.json
    with open(results_file, 'r') as f:
        results = json.load(f)['results']

    # Group results by IP address
    ip_to_tabs = {}
    for result in results:
        ip = result['ip_address']
        if ip not in ip_to_tabs:
            ip_to_tabs[ip] = []
        ip_to_tabs[ip].append({
            "url": result["url"],
            "title": result["title"],
            "category": result["category"]
        })

    # Create user documents and insert into MongoDB
    for user in users:
        ip_address = user["ip_address"]
        username = user["username"]

        # Fetch the user's score from the users collection
        user_doc = users_collection.find_one({"username": username})
        score = user_doc["score"] if user_doc else 0

        user_data = {
            "username": username,
            "ip_address": ip_address,
            "tabs": ip_to_tabs.get(ip_address, []),
            "score": score
        }
        tabs_collection.update_one({"username": username}, {"$set": user_data}, upsert=True)

    # Write results to a JSON file including the score
    with open(results_file, 'w') as file:
        json.dump({"results": results}, file, indent=4)

    print("Data merged and stored successfully.")

def fetch_user_data(username):
    user_data = tabs_collection.find_one({"username": username})
    if user_data:
        print(dumps(user_data, indent=4))
    else:
        print(f"No user found with username: {username}")

def fetch_urls_by_ip(ip_address):
    user_data = tabs_collection.find_one({"ip_address": ip_address})
    if user_data and "tabs" in user_data:
        for tab in user_data["tabs"]:
            print(f"URL: {tab['url']}, Title: {tab['title']}, Category: {tab.get('category', 'N/A')}")
    else:
        print(f"No data found for IP address: {ip_address}")

# Example usage
merge_and_store_data('./my-modern-app/usernames.json', 'results.json')
fetch_user_data('sjnetra')
fetch_urls_by_ip('149.154.22.194')