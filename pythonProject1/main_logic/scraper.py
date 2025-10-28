import requests
from bs4 import BeautifulSoup


def scrape_menu_page(url: str) -> str | None:
    """
    Fetches and parses the HTML content of a restaurant's menu webpage.

    Args:
    url (str): The full URL of the restaurant menu page.

    Returns:
    str | None: Cleaned textual content from the page,
    or None if the request fails.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(strip=True)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to scrape {url}: {e}")
        return None


def is_menu_mostly_image(html: str) -> bool:
    """
    Detects if the menu page contains mostly images.

    Args:
    html (str): Raw HTML content of the menu page.

    Returns:
    bool: True if the page has very little text and at least one image tag,
              indicating an image-based menu.
    """
    soup = BeautifulSoup(html, "html.parser")
    text_content = soup.get_text(strip=True)
    images = soup.find_all("img")
    return len(text_content) < 100 and len(images) > 0
