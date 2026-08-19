import requests #allows Python to communicate with the website 
from bs4 import BeautifulSoup #allows python to read and search the websites HTML 

url = "https://www.winners.mu/"
response = requests.get(url)

print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

products = soup.find_all("h2", class_="product-title")

print("Number of products:", len(products))

for product_title in products:
    print(product_title.get_text(strip=True))