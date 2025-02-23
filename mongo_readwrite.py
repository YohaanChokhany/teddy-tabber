from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.json_util import dumps

uri = "mongodb+srv://bear_hello:bear_necessities3!@tabs.kdrkq.mongodb.net/?retryWrites=true&w=majority&appName=tabs"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Function to fetch user data by username
def fetch_user_data(username):
    db = client['userTabs']
    users_collection = db['user_tabs']
    user_data = users_collection.find_one({"username": username})
    if user_data:
        print(dumps(user_data, indent=4))
    else:
        print(f"No user found with username: {username}")

# Function to write user data, including IP address, to the database
def write_user_data(username, ip_address, new_data):
    db = client['userTabs']
    users_collection = db['user_tabs']
    user_data = {
        "username": username,
        "ip_address": ip_address,
        **new_data
    }
    result = users_collection.update_one(
        {"username": username, "ip_address": ip_address},
        {"$set": user_data},
        upsert=True
    )
    if result.matched_count > 0:
        print(f"User data for '{username}' with IP '{ip_address}' updated successfully.")
    else:
        print(f"User data for '{username}' with IP '{ip_address}' inserted successfully.")

# Example usage
fetch_user_data('tech_wizard99')
write_user_data('tech_wizard99', '192.168.1.1', {"tabs_open": ["tab1", "tab2"], "score": 100})
fetch_user_data('tech_wizard99')