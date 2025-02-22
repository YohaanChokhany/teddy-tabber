import google.generativeai as genai
# Step 1: Configure the Gemini API
API_KEY = "AIzaSyC3zDAbuPrj4okDnXmvpHRbqLKo3GywmrE"  # Replace with your actual API key
genai.configure(api_key=API_KEY)

# Step 2: Define the categories
CATEGORIES = {
    "education": 5,
    "productivity": 5,
    "technology & development": 2,
    "finance & investments": 2,
    "health & wellness": 2,
    "social media": -5,
    "entertainment": -5,
    "gaming": -5,
}

# Step 3: Function to classify tabs
def categorize_tabs(tab_titles):
    model = genai.GenerativeModel("gemini-1.5-flash")  # Adjust model version as needed

    # Construct the prompt
    prompt = f"""
    You are an AI that categorizes website tabs into predefined categories with scores:
    {CATEGORIES}

    Given a list of tab titles, return the most suitable category for each.

    Example format:
    - "Khan Academy - Learn Math" -> "education"
    - "Stock Market News - Bloomberg" -> "finance & investments"
    - "TikTok - Watch Videos" -> "social media"

    Tabs to categorize:
    {tab_titles}
    """

    # Generate AI response
    response = model.generate_content(prompt)

    return response.text

# Step 4: Example usage
tabs = [
    "Khan Academy - Learn Math",
    "Gmail - Inbox",
    "GitHub - Open Source Projects",
    "Netflix - Watch Movies",
    "Yahoo Finance - Stock Prices",
    "Fortnite - Play Now",
]

categorized_tabs = categorize_tabs(tabs)
print(categorized_tabs)
