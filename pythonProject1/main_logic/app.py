from flask import Flask, request, jsonify
from main_logic.scraper import scrape_menu_page
from main_logic.llm_parser import extract_menu_with_llm
from main_logic.cache import get_cached_menu, save_menu_to_cache

app = Flask(__name__)


@app.route('/summarize', methods=['POST'])
def summarize_menu():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    from datetime import date
    today = date.today().isoformat()

    cached = get_cached_menu(url, today)
    if cached:
        return jsonify(cached)

    html_content = scrape_menu_page(url)

    menu_data = extract_menu_with_llm(html_content, url, today)

    save_menu_to_cache(url, today, menu_data)

    return jsonify(menu_data)


if __name__ == '__main__':
    app.run(debug=True)
