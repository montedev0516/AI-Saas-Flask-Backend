import requests
from bs4 import BeautifulSoup

def extract_content(url):
    content=[]
    res = requests.get(url)
    htmlData = res.content
    soup = BeautifulSoup(htmlData, "html.parser")

    tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])

    for tag in tags:
        if tag.name == 'p':
            content.append(tag.get_text(strip=True) + " ")
        else:
            content.append(tag.name.upper() +": "+ tag.get_text(strip=True) + " ")
    
    return content