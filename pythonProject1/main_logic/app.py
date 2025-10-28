import os
from flask import Flask, request, jsonify
from main_logic.scraper import scrape_menu_page, is_menu_mostly_image
from main_logic.llm_parser import extract_menu_with_llm
from main_logic.cache import get_cached_menu, save_menu_to_cache
from datetime import date
from dotenv import load_dotenv
from functools import wraps
import holidays


app = Flask(__name__)
load_dotenv()

API_KEY = os.getenv("API_KEY")


def is_public_holiday(today=None):
    """
    Check if the given date (or today by default) is a public holiday in the Czech Republic.

    This helps identify days when restaurants may be closed or not publishing a daily menu.
    It includes official Czech holidays as well as Christmas dates (24–26 December).
    """

    today = today or date.today()
    cz_holidays = holidays.CZ()
    return today in cz_holidays or today.month == 12 and today.day in (24, 25, 26)


def require_api_key(func):
    """
    Flask decorator to require a valid API key for access to protected endpoints.

    The client must include an 'Authorization' header in the format:
    Authorization: Bearer <API_KEY>

    Returns:
        - 401 if the header is missing or malformed
        - 403 if the provided key is invalid
        - Calls the wrapped function if authentication succeeds
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ")[1]
        if token != API_KEY:
            return jsonify({"error": "Invalid API key"}), 403
        return func(*args, **kwargs)

    return wrapper


@app.route('/summarize', methods=['POST'])
@require_api_key
def summarize_menu():
    """
    Main API endpoint: Summarizes a restaurant's menu from a given URL.

    Steps:
    1. Validate and parse request JSON.
    2. Check cache — return cached menu if already available for today.
    3. Scrape the webpage and ensure it’s valid HTML (not an image-only menu).
    4. Extract structured menu data using the LLM.
    5. Add context note if it's a public holiday.
    6. Save to cache and return as JSON.

    Returns:
        JSON response with extracted menu data or an error message.
    """
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    today = date.today().isoformat()

    cached = get_cached_menu(url, today)
    if cached:
        return jsonify(cached)

    html_content = scrape_menu_page(url)
    if html_content is None:
        return jsonify({"error": "Failed to load menu page"}), 503
    if is_menu_mostly_image(html_content):
        return jsonify({"error": "Menu appears to be mostly in image form"}), 400

    menu_data = extract_menu_with_llm(html_content, url, today)

    if is_public_holiday(today):
        menu_data["info"] = "It's a public holiday — menu may not be available today."

    save_menu_to_cache(url, today, menu_data)

    return jsonify(menu_data)


if __name__ == '__main__':
    app.run(debug=True)
