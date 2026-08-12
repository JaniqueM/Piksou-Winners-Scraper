import requests #allows Python to communicate with the website 
from bs4 import BeautifulSoup #allows python to read and search the websites HTML 

url = "https://www.winners.mu/"
response = requests.get(url)
print(response.status_code)