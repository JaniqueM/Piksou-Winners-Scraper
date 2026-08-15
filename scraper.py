import requests #allows Python to communicate with the website 
from bs4 import BeautifulSoup #allows python to read and search the websites HTML 

url = "https://www.winners.mu/"
response = requests.get(url)
print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

product = soup.find("div", class_="product-item")

name = product.find("h2", class_="product-title")
price = product.find("span", class_="price actual-price")
print(name.text)
print(price.text)