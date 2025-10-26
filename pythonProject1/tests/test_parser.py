
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_logic.llm_parser import extract_menu_with_llm


def test_extract_menu_with_llm_parses_valid_json(monkeypatch):
    """Test that markdown JSON from LLM is parsed correctly."""

    fake_response = """```json
    {
        "restaurant_name": "Bistro Republika",
        "date": "2025-10-26",
        "day_of_week": "Sunday",
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

    result = extract_menu_with_llm("<html></html>", "https://www.bistrorepublika.cz/menu", "2025-10-26")
    assert result["restaurant_name"] == "Bistro Republika"
    assert result["daily_menu"] is True
