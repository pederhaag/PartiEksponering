#!/usr/bin/env python3

# Add parent folder to path
import sys
from pathlib import Path
file = Path(__file__).resolve()
package_root_directory = file.parents[1]
sys.path.append(str(package_root_directory))

import utilities.logging as lg

import DB.DBArticle as DB

import logging as log
import requests
from datetime import datetime
from requests_html import AsyncHTMLSession # HTMLSession
import bs4 as bs
import asyncio


class DBAnalyzer:


    # sitemap_URL = "https://www.dagbladet.no/sitemapindex.xml"
    sitemap_URL = "https://www.dagbladet.no/sitemap"
    sitemap_parser = "lxml"
    sitemaps = None

    def __init__(self, num_articles, block_size=3, verbose=True):
        self.num_articles = num_articles
        self.block_size = block_size
        self.sitemaps = [] # in use?
        self.articles = []
        self.fetch_limit = 10
        self.__init_logging(verbose)
        self.logger.info("DBAnalyzer initialized.")


    def __init_logging(self, verbose):
        # Settings
        logging_level = log.INFO if verbose else log.WARNING
        formatter = log.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Analyzer logger
        analyzer_handler = log.StreamHandler()
        analyzer_handler.setFormatter(formatter)
        self.logger = log.getLogger(__name__)
        self.logger.addHandler(analyzer_handler)
        self.logger.setLevel(logging_level)

        # Article logger
        article_handler = log.StreamHandler()
        article_handler.setFormatter(formatter)
        article_logger = log.getLogger("DB.DBArticle")
        article_logger.addHandler(article_handler)
        article_logger.setLevel(logging_level)

    def get_article_info(self):
        try:
            logger = self.logger
            articles_pulled = 0
            while (articles_pulled < self.num_articles):
                # Build request-parameters
                count = min(self.block_size, self.num_articles - articles_pulled)
                parameters = {"start" : articles_pulled, "count" : count, "pageType" : "front"}

                # Request sitemap
                logger.info("Requesting sitemap")
                response = requests.get(DBAnalyzer.sitemap_URL, params = parameters)
                response.raise_for_status()
                logger.info("Creating sitemap-soup")
                sitemap_soup = bs.BeautifulSoup(response.content,
                    DBAnalyzer.sitemap_parser)

                # Loop through articlelinks, generating DBArticle-objects
                logger.info("Retrieving URLs in soup")
                for article_node in sitemap_soup.find_all("url"):
                    article_URL = article_node.find("loc").get_text()
                    article_ts_iso = article_node.find("lastmod").get_text()
                    article_ts = datetime.fromisoformat(article_ts_iso)
                    logger.info(f"Creating article from {article_URL}")
                    self.articles.append(DB.DBArticle(article_URL, article_ts))

                articles_pulled += count
                logger.info(f"Articles retrieved: {articles_pulled}")
        except Exception as e:
            logger.exception("Exception occurred in method get_article_info")

    # def __fetch_batch(self, session, tasks):
    #     logger = self.logger
    #     logger.info(f"Fetching {len(tasks)} articles")


    def fetch_articles(self):
        logger = self.logger

        try:
            logger.info("Fetching articles from web")
            logger.info("Creating session")
            # Create session
            session = AsyncHTMLSession()

            # Create list of routines to call
            tasks = []
            for article in self.articles:
                article.session = session
                task = article.fetch
                tasks.append(task)

            # Fetch in batches
            while len(tasks) > 0:
                tasks_to_run = tasks[:self.fetch_limit]
                tasks = tasks[self.fetch_limit:]
                logger.info(f"Fetching {len(tasks_to_run)} articles")
                session.run(*tasks_to_run)

            logger.info("All articles fetched")

        except Exception as e:
            logger.exception("Exception occurred in method fetch_articles")

    def fetch_articles_std(self):
        try:
            from requests_html import HTMLSession # HTMLSession
            session = HTMLSession()
            for article in self.articles:
                article.session = session
                article.fetch_std()

        except Exception as e:
            logger.exception("Exception occurred in method fetch_articles")

    def __str__(self):
        # res = ""
        # [res = res + article + "\n" for article in self.articles]
        # return res
        return self.articles





if __name__ == "__main__":
    pass
    # from requests_html import HTMLSession
    # obj = DBAnalyzer(10)
    # obj.get_article_info()
    # obj.process_site_map(obj.sitemaps[0])
