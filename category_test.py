import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

BASE_URL = "https://www.winners.mu"

url = BASE_URL

response = requests.get(url)

print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

category_ids = set()

for link in soup.find_all("a", href=True):

    href = link["href"]

    if "/category/products" in href:

        parsed_url = urlparse(href)

        parameters = parse_qs(parsed_url.query)

        if "categoryId" in parameters:

            category_id = parameters["categoryId"][0]

            category_ids.add(category_id)

print("Category IDs found:")

for category_id in sorted(category_ids):
    print(category_id)