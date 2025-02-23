from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import requests
from google import genai
import sqlite3
import os
import json
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
def add_score_column():
    """Add the score column to the webpage_categories table if it doesn't exist."""
    conn = sqlite3.connect("db/sqlite.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(webpage_categories)")
    columns = [column[1] for column in c.fetchall()]
    if "score" not in columns:
        c.execute("ALTER TABLE webpage_categories ADD COLUMN score INTEGER NOT NULL DEFAULT 0")
    conn.commit()
    conn.close()

# Initialize the database and add the score column if necessary
init_db()
add_score_column()

client = genai.Client(api_key="AIzaSyBF66UtwF45q40Xfon6uJgyKQF9kEiNSe4")
app = Flask(__name__)
CORS(app)  # This allows the Chrome extension to make requests to this server

def get_category_score(category):
    """Assigns a score based on category type."""
    category_scores = {
        'education': 500,
        'entertainment': -500,
        'productivity': 500,
        'tech_and_dev': 200,
        'finance': 200,
        'health_and_wellness': 200,
        'social_media': -500,
        'shopping': -200,
        'gaming': -500,
        'other': -100
    }
    return category_scores.get(category, 1)

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

        conn = sqlite3.connect("db/sqlite.db")
        c = conn.cursor()

        c.execute(
            """
            SELECT category, score FROM webpage_categories
            WHERE url = ?
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (url,),
        )
        existing_entry = c.fetchone()

        if existing_entry:
            category, score = existing_entry
            print(f"Category: {category}, Score: {score}")
            conn.close()
            return jsonify({"output": category, "score": score})

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            config={
                "tools": [tab_categorizer],
                "tool_config": {"function_calling_config": {"mode": "ANY"}},
                "automatic_function_calling": {"disable": True, "maximum_remote_calls": None},
                "system_instruction": open("gemini-api/system-instructions.txt", "r").read(),
            },
            contents=f"Title: {title}\nURL: {url}",
        )

        category = "other"
        for k, v in response.function_calls[0].args.items():
            if v:
                category = k
                break

        score = get_category_score(category)
        print(f"Category: {category}, Score: {score}")

        c.execute(
            """
            INSERT INTO webpage_categories (title, url, category, score)
            VALUES (?, ?, ?, ?)
            """,
            (title, url, category, score),
        )
        conn.commit()
        conn.close()

        return jsonify({"output": category, "score": score})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

import json

@app.route("/categorize-batch", methods=["POST"])
def categorize_batch():
    print("Categorizing batch")
    try:
        data = request.get_json()
        tabs = data.get("tabs", [])
        user_ip = request.remote_addr  # Capture the user's IP address

        conn = sqlite3.connect("db/sqlite.db")
        c = conn.cursor()

        results = []
        total_score = 0
        for tab in tabs:
            url = tab.get("url", "")
            title = tab.get("title", "")

            c.execute(
                """
                SELECT category, score FROM webpage_categories
                WHERE url = ?
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (url,),
            )
            existing_entry = c.fetchone()

            if existing_entry:
                category, score = existing_entry
                print(f"Found category for {url}: {category}, Score: {score}")
            else:
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    config={
                        "tools": [tab_categorizer],
                        "tool_config": {"mode": "ANY"},
                        "automatic_function_calling": {"disable": True, "maximum_remote_calls": None},
                        "system_instruction": open("gemini-api/system-instructions.txt", "r").read(),
                    },
                    contents=f"Title: {title}\nURL: {url}",
                )

                category = "other"
                for k, v in response.function_calls[0].args.items():
                    if v:
                        category = k
                        break

                score = get_category_score(category)
                print(f"New category for {url}: {category}, Score: {score}")

                c.execute(
                    """
                    INSERT INTO webpage_categories (title, url, category, score)
                    VALUES (?, ?, ?, ?)
                    """,
                    (title, url, category, score),
                )

            results.append({"url": url, "title": title, "category": category, "score": score, "ip_address": user_ip})
            total_score += score

        conn.commit()
        conn.close()

        # Write results to results.json including IP address
        with open("results.json", "w") as f:
            json.dump({"results": results, "total_score": total_score}, f, indent=4)

        # Call the external scripts
        subprocess.run(["python3", "./my-modern-app/getting_users.py"])
        subprocess.run(["python3", "mongo_readwrite.py"])

        return jsonify({"results": results, "total_score": total_score})
    #hi test commit?
    except Exception as e:
        print(e)
        if "conn" in locals():
            conn.close()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)