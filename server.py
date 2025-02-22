from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
from google import genai

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


@app.route("/run-python", methods=["POST"])
def run_python():
    try:
        data = request.get_json()
        input_string = data.get("input_string", "")

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
            contents=input_string,
        )

        for k, v in response.function_calls[0].args.items():
            if v:
                return jsonify({"output": k})
        return jsonify({"output": "other"})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)
