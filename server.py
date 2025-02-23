from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
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