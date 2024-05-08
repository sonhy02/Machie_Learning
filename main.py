import requests
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/"
r = requests.get(URL)

soup = BeautifulSoup(r.text, "html.parser")
print(soup.prettify())