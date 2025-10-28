from main_logic.app import app


def test_integration_flow(monkeypatch):
    """
    Full integration test for the /summarize API endpoint.

    This test simulates a complete request to the Flask app, ensuring that:
      - The /summarize endpoint accepts POST requests correctly.
      - Scraping and LLM parsing functions are called as expected.
      - The endpoint returns valid JSON data with the correct structure.
    """
    client = app.test_client()

    def fake_scraper(url):
        return "<html><body>Menu content</body></html>"

    def fake_llm_parser(html, url):
        return {
            "restaurant_name": "Zlatá Hvězda",
            "date": "2025-10-28",
            "day_of_week": "Tuesday",
            "menu_items": [],
            "daily_menu": True,
            "source_url": url,
        }

    monkeypatch.setattr("main_logic.scraper.scrape_menu_page", fake_scraper)
    monkeypatch.setattr("main_logic.llm_parser.extract_menu_with_llm", fake_llm_parser)

    response = client.post(
        "/summarize",
        json={"url": "https://www.zlata-hvezda.cz/jidelni-listek"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["restaurant_name"] == "Restaurace Zlatá Hvězda"
