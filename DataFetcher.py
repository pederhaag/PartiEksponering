
import bs4 as bs
# from bs4.diagnose import diagnose
# import urllib.request
from requests_html import HTMLSession
# import requests
import time


def write(s):
    f = open("temp.xml", "w", encoding='utf8')
    f.write(s)
    f.close()


URL = "https://www.dagbladet.no/nyheter/drapsmistenkt-bryter-tausheten/73905546"
# source = urllib.request.urlopen(URL).read()
session = HTMLSession()
resp = session.get(URL)
resp.content.decode('utf-8')
print(f'Response: {resp}')

# Rendring
print("Rendering...")
start_time = time.time()
resp.html.render()
print("--- %s seconds ---" % (time.time() - start_time))
print("Rendered!")
# soup = bs.BeautifulSoup(source, 'html5lib')
# soup = bs.BeautifulSoup(source, 'html.parser', parse_only=filtered_source)
soup = bs.BeautifulSoup(resp.html.html, 'lxml')
article = soup.find("body").find("article")
write(article.prettify())


ptags = article.find_all("p")
for p in ptags:
    print(p.contents)

# body = soup.find("body")
# article = body.find(class_ = "article-wrapper-L0n959")
# write(resp.html.html
