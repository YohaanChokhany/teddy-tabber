from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
from pymongo import MongoClient
from google import genai
import sqlite3
import os
from datetime import datetime

# Create db directory if it doesn't exist
os.makedirs("db", exist_ok=True)


def init_db():
    """Initialize the database and create the table if it doesn't exist."""
    conn = sqlite3.connect("db/sqlite.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS webpage_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            category TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


# Initialize the database when the server starts
init_db()

client = genai.Client(api_key="AIzaSyBF66UtwF45q40Xfon6uJgyKQF9kEiNSe4")
app = Flask(__name__)
CORS(app)  # This allows the Chrome extension to make requests to this server

MONGO_URI = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Imh4SWFhSUszZTdEY01JN1ZuVnpQTSJ9.eyJpc3MiOiJodHRwczovL2Rldi1hdDIyNGs4YTJvZ3JvbW1kLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJQSTkzN3loOFFWWGlVcnpZTE4xeEVNOW1MSGUwV0hBUkBjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9kZXYtYXQyMjRrOGEyb2dyb21tZC51cy5hdXRoMC5jb20vYXBpL3YyLyIsImlhdCI6MTc0MDI3OTQ5OSwiZXhwIjoxNzQwMzY1ODk5LCJzY29wZSI6InJlYWQ6Y2xpZW50X2dyYW50cyBjcmVhdGU6Y2xpZW50X2dyYW50cyBkZWxldGU6Y2xpZW50X2dyYW50cyB1cGRhdGU6Y2xpZW50X2dyYW50cyByZWFkOnVzZXJzIHVwZGF0ZTp1c2VycyBkZWxldGU6dXNlcnMgY3JlYXRlOnVzZXJzIHJlYWQ6dXNlcnNfYXBwX21ldGFkYXRhIHVwZGF0ZTp1c2Vyc19hcHBfbWV0YWRhdGEgZGVsZXRlOnVzZXJzX2FwcF9tZXRhZGF0YSBjcmVhdGU6dXNlcnNfYXBwX21ldGFkYXRhIHJlYWQ6dXNlcl9jdXN0b21fYmxvY2tzIGNyZWF0ZTp1c2VyX2N1c3RvbV9ibG9ja3MgZGVsZXRlOnVzZXJfY3VzdG9tX2Jsb2NrcyBjcmVhdGU6dXNlcl90aWNrZXRzIHJlYWQ6Y2xpZW50cyB1cGRhdGU6Y2xpZW50cyBkZWxldGU6Y2xpZW50cyBjcmVhdGU6Y2xpZW50cyByZWFkOmNsaWVudF9rZXlzIHVwZGF0ZTpjbGllbnRfa2V5cyBkZWxldGU6Y2xpZW50X2tleXMgY3JlYXRlOmNsaWVudF9rZXlzIHJlYWQ6Y29ubmVjdGlvbnMgdXBkYXRlOmNvbm5lY3Rpb25zIGRlbGV0ZTpjb25uZWN0aW9ucyBjcmVhdGU6Y29ubmVjdGlvbnMgcmVhZDpyZXNvdXJjZV9zZXJ2ZXJzIHVwZGF0ZTpyZXNvdXJjZV9zZXJ2ZXJzIGRlbGV0ZTpyZXNvdXJjZV9zZXJ2ZXJzIGNyZWF0ZTpyZXNvdXJjZV9zZXJ2ZXJzIHJlYWQ6ZGV2aWNlX2NyZWRlbnRpYWxzIHVwZGF0ZTpkZXZpY2VfY3JlZGVudGlhbHMgZGVsZXRlOmRldmljZV9jcmVkZW50aWFscyBjcmVhdGU6ZGV2aWNlX2NyZWRlbnRpYWxzIHJlYWQ6cnVsZXMgdXBkYXRlOnJ1bGVzIGRlbGV0ZTpydWxlcyBjcmVhdGU6cnVsZXMgcmVhZDpydWxlc19jb25maWdzIHVwZGF0ZTpydWxlc19jb25maWdzIGRlbGV0ZTpydWxlc19jb25maWdzIHJlYWQ6aG9va3MgdXBkYXRlOmhvb2tzIGRlbGV0ZTpob29rcyBjcmVhdGU6aG9va3MgcmVhZDphY3Rpb25zIHVwZGF0ZTphY3Rpb25zIGRlbGV0ZTphY3Rpb25zIGNyZWF0ZTphY3Rpb25zIHJlYWQ6ZW1haWxfcHJvdmlkZXIgdXBkYXRlOmVtYWlsX3Byb3ZpZGVyIGRlbGV0ZTplbWFpbF9wcm92aWRlciBjcmVhdGU6ZW1haWxfcHJvdmlkZXIgYmxhY2tsaXN0OnRva2VucyByZWFkOnN0YXRzIHJlYWQ6aW5zaWdodHMgcmVhZDp0ZW5hbnRfc2V0dGluZ3MgdXBkYXRlOnRlbmFudF9zZXR0aW5ncyByZWFkOmxvZ3MgcmVhZDpsb2dzX3VzZXJzIHJlYWQ6c2hpZWxkcyBjcmVhdGU6c2hpZWxkcyB1cGRhdGU6c2hpZWxkcyBkZWxldGU6c2hpZWxkcyByZWFkOmFub21hbHlfYmxvY2tzIGRlbGV0ZTphbm9tYWx5X2Jsb2NrcyB1cGRhdGU6dHJpZ2dlcnMgcmVhZDp0cmlnZ2VycyByZWFkOmdyYW50cyBkZWxldGU6Z3JhbnRzIHJlYWQ6Z3VhcmRpYW5fZmFjdG9ycyB1cGRhdGU6Z3VhcmRpYW5fZmFjdG9ycyByZWFkOmd1YXJkaWFuX2Vucm9sbG1lbnRzIGRlbGV0ZTpndWFyZGlhbl9lbnJvbGxtZW50cyBjcmVhdGU6Z3VhcmRpYW5fZW5yb2xsbWVudF90aWNrZXRzIHJlYWQ6dXNlcl9pZHBfdG9rZW5zIGNyZWF0ZTpwYXNzd29yZHNfY2hlY2tpbmdfam9iIGRlbGV0ZTpwYXNzd29yZHNfY2hlY2tpbmdfam9iIHJlYWQ6Y3VzdG9tX2RvbWFpbnMgZGVsZXRlOmN1c3RvbV9kb21haW5zIGNyZWF0ZTpjdXN0b21fZG9tYWlucyB1cGRhdGU6Y3VzdG9tX2RvbWFpbnMgcmVhZDplbWFpbF90ZW1wbGF0ZXMgY3JlYXRlOmVtYWlsX3RlbXBsYXRlcyB1cGRhdGU6ZW1haWxfdGVtcGxhdGVzIHJlYWQ6bWZhX3BvbGljaWVzIHVwZGF0ZTptZmFfcG9saWNpZXMgcmVhZDpyb2xlcyBjcmVhdGU6cm9sZXMgZGVsZXRlOnJvbGVzIHVwZGF0ZTpyb2xlcyByZWFkOnByb21wdHMgdXBkYXRlOnByb21wdHMgcmVhZDpicmFuZGluZyB1cGRhdGU6YnJhbmRpbmcgZGVsZXRlOmJyYW5kaW5nIHJlYWQ6bG9nX3N0cmVhbXMgY3JlYXRlOmxvZ19zdHJlYW1zIGRlbGV0ZTpsb2dfc3RyZWFtcyB1cGRhdGU6bG9nX3N0cmVhbXMgY3JlYXRlOnNpZ25pbmdfa2V5cyByZWFkOnNpZ25pbmdfa2V5cyB1cGRhdGU6c2lnbmluZ19rZXlzIHJlYWQ6bGltaXRzIHVwZGF0ZTpsaW1pdHMgY3JlYXRlOnJvbGVfbWVtYmVycyByZWFkOnJvbGVfbWVtYmVycyBkZWxldGU6cm9sZV9tZW1iZXJzIHJlYWQ6ZW50aXRsZW1lbnRzIHJlYWQ6YXR0YWNrX3Byb3RlY3Rpb24gdXBkYXRlOmF0dGFja19wcm90ZWN0aW9uIHJlYWQ6b3JnYW5pemF0aW9uc19zdW1tYXJ5IGNyZWF0ZTphdXRoZW50aWNhdGlvbl9tZXRob2RzIHJlYWQ6YXV0aGVudGljYXRpb25fbWV0aG9kcyB1cGRhdGU6YXV0aGVudGljYXRpb25fbWV0aG9kcyBkZWxldGU6YXV0aGVudGljYXRpb25fbWV0aG9kcyByZWFkOm9yZ2FuaXphdGlvbnMgdXBkYXRlOm9yZ2FuaXphdGlvbnMgY3JlYXRlOm9yZ2FuaXphdGlvbnMgZGVsZXRlOm9yZ2FuaXphdGlvbnMgY3JlYXRlOm9yZ2FuaXphdGlvbl9tZW1iZXJzIHJlYWQ6b3JnYW5pemF0aW9uX21lbWJlcnMgZGVsZXRlOm9yZ2FuaXphdGlvbl9tZW1iZXJzIGNyZWF0ZTpvcmdhbml6YXRpb25fY29ubmVjdGlvbnMgcmVhZDpvcmdhbml6YXRpb25fY29ubmVjdGlvbnMgdXBkYXRlOm9yZ2FuaXphdGlvbl9jb25uZWN0aW9ucyBkZWxldGU6b3JnYW5pemF0aW9uX2Nvbm5lY3Rpb25zIGNyZWF0ZTpvcmdhbml6YXRpb25fbWVtYmVyX3JvbGVzIHJlYWQ6b3JnYW5pemF0aW9uX21lbWJlcl9yb2xlcyBkZWxldGU6b3JnYW5pemF0aW9uX21lbWJlcl9yb2xlcyBjcmVhdGU6b3JnYW5pemF0aW9uX2ludml0YXRpb25zIHJlYWQ6b3JnYW5pemF0aW9uX2ludml0YXRpb25zIGRlbGV0ZTpvcmdhbml6YXRpb25faW52aXRhdGlvbnMgcmVhZDpzY2ltX2NvbmZpZyBjcmVhdGU6c2NpbV9jb25maWcgdXBkYXRlOnNjaW1fY29uZmlnIGRlbGV0ZTpzY2ltX2NvbmZpZyBjcmVhdGU6c2NpbV90b2tlbiByZWFkOnNjaW1fdG9rZW4gZGVsZXRlOnNjaW1fdG9rZW4gZGVsZXRlOnBob25lX3Byb3ZpZGVycyBjcmVhdGU6cGhvbmVfcHJvdmlkZXJzIHJlYWQ6cGhvbmVfcHJvdmlkZXJzIHVwZGF0ZTpwaG9uZV9wcm92aWRlcnMgZGVsZXRlOnBob25lX3RlbXBsYXRlcyBjcmVhdGU6cGhvbmVfdGVtcGxhdGVzIHJlYWQ6cGhvbmVfdGVtcGxhdGVzIHVwZGF0ZTpwaG9uZV90ZW1wbGF0ZXMgY3JlYXRlOmVuY3J5cHRpb25fa2V5cyByZWFkOmVuY3J5cHRpb25fa2V5cyB1cGRhdGU6ZW5jcnlwdGlvbl9rZXlzIGRlbGV0ZTplbmNyeXB0aW9uX2tleXMgcmVhZDpzZXNzaW9ucyBkZWxldGU6c2Vzc2lvbnMgcmVhZDpyZWZyZXNoX3Rva2VucyBkZWxldGU6cmVmcmVzaF90b2tlbnMgY3JlYXRlOnNlbGZfc2VydmljZV9wcm9maWxlcyByZWFkOnNlbGZfc2VydmljZV9wcm9maWxlcyB1cGRhdGU6c2VsZl9zZXJ2aWNlX3Byb2ZpbGVzIGRlbGV0ZTpzZWxmX3NlcnZpY2VfcHJvZmlsZXMgY3JlYXRlOnNzb19hY2Nlc3NfdGlja2V0cyBkZWxldGU6c3NvX2FjY2Vzc190aWNrZXRzIHJlYWQ6Zm9ybXMgdXBkYXRlOmZvcm1zIGRlbGV0ZTpmb3JtcyBjcmVhdGU6Zm9ybXMgcmVhZDpmbG93cyB1cGRhdGU6Zmxvd3MgZGVsZXRlOmZsb3dzIGNyZWF0ZTpmbG93cyByZWFkOmZsb3dzX3ZhdWx0IHJlYWQ6Zmxvd3NfdmF1bHRfY29ubmVjdGlvbnMgdXBkYXRlOmZsb3dzX3ZhdWx0X2Nvbm5lY3Rpb25zIGRlbGV0ZTpmbG93c192YXVsdF9jb25uZWN0aW9ucyBjcmVhdGU6Zmxvd3NfdmF1bHRfY29ubmVjdGlvbnMgcmVhZDpmbG93c19leGVjdXRpb25zIGRlbGV0ZTpmbG93c19leGVjdXRpb25zIHJlYWQ6Y29ubmVjdGlvbnNfb3B0aW9ucyB1cGRhdGU6Y29ubmVjdGlvbnNfb3B0aW9ucyByZWFkOnNlbGZfc2VydmljZV9wcm9maWxlX2N1c3RvbV90ZXh0cyB1cGRhdGU6c2VsZl9zZXJ2aWNlX3Byb2ZpbGVfY3VzdG9tX3RleHRzIGNyZWF0ZTpuZXR3b3JrX2FjbHMgdXBkYXRlOm5ldHdvcmtfYWNscyByZWFkOm5ldHdvcmtfYWNscyBkZWxldGU6bmV0d29ya19hY2xzIGRlbGV0ZTp2ZGNzX3RlbXBsYXRlcyByZWFkOnZkY3NfdGVtcGxhdGVzIGNyZWF0ZTp2ZGNzX3RlbXBsYXRlcyB1cGRhdGU6dmRjc190ZW1wbGF0ZXMgcmVhZDpjbGllbnRfY3JlZGVudGlhbHMgY3JlYXRlOmNsaWVudF9jcmVkZW50aWFscyB1cGRhdGU6Y2xpZW50X2NyZWRlbnRpYWxzIGRlbGV0ZTpjbGllbnRfY3JlZGVudGlhbHMgcmVhZDpvcmdhbml6YXRpb25fY2xpZW50X2dyYW50cyBjcmVhdGU6b3JnYW5pemF0aW9uX2NsaWVudF9ncmFudHMgZGVsZXRlOm9yZ2FuaXphdGlvbl9jbGllbnRfZ3JhbnRzIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIiwiYXpwIjoiUEk5Mzd5aDhRVlhpVXJ6WUxOMXhFTTltTEhlMFdIQVIifQ.AQHQqrNFaBxZjhhNqdjdUs2EQ-0SWabtAVsYkDBLah6hg-gdRG4fSD692scJjAKYjZ1t92cyZhcKRY3coP_vNzTtRj8UIx2dDTPv-bL8No_Q5OOyEhZf4mfbaomX-KwsfLrBkw8IXmzl3M4j0VM2k2X0fF5ecyScWCL7H8PU1ON359kpgX6zKUOB2bgH0QJMsIw2zYoImosHMYoyQUgk1UqNz1R7mguwPZ2UwSCpCM50gnAdeL2ztrJH8AXW8t_n9BRY4IGMK_-xnTbmH_Kaiyy6I3QRkJ_ejpmdmGnse5LTlcK5pKfv4IRSDt6-DlrqfGzIOQAof5_nLzigj91CXQ"
client = MongoClient(MONGO_URI)
db = client["user_data"]
users_collection = db["users"]

@app.route("/api/store-user", methods=["POST"])
def store_user():
    data = request.json
    username = data.get("username")
    ip_address = data.get("ip_address")

    if not username or not ip_address:
        return jsonify({"error": "Username and IP address are required"}), 400

    existing_user = users_collection.find_one({"ip_address": ip_address})
    if not existing_user:
        users_collection.insert_one({"username": username, "ip_address": ip_address, "tabs": []})

    return jsonify({"message": "User stored successfully"})

@app.route("/api/tabs", methods=["POST"])
def store_tab_data():
    data = request.json
    username = data.get("username")
    ip_address = data.get("ip_address")
    tabs = data.get("tabs", [])

    if not username or not ip_address or not tabs:
        return jsonify({"error": "Username, IP address, and tabs are required"}), 400

    users_collection.update_one(
        {"ip_address": ip_address},
        {"$push": {"tabs": {"$each": tabs}}},
        upsert=True
    )

    return jsonify({"message": "Tabs stored successfully"})

if __name__ == "__main__":
    app.run(port=5000)

def tab_categorizer(
        education: bool,
        entertainment: bool,
        productivity: bool,
        tech_and_dev: bool,
        finance: bool,
        health_and_wellness: bool,
        social_media: bool,
        shopping: bool,
        gaming: bool,
        other: bool,
) -> None:
    """Categorizes the tabs based on the user's input. Only one of the arguments can be true.

    Args:
        education (bool): Whether the user has an education tab open.
        entertainment (bool): Whether the user has an entertainment tab open.
        productivity (bool): Whether the user has a productivity tab open.
        tech_and_dev (bool): Whether the user has a tech and dev tab open.
        finance (bool): Whether the user has a finance tab open.
        health_and_wellness (bool): Whether the user has a health and wellness tab open.
        social_media (bool): Whether the user has a social media tab open.
        shopping (bool): Whether the user has a shopping tab open.
        gaming (bool): Whether the user has a gaming tab open.
        other (bool): Whether the user has an other tab open.
    """
    # Create a dictionary mapping boolean args to their names
    categories = {
        "education": education,
        "entertainment": entertainment,
        "productivity": productivity,
        "tech_and_dev": tech_and_dev,
        "finance": finance,
        "health_and_wellness": health_and_wellness,
        "social_media": social_media,
        "shopping": shopping,
        "gaming": gaming,
        "other": other,
    }

    # Find which category is True
    active_category = next((cat for cat, value in categories.items() if value), None)

    return active_category


@app.route("/categorize", methods=["POST"])
def categorize():
    try:
        data = request.get_json()
        title = data.get("title", "")
        url = data.get("url", "")
        print(f"Title: {title}\nURL: {url}")

        # Connect to database once
        conn = sqlite3.connect("db/sqlite.db")
        c = conn.cursor()

        # Check if URL already exists in database
        c.execute(
            """
            SELECT category FROM webpage_categories 
            WHERE url = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """,
            (url,),
        )
        existing_category = c.fetchone()

        if existing_category:
            print(f"Category: {existing_category[0]}")
            conn.close()
            return jsonify({"output": existing_category[0]})

        # If URL doesn't exist, proceed with API call
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            config={
                "tools": [tab_categorizer],
                "tool_config": {
                    "function_calling_config": {
                        "mode": "ANY",
                    }
                },
                "automatic_function_calling": {
                    "disable": True,
                    "maximum_remote_calls": None,
                },
                "system_instruction": open(
                    "gemini-api/system-instructions.txt", "r"
                ).read(),
            },
            contents=f"Title: {title}\nURL: {url}",
        )

        category = "other"
        for k, v in response.function_calls[0].args.items():
            if v:
                category = k
                break
        print(f"Category: {category}")

        # Store the data using the existing connection
        c.execute(
            """
            INSERT INTO webpage_categories (title, url, category)
            VALUES (?, ?, ?)
        """,
            (title, url, category),
        )
        conn.commit()
        conn.close()

        return jsonify({"output": category})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/categorize-batch", methods=["POST"])
def categorize_batch():
    print("Categorizing batch")
    try:
        data = request.get_json()
        tabs = data.get("tabs", [])  # Expect list of {url, title} objects

        # Connect to database once for the entire batch
        conn = sqlite3.connect("db/sqlite.db")
        c = conn.cursor()

        results = []
        for tab in tabs:
            url = tab.get("url", "")
            title = tab.get("title", "")

            # Check if URL exists in database
            c.execute(
                """
                SELECT category FROM webpage_categories 
                WHERE url = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """,
                (url,),
            )
            existing_category = c.fetchone()

            if existing_category:
                print(f"Found category for {url}: {existing_category[0]}")
                results.append(
                    {"url": url, "title": title, "category": existing_category[0]}
                )
                continue

            # If URL doesn't exist, call the API
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                config={
                    "tools": [tab_categorizer],
                    "tool_config": {
                        "function_calling_config": {
                            "mode": "ANY",
                        }
                    },
                    "automatic_function_calling": {
                        "disable": True,
                        "maximum_remote_calls": None,
                    },
                    "system_instruction": open(
                        "gemini-api/system-instructions.txt", "r"
                    ).read(),
                },
                contents=f"Title: {title}\nURL: {url}",
            )

            category = "other"
            for k, v in response.function_calls[0].args.items():
                if v:
                    category = k
                    break
            print(f"New category for {url}: {category}")

            # Store the new categorization
            c.execute(
                """
                INSERT INTO webpage_categories (title, url, category)
                VALUES (?, ?, ?)
            """,
                (title, url, category),
            )

            results.append({"url": url, "title": title, "category": category})

        # Commit all new entries and close connection
        conn.commit()
        conn.close()

        return jsonify({"results": results})
    except Exception as e:
        print(e)
        if "conn" in locals():
            conn.close()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)