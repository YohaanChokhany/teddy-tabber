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
score_fin = 0
def merge_and_store_data(usernames_file, results_file):
    try:
        # Load usernames.json
        with open(usernames_file, 'r') as f:
            users = json.load(f)
        print(f"Loaded {len(users)} users from {usernames_file}")

        # Load results.json
        with open(results_file, 'r') as f:
            results_data = json.load(f)

        # Ensure 'total_score' exists in results_data
        if 'total_score' in results_data:
            total_score = results_data['total_score']
            score_fin = total_score
        else:
            raise KeyError("Key 'total_score' not found in results data")
        print(f"Total Score from results file: {total_score}")

        results = results_data['results']
        print(f"Loaded {len(results)} results from {results_file}")

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
        print(f"Grouped results by {len(ip_to_tabs)} unique IPs")

        # Create user documents and insert into MongoDB
        for user in users:
            ip_address = user["ip_address"]
            username = user["username"]

            # Fetch the user's score from the users collection
            print(f"Fetching user document for: {username}")
            user_doc = users_collection.find_one({"username": username})
            print(f"Raw user document: {user_doc}")

            if user_doc:
                score = user_doc.get("total_score", None)
                if score is None:
                    print(f"total_score not found for {username}, defaulting to 0")
                    score = 0
            else:
                print(f"User {username} not found in users collection, defaulting score to 0")
                #score = 0

            user_tabs = ip_to_tabs.get(ip_address, [])
            print(f"Tabs found for {username}: {len(user_tabs)}")

            user_data = {
                "username": username,
                "ip_address": ip_address,
                "tabs": user_tabs,
                "score": score_fin
            }
            print(f"Final user data to update: {json.dumps(user_data, indent=4)}")

            # Use username as the unique identifier
            result = tabs_collection.update_one(
                {"username": username},
                {"$set": user_data},
                upsert=True
            )

            print(f"Update result for {username}: {result.modified_count} documents modified")

    except Exception as e:
        print(f"An error occurred: {e}")

print("Data merged and stored successfully.")

def fetch_user_data(username):
    print(f"\nFetching data for user: {username}")

    # Get the score from users collection
    user_score = users_collection.find_one({"username": username})
    if user_score:
        print(f"User found in users collection: {user_score}")
        print(f"Total Score in users collection: {user_score.get('total_score', 0)}")
    else:
        print(f"No score found for {username}")

    # Get the tabs data
    user_data = tabs_collection.find_one({"username": username})
    if user_data:
        if user_score:
            user_data["total_score"] = user_score.get("total_score", 0)
        print("\nUser data from tabs collection:")
        print(dumps(user_data, indent=4))
    else:
        print(f"No user found with username: {username}")

def fetch_urls_by_ip(ip_address):
    print(f"\nFetching URLs for IP: {ip_address}")
    user_data = tabs_collection.find_one({"ip_address": ip_address})
    if user_data and "tabs" in user_data:
        for tab in user_data["tabs"]:
            print(f"URL: {tab['url']}, Title: {tab['title']}, Category: {tab.get('category', 'N/A')}")
    else:
        print(f"No data found for IP address: {ip_address}")

def verify_input_files(usernames_file, results_file):
    try:
        with open(usernames_file, 'r') as f:
            users = json.load(f)
            print(f"Usernames file contains {len(users)} users")
            print("Sample user:", users[0] if users else "No users found")

        with open(results_file, 'r') as f:
            results = json.load(f)
            print(f"Results file contains {len(results['results'])} results")
            print("Sample result:", results['results'][0] if results['results'] else "No results found")

        return True
    except Exception as e:
        print(f"Error verifying input files: {e}")
        return False

# Example usage with verification
if verify_input_files('./my-modern-app/usernames.json', 'results.json'):
    merge_and_store_data('./my-modern-app/usernames.json', 'results.json')
    fetch_user_data('sjnetra')
    fetch_urls_by_ip('149.154.22.194')