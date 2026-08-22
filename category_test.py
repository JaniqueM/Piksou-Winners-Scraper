import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.winners.mu"
CATEGORY_URL = urljoin(BASE_URL, "/epicerie")

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

response = requests.get(
    CATEGORY_URL,
    headers=headers,
    timeout=30
)

print("Status:", response.status_code)
print("Length:", len(response.text))

soup = BeautifulSoup(response.text, "html.parser")

products = soup.select(".product-item")

print("Products found:", len(products))
print("\nPRODUCTS:\n")

for product in products:

    product_id = product.get("data-productid")

    name_element = product.select_one(".product-title a")
    sku_element = product.select_one(".sku")
    price_element = product.select_one(".actual-price")

    name = name_element.get_text(strip=True) if name_element else None

    product_url = (
        urljoin(BASE_URL, name_element.get("href"))
        if name_element and name_element.get("href")
        else None
    )

    sku = sku_element.get_text(strip=True) if sku_element else None
    price = price_element.get_text(strip=True) if price_element else None

    print("Product ID:", product_id)
    print("Name:", name)
    print("SKU:", sku)
    print("Price:", price)
    print("URL:", product_url)
    print("-" * 50)