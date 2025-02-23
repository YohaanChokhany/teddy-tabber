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
            score INTEGER NOT NULL DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS user_tabs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            points INTEGER NOT NULL DEFAULT 0,
            tabs JSON NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


# Initialize the database and add the score column if necessary
init_db()

client = genai.Client(api_key="AIzaSyBF66UtwF45q40Xfon6uJgyKQF9kEiNSe4")
app = Flask(__name__)
CORS(app)  # This allows the Chrome extension to make requests to this server


def get_category_score(category):
    """Assigns a score based on category type."""
    category_scores = {
        "education": 500,
        "entertainment": -500,
        "productivity": 500,
        "tech_and_dev": 200,
        "finance": 200,
        "health_and_wellness": 200,
        "social_media": -500,
        "shopping": -200,
        "gaming": -500,
        "other": -100,
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
            conn.close()
            return jsonify({"output": category, "score": score})

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            config={
                "tools": [tab_categorizer],
                "tool_config": {"function_calling_config": {"mode": "any"}},
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

        score = get_category_score(category)

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


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "")
    with open("usernames.json", "w") as f:
        json.dump(data, f, indent=4)
    return jsonify({"message": "Login successful"})


@app.route("/get-usertabs", methods=["POST"])
def get_usertabs():
    data = request.get_json()
    username = data.get("username", "")
    conn = sqlite3.connect("db/sqlite.db")
    c = conn.cursor()
    c.execute(
        """
        SELECT points, tabs FROM user_tabs WHERE username = ?
        """,
        (username,),
    )
    user_tabs = c.fetchone()
    conn.close()
    return jsonify({"points": user_tabs[0], "tabs": json.loads(user_tabs[1])})


@app.route("/categorize-batch", methods=["POST"])
def categorize_batch():
    try:
        data = request.get_json()
        tabs = data.get("tabs", [])
        numTabGroups = data.get("numTabGroups", 0)

        with open("usernames.json", "r") as f:
            usernames = json.load(f)
        username = usernames.get("username", "")

        conn = sqlite3.connect("db/sqlite.db")
        c = conn.cursor()

        results = []
        total_score = 0
        for tab in tabs:
            url = tab.get("url", "")
            title = tab.get("title", "")
            id = tab.get("id", "")

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
            else:
                category = "other"
                score = get_category_score(category)
                c.execute(
                    """
                    INSERT INTO webpage_categories (title, url, category, score)
                    VALUES (?, ?, ?, ?)
                    """,
                    (title, url, category, score),
                )

            results.append(
                {
                    "id": id,
                    "url": url,
                    "title": title,
                    "category": category,
                    "score": score,
                }
            )
            total_score += score

        if len(tabs) < 10:
            total_score += 300
            print("300 points for opening 10 tabs")
        education_tabs_count = sum(
            1 for tab in results if tab["category"] == "education"
        )
        if education_tabs_count >= 3:
            total_score += 300
            print("300 points for opening 3 education tabs")
        if numTabGroups > 0:
            total_score += 300
            print("300 points for grouping tabs")

        c.execute(
            """
            INSERT INTO user_tabs (username, points, tabs)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                    points = excluded.points,
                    tabs = excluded.tabs
                """,
            (username, total_score, json.dumps(results)),
        )

        conn.commit()
        conn.close()

        return jsonify({"results": results, "total_score": total_score})
    except Exception as e:
        print(e)
        if "conn" in locals():
            conn.close()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)
