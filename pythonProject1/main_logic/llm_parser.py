from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import re
from collections import OrderedDict

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def normalize_price(price_str):
    """Convert price string like '145,-', '145 Kč', or '145kc' into int (145)."""
    if isinstance(price_str, (int, float)):
        return int(price_str)
    if not isinstance(price_str, str):
        return None

    match = re.search(r"(\d+)", price_str.replace(",", "."))
    return int(match.group(1)) if match else None


def extract_menu_with_llm(text: str, source_url: str, date_str: str):
    """Extracts a structured menu from restaurant webpage text using the LLM."""

    no_allergens = r"Musíte se zeptat obsluhu"
    prompt = f"""
    You are a data extraction assistant. From the following restaurant webpage text,
    extract today's menu (date: {date_str}) in valid JSON format. If no allergens were found, write {no_allergens} 
    to the allergens field.
    IMPORTANT: Return only valid JSON — no markdown, no explanations.

    Text (truncated to 6000 chars):
    {text[:6000]}

    JSON schema:
    {{
      "restaurant_name": string,
      "date": "{date_str}",
      "day_of_week": string,
      "menu_items": [
        {{
          "category": string,
          "name": string,
          "price": integer | string,
          "allergens": [string],
          "weight": string | null
        }}
      ],
      "daily_menu": true,
      "source_url": "{source_url}"
    }}
    """

    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )

        raw_text = resp.output_text.strip()
        cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_text, flags=re.MULTILINE).strip()
        data = json.loads(cleaned)

        # Normalize prices here ---
        if "menu_items" in data and isinstance(data["menu_items"], list):
            for item in data["menu_items"]:
                if "price" in item:
                    item["price"] = normalize_price(item["price"])

        # Ensure defaults
        data.setdefault("source_url", source_url)
        data.setdefault("date", date_str)

        # Sort so restaurant_name is always first
        if isinstance(data, dict) and "restaurant_name" in data:
            data = OrderedDict(
                [("restaurant_name", data["restaurant_name"])]
                + [(k, v) for k, v in data.items() if k != "restaurant_name"]
            )

        return data

    except json.JSONDecodeError:
        print("JSON parsing failed. Raw model output:\n", raw_text)
        return {"error": "Invalid JSON returned by LLM", "raw_output": raw_text}

    except Exception as e:
        print("LLM extraction failed:", e)
        return {"error": str(e)}





