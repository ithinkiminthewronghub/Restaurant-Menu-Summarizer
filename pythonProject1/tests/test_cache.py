import os
import tempfile
import pytest
from main_logic import cache
from main_logic.cache import save_menu_to_cache, get_cached_menu, init_db
from main_logic.app import app

@pytest.fixture
def temp_cache_db():
    tmp_db = tempfile.NamedTemporaryFile(delete=False)
    cache.DB_PATH = tmp_db.name
    init_db()
    yield tmp_db.name
    tmp_db.close()
    os.unlink(tmp_db.name)

def test_cache_write_and_read(temp_cache_db):
    url = "https://test.example.com"
    date = "2025-10-25"
    data = {"restaurant_name": "Mock Café"}

    save_menu_to_cache(url, date, data)
    cached = get_cached_menu(url, date)

    assert cached["restaurant_name"] == "Mock Café"

def test_cache_prevents_duplicate_llm_calls(monkeypatch, temp_cache_db):
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

    # Second call uses cache → no new LLM call
    resp2 = client.post("/summarize", json={"url": url})
    assert resp2.status_code == 200
    assert call_count["llm"] == 1



