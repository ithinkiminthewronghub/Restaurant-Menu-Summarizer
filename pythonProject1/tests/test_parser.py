
import sys
import os
from main_logic.llm_parser import extract_menu_with_llm, normalize_price

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_extract_menu_with_llm_parses_valid_json(monkeypatch):
    """Test that markdown JSON from LLM is parsed correctly."""

    fake_response = """```json
    {
        "restaurant_name": "Bistro Republika",
        "date": "2025-10-27",
        "day_of_week": "Monday",
        "menu_items": [],
        "daily_menu": true,
        "source_url": "https://www.bistrorepublika.cz/menu"
    }
    ```"""

    class FakeResp:
        output_text = fake_response

    def fake_create(*args, **kwargs):
        return FakeResp()

    monkeypatch.setattr("main_logic.llm_parser.client.responses.create", fake_create)

    result = extract_menu_with_llm("<html></html>", "https://www.bistrorepublika.cz/menu", "2025-10-27")
    assert result["restaurant_name"] == "Bistro Republika"
    assert result["daily_menu"] is True


def test_normalize_price_variants():

    assert normalize_price("145 Kč") == 145
    assert normalize_price("145,-") == 145
    assert normalize_price("145kc") == 145
    assert normalize_price(145) == 145
    assert normalize_price("not available") is None
