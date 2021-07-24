#!/usr/bin/env python3

# Add parent folder to path
from Database.database_tools import build_lemma_translations
import sys
from pathlib import Path

from pandas.core.frame import DataFrame
file = Path(__file__).resolve()
package_root_directory = file.parents[1]
sys.path.append(str(package_root_directory))


import bs4 as bs
from requests_html import AsyncHTMLSession, HTMLSession #Needed?
import re
import regex # for proper unicode
import logging as log
import pandas as pd

class DBArticle:
    def __init__(self, URL, timestamp = None):
        self.URL = URL
        self.response = None
        self.html_content = None
        self.article = None
        self.text = None
        self.raw_text = None
        self.timestamp = timestamp
        self.logger = log.getLogger(__name__)
        self.tags = ["Undef"]
        self.processed = False

    def __str__(self):
        return f"URL: {self.URL}\tTimestamp: {self.timestamp}"

    def give_data(self, data):
        self.text = data
        self.processed = True

    @staticmethod
    def clean(t):
        
        # remove '\n' and '\t'
        t = regex.sub("\\n|\\t", " ", t)
        # remove unwanted characters
        t = regex.sub("[^\w \ ]", "", t, re.UNICODE)
        return t.lower()
    
    

    @staticmethod
    def valid_node(n):
        # TODO: Needs try-catch
        # This method is used to exclude nodes with text not
        # relating to the subject of the article
        # - i.e. advertising related
        exclusions = [
            "aller",
            "ads-setting",
            "ad-",
            "css-pp-body"
        ]
        if "class" in n.attrs:
            for keyword in exclusions:
                for class_ in n.attrs["class"]:
                    if keyword in class_:
                        return False

        return True

    def get_number_of_words(self):
        return len(self.text.GRUNNFORM)

    def clear_tags(self):
        self.tags = ["Undef"]

    def set_tag(self, tag):
        if "Undef" in self.tags:
            self.tags = [tag]
        else:
            self.tags.append(tag)

    def has_tag(self, tag):
        return tag in self.tags

    def read(self):
        soup = bs.BeautifulSoup(self.response.html.html, 'lxml')
        self.article = soup.find("body").find("article")
        if self.article is not None:
            self.raw_text = ""
            text = []
            for node in self.article.find_all(["h1", "h3", "p"]):
                if DBArticle.valid_node(node):
                    text += DBArticle.clean(node.get_text()).split()
                    self.raw_text += " " + node.get_text()
            self.text = pd.DataFrame(text, columns=["WORD"])

    def lemmatize(self, translations = build_lemma_translations()):
        self.text = self.text.merge(translations, left_on="WORD", right_on="OPPSLAG", how="left")
        self.text.drop(columns=["OPPSLAG"], inplace=True)
        self.text.GRUNNFORM.fillna(self.text.WORD, inplace=True)
        self.processed = True


    async def afetch(self):
        try:
            logger = self.logger
            # Send request
            self.response = await self.session.get(self.URL)
            status_code = self.response.status_code
            if status_code != 200:
                logger.exception(f"Server returned status code {status_code}. URL = {self.url}")
            logger.debug(f"Response from server: {status_code}")

            # Render page
            await self.response.html.arender()
            logger.debug("Rendering complete")

        except Exception as e:
            logger.exception(f"Exception when fetching {self.URL}")


    def fetch(self):
        try:
            logger = self.logger
            # Send request
            session = HTMLSession()
            self.response = session.get(self.URL)
            status_code = self.response.status_code
            if status_code != 200:
                logger.exception(f"Server returned status code {status_code}")
            logger.debug(f"Response from server: {status_code}")

            # Render page
            self.response.html.render()
            logger.debug("Rendering complete")

        except Exception as e:
            logger.exception(f"Exception when fetching {self.URL}")


