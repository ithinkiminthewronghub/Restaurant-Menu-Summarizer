from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import re
from collections import OrderedDict

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def normalize_price(price_str):
    """
    Convert price string like '145,-', '145 Kč', or '145kc' into int (145).

    Args:
    price_str (str | int | float): Raw price extracted from the menu text.

    Returns:
    int | None: Numeric price if found, otherwise None.
    """
    if isinstance(price_str, (int, float)):
        return int(price_str)
    if not isinstance(price_str, str):
        return None

    match = re.search(r"(\d+)", price_str.replace(",", "."))
    return int(match.group(1)) if match else None


def extract_menu_with_llm(text: str, source_url: str, date_str: str):

    """
    Extracts a structured menu from restaurant webpage text using the LLM.

    Args:
    text (str): Extracted webpage text.
    source_url (str): The original URL of the restaurant page.
    date_str (str): ISO date string.

    Returns:
    dict: Structured JSON object representing the restaurant menu, or
    an error message if parsing or LLM processing fails.
    """

    no_allergens = r"Please, ask the staff"
    prompt = f"""
    You are a data extraction assistant. From the following restaurant webpage text,
    extract today's menu (date: {date_str}) in valid JSON format. 
    
    If no allergens were found, write {no_allergens} to the allergens field.
    
    Please, check the ingredients in the description of the dish to see if the items are really 
    vegan/vegetarian/gluten-free. If there is any kind of bread or meat, the dish cannot be gluten-free 
    or vegetarian/vegan. If item is not vegan/vegetarian/gluten-free dishes, mark the corresponding field  as false. 
    
    IMPORTANT: Return only valid JSON — no markdown, no explanations.

    Text (truncated to 9000 chars):
    {text[:9000]}

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
          "vegan": boolean,
          "vegetarian": boolean,
          "gluten_free": boolean,
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
        # Cleaning the output so it would look nicer
        raw_text = resp.output_text.strip()
        cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_text, flags=re.MULTILINE).strip()
        data = json.loads(cleaned)

        # The price should look the same in the output
        if "menu_items" in data and isinstance(data["menu_items"], list):
            for item in data["menu_items"]:
                if "price" in item:
                    item["price"] = normalize_price(item["price"])

        data.setdefault("source_url", source_url)
        data.setdefault("date", date_str)

        # Ordering the data, so the restaurant name would always be the first
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





