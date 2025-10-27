import requests
from bs4 import BeautifulSoup


def scrape_menu_page(url: str) -> str | None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(strip=True)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to scrape {url}: {e}")
        return None


def is_menu_mostly_image(html: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    text_content = soup.get_text(strip=True)
    images = soup.find_all("img")
    return len(text_content) < 100 and len(images) > 0


