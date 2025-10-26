import os
import json
import sqlite3
from main_logic.cache import save_menu_to_cache, get_cached_menu, init_db
from main_logic.app import app


def test_cache_write_and_read(tmp_path):
    """Test saving and reading from cache."""
    test_db = tmp_path / "test_cache.db"
    os.environ["DB_PATH"] = str(test_db)

    init_db()

    url = "https://test.example.com"
    date = "2025-10-25"
    data = {"restaurant_name": "Mock Café"}

    save_menu_to_cache(url, date, data)
    cached = get_cached_menu(url, date)

    assert cached["restaurant_name"] == "Mock Café"


def test_cache_prevents_duplicate_llm_calls(monkeypatch):
    """Ensure that cached responses skip new LLM calls."""
    client = app.test_client()
    call_count = {"llm": 0}

    def fake_scraper(url):
        return "<html>menu</html>"

    def fake_llm_parser(html, url, date):
        call_count["llm"] += 1
        return {
            "restaurant_name": "SPOJKA",
            "date": date,
            "day_of_week": "Sunday",
            "menu_items": [],
            "daily_menu": True,
            "source_url": url,
        }

    monkeypatch.setattr("main_logic.scraper.scrape_menu_page", fake_scraper)
    monkeypatch.setattr("main_logic.llm_parser.extract_menu_with_llm", fake_llm_parser)

    url = "https://www.spojka-karlin.cz/menu"

    resp1 = client.post("/summarize", json={"url": url})
    assert resp1.status_code == 200

    resp2 = client.post("/summarize", json={"url": url})
    assert resp2.status_code == 200

    assert call_count["llm"] == 0




