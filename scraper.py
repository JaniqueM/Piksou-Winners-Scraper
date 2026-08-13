import requests #allows Python to communicate with the website 
from bs4 import BeautifulSoup #allows python to read and search the websites HTML 

url = "https://www.winners.mu/"
response = requests.get(url)
print(response.status_code)
print(response.text[:500]) #from the website, we printed the first 500 characters as a test of connection 

from bs4 import BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

print(soup.title)