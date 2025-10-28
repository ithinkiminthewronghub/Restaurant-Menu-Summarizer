import os
import tempfile
import pytest
from main_logic import cache
from main_logic.cache import save_menu_to_cache, get_cached_menu, init_db
from main_logic.app import app


@pytest.fixture
def temp_cache_db():
    """
    Create a temporary SQLite database for cache testing.
    """
    tmp_db = tempfile.NamedTemporaryFile(delete=False)
    cache.DB_PATH = tmp_db.name
    init_db()
    yield tmp_db.name
    tmp_db.close()
    os.unlink(tmp_db.name)


def test_cache_write_and_read(temp_cache_db):
    """
    Test writing to and reading from the cache database.

    This test verifies that:
      - Menus are correctly saved into the cache.
      - Cached data can be read back accurately.
    """
    url = "https://test.example.com"
    date = "2025-10-25"
    data = {"restaurant_name": "Eowyn's Stew"}

    save_menu_to_cache(url, date, data)
    cached = get_cached_menu(url, date)

    assert cached["restaurant_name"] == "Eowyn's Stew"


def test_cache_prevents_duplicate_llm_calls(monkeypatch, temp_cache_db):
    """
    Test that the API uses cached results instead of calling the LLM repeatedly.

    This ensures:
      - The first request triggers the LLM to extract the menu.
      - Subsequent requests for the same URL/date use the cached result.
      - Prevents unnecessary API costs and delays.
    """
    client = app.test_client()
    call_count = {"llm": 0}

    def fake_scraper(url):
        return "<html>menu</html>"

    def fake_llm_parser(html, url, date):
        call_count["llm"] += 1
        return {
            "restaurant_name": "SPOJKA",
            "date": date,
            "day_of_week": "Monday",
            "menu_items": [],
            "daily_menu": True,
            "source_url": url,
        }

    monkeypatch.setattr("main_logic.app.extract_menu_with_llm", fake_llm_parser)
    monkeypatch.setattr("main_logic.app.scrape_menu_page", fake_scraper)

    url = "https://www.spojka-karlin.cz/menu"

    # First call triggers LLM
    resp1 = client.post("/summarize", json={"url": url})
    assert resp1.status_code == 200
    assert call_count["llm"] == 1

    # Second call uses cache, so no new LLM call
    resp2 = client.post("/summarize", json={"url": url})
    assert resp2.status_code == 200
    assert call_count["llm"] == 1



