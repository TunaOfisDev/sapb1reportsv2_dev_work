# html_scraper.py
import requests
from bs4 import BeautifulSoup

url = "https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/4505bc1c24a70489e10000000a155369.html?locale=tr-TR"
res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

# Başlık ve içerik bloklarını topla
for section in soup.find_all(["h1", "h2", "p", "li"]):
    text = section.get_text(strip=True)
    if text:
        print(text)
