from main_logic.app import app
import os


def test_integration_flow(monkeypatch):
    """
    Full integration test for the /summarize API endpoint.

    Ensures that authentication, scraping, and parsing work end-to-end.
    """
    client = app.test_client()
    api_key = os.getenv("API_KEY")

    def fake_scraper(url):
        return "<html><body>Menu content</body></html>"

    def fake_llm_parser(html, url, date):
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
        headers={"Authorization": f"Bearer {api_key}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["restaurant_name"] == "Restaurace Zlatá Hvězda"
