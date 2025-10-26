from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import re
from collections import OrderedDict

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
          "price": integer,
          "allergens": [string],
          "weight": string | null
        }}
      ],
      "daily_menu": true,
      "source_url": "{source_url}"
    }}
    """

    try:
        # 1️⃣ Call LLM
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )

        # 2️⃣ Extract plain text output
        raw_text = resp.output_text.strip()

        # 3️⃣ Remove Markdown fences if present (```json ... ```)
        cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_text, flags=re.MULTILINE).strip()

        # 4️⃣ Parse as JSON
        data = json.loads(cleaned)

        # 5️⃣ Ensure source_url + date exist
        data.setdefault("source_url", source_url)
        data.setdefault("date", date_str)

        # Ensure restaurant_name is first key in output
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





