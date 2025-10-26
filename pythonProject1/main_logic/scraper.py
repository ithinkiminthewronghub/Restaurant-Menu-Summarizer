import requests
from bs4 import BeautifulSoup


def scrape_menu_page(url: str) -> str:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(strip=True)


print(scrape_menu_page("https://www.spojka-karlin.cz/menu"))


