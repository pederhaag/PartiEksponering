#!/usr/bin/env python3

# Add parent folder to path
import sys
from pathlib import Path
file = Path(__file__).resolve()
package_root_directory = file.parents[1]
sys.path.append(str(package_root_directory))


import bs4 as bs
from requests_html import HTMLSession
import re
import logging as log

class DBArticle:
    def __init__(self, URL, timestamp):
        self.URL = URL
        self.response = None
        self.html_content = None
        self.article = None
        self.text = None
        self.timestamp = timestamp
        self.logger = log.getLogger(__name__)

    def __str__(self):
        return f"URL: {self.URL}\tTimestamp: {self.timestamp}"

    def test(self): #Fjern
        self.fetch()
        soup = bs.BeautifulSoup(self.html_content.html, 'lxml')
        self.article = soup.find("body").find("article")
        # write(self.article.prettify())
        self.text = [VGArticle.clean(t.get_text()) for t in self.article.find_all(["h1", "h3", "p"])]
        print(self.text)

    @staticmethod
    def clean(t):
        # remove '\n' and '\t'
        t = re.sub("\\n|\\t", " ", t)
        # remove supurfluous whitespaces and return
        return re.sub("[ ]{2,}", " ", t.strip())


    def fetch(self):
        logger = self.logger
        session = HTMLSession()
        logger.info("HTMLSession created.")
        self.response = session.get(self.URL)
        logger.info("Response from server: " + str(self.response.status_code))

    def render(self):
        logger = self.logger
        self.response.content.decode("utf-8")
        self.response.html.render()
        logger.info("Rendering complete")
        self.html_content = self.response.html
