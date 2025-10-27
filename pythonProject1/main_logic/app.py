from flask import Flask, request, jsonify
from main_logic.scraper import scrape_menu_page, is_menu_mostly_image
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
    if html_content is None:
        return jsonify({"error": "Failed to load menu page"}), 503
    if is_menu_mostly_image(html_content):
        return jsonify({"error": "Menu appears to be mostly in image form"}), 400

    menu_data = extract_menu_with_llm(html_content, url, today)

    save_menu_to_cache(url, today, menu_data)

    return jsonify(menu_data)


if __name__ == '__main__':
    app.run(debug=True)
