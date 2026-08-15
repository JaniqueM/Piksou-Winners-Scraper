import requests #allows Python to communicate with the website 
from bs4 import BeautifulSoup #allows python to read and search the websites HTML 

url = "https://www.winners.mu/"
response = requests.get(url)
print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

product_text = soup.find(string=lambda text: text and "DANESITA" in text.upper())

print(product_text.parent.parent.parent)

product_title = soup.find("h2", class_="product-title")

product = product_title.parent

name = product_title.get_text(strip=True)

sku = product.find("div", class_="sku").get_text(strip=True)

old_price = product.find("span", class_="old-price").get_text(strip=True)

actual_price = product.find("span", class_="actual-price").get_text(strip=True)

link = product_title.find("a")["href"]

print("Name:", name)
print("SKU:", sku)
print("Old price:", old_price)
print("Actual price:", actual_price)
print("Link:", link)