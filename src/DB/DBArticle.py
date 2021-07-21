#!/usr/bin/env python3

# Add parent folder to path
import sys
from pathlib import Path

from pandas.core.frame import DataFrame
file = Path(__file__).resolve()
package_root_directory = file.parents[1]
sys.path.append(str(package_root_directory))


import bs4 as bs
from requests_html import AsyncHTMLSession, HTMLSession #Needed?
import re
import regex # for propper unicode
import logging as log
import pandas as pd

class DBArticle:
    def __init__(self, URL, timestamp = None):
        self.URL = URL
        self.response = None
        self.html_content = None
        self.article = None
        self.text = None
        self.timestamp = timestamp
        self.logger = log.getLogger(__name__)

    def __str__(self):
        return f"URL: {self.URL}\tTimestamp: {self.timestamp}"



    @staticmethod
    def clean(t):
        # remove '\n' and '\t'
        t = regex.sub("\\n|\\t", " ", t)
        # remove unwanted characters
        t = regex.sub("[^\w \ ]", "", t, re.UNICODE)
        # remove supurfluous whitespaces and return
        # return re.sub("[ ]{2,}", " ", t.strip())
        return t.lower()

    def read(self):
        # TODO: Needs try-catch
        soup = bs.BeautifulSoup(self.response.html.html, 'lxml')
        self.article = soup.find("body").find("article")
        if self.article is not None:
            # self.text = []
            text = []
            for node in self.article.find_all(["h1", "h3", "p"]):
                # self.text += DBArticle.clean(node.get_text()).split()
                text += DBArticle.clean(node.get_text()).split()
            self.text = pd.DataFrame(text, columns=["WORD"])
            # self.text = [DBArticle.clean(t.get_text()).split() for t in self.article.find_all(["h1", "h3", "p"])]

    def lemmatize(self, translations):
        self.text = self.text.merge(translations, left_on="WORD", right_on="OPPSLAG", how="left")
        self.text.drop(columns=["OPPSLAG"], inplace=True)
        # self.text.apply(DBArticle.lemma_cleaner, )
        self.text.GRUNNFORM.fillna(self.text.WORD, inplace=True)

    # @staticmethod
    # def lemma_cleaner(data):
    #     if data[1] == "NaN":
    #         return [data[0], data[0]]
    #     return data

    async def afetch(self):
        try:
            logger = self.logger
            # Send request
            self.response = await self.session.get(self.URL)
            status_code = self.response.status_code
            if status_code != 200:
                logger.exception(f"Server returned status code {status_code}")
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



    # def render(self):
    #     logger = self.logger
    #     self.response.content.decode("utf-8")
    #     self.response.html.render()
    #     logger.info("Rendering complete")
    #     self.html_content = self.response.html
