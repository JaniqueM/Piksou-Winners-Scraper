import requests #allows Python to communicate with the website 
from bs4 import BeautifulSoup #allows python to read and search the websites HTML 

url = "https://www.winners.mu/"
response = requests.get(url)
print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

products = soup.find_all("h2", class_="product-title")

print("Number of products:", len(products))

for product_title in products:

    product = product_title.parent

    name = product_title.get_text(strip=True)

    sku_element = product.find("div", class_="sku")
    sku = sku_element.get_text(strip=True) if sku_element else "N/A"

    old_price_element = product.find("span", class_="old-price")
    old_price = old_price_element.get_text(strip=True) if old_price_element else "N/A"

    actual_price_element = product.find("span", class_="actual-price")
    actual_price = actual_price_element.get_text(strip=True) if actual_price_element else "N/A"

    link = product_title.find("a")["href"]

    print("--------------------")
    print("Name:", name)
    print("SKU:", sku)
    print("Old price:", old_price)
    print("Actual price:", actual_price)
    print("Link:", link)