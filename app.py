import google.generativeai as genai
import json

print("Google Generative AI module is working!")

API_KEY = "AIzaSyC3zDAbuPrj4okDnXmvpHRbqLKo3GywmrE"  # Replace with your actual API key
genai.configure(api_key=API_KEY)

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

def categorize_tabs(tab_titles):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    You are an AI that categorizes website tabs into predefined categories:
    {list(CATEGORIES.keys())}
    Given a list of tab titles, return a JSON object mapping each tab to a category.
    
    Example:
    {{
      "Khan Academy - Learn Math": "education",
      "Stock Market News - Bloomberg": "finance & investments",
      "TikTok - Watch Videos": "social media"
    }}
    
    Tabs to categorize:
    {json.dumps(tab_titles)}
    """

    response = model.generate_content(prompt)

    try:
        categorized_data = json.loads(response.text)  # Parse JSON response
        return categorized_data
    except json.JSONDecodeError:
        print("Error: Gemini API response not in valid JSON format.")
        return {title: "Uncategorized" for title in tab_titles}  # Default to Uncategorized

async def fetch_and_categorize_tabs():
    tabs = await chrome.tabs.query({})
    tab_titles = [tab.title for tab in tabs if tab.url]
    categorized_tabs = categorize_tabs(tab_titles)
    return categorized_tabs

async def group_tabs_by_category():
    categorized_tabs = await fetch_and_categorize_tabs()
    grouped_tabs = {}

    for tab_title, category in categorized_tabs.items():
        if category not in grouped_tabs:
            grouped_tabs[category] = []
        grouped_tabs[category].append(tab_title)

    for category, tab_titles in grouped_tabs.items():
        tab_ids = [
            tab.id for tab in await chrome.tabs.query({})
            if tab.title in tab_titles
        ]

        if tab_ids:
            try:
                group = await chrome.tabs.group({"tabIds": tab_ids})
                await chrome.tabGroups.update(group, {"title": category})
            except Exception as err:
                print(f"Error grouping \"{category}\": {err}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(group_tabs_by_category())
