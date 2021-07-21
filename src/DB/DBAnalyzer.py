#!/usr/bin/env python3

import asyncio
from requests_html import AsyncHTMLSession  # HTMLSession
from datetime import datetime, timedelta, timezone
import bs4 as bs
from datetime import datetime
import requests
import re
import logging as log
import DB.DBArticle as DB
from Database.database_tools import build_lemma_translations, import_stopwords

# Add parent folder to path
import sys
from pathlib import Path
file = Path(__file__).resolve()
package_root_directory = file.parents[1]
sys.path.append(str(package_root_directory))


class DBAnalyzer:

    # sitemap_URL = "https://www.dagbladet.no/sitemapindex.xml"
    sitemap_URL = "https://www.dagbladet.no/sitemap"
    sitemap_parser = "lxml"
    sitemaps = None

    def __init__(self, num_articles, **kwargs):
        # default values
        self.block_size = 5
        self.verbose = True
        self.max_age_days = 100
        self.URL_filter = None
        self.fetch_limit = 10
        self.logging_level = log.INFO

        self.__dict__.update(kwargs)

        self.num_articles = num_articles
        self.sitemaps = []  # in use?
        self.articles = []

        self.__init_logging()

        if not hasattr(self, "excl_substrings_url"):
            path = str(Path(__file__).resolve().parents[0]) + "\exclusion_substrings_url.txt"
            self.excl_substrings_url = DBAnalyzer.__file_to_list(path)

        if not hasattr(self, "excl_re"):
            path = str(Path(__file__).resolve().parents[0]) + "\exclusion_regex.txt"
            self.excl_re = DBAnalyzer.__file_to_list(path)


        self.logger.debug("DBAnalyzer initialized.")

    def __init_logging(self):
        # Settings
        formatter = log.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Analyzer logger
        analyzer_handler = log.StreamHandler()
        analyzer_handler.setFormatter(formatter)
        self.logger = log.getLogger(__name__)
        self.logger.addHandler(analyzer_handler)
        self.logger.setLevel(self.logging_level)

        # Article logger
        article_handler = log.StreamHandler()
        article_handler.setFormatter(formatter)
        article_logger = log.getLogger("DB.DBArticle")
        article_logger.addHandler(article_handler)
        article_logger.setLevel(self.logging_level)

    def read_sitemap(self):
        try:
            logger = self.logger
            articles_pulled = 0
            URLs_checked = -1
            while (articles_pulled < self.num_articles):
                # Build request-parameters
                parameters = {"start": URLs_checked+1,
                              "count": self.block_size, "pageType": "article"}

                # Request sitemap
                logger.debug("Requesting sitemap")
                response = requests.get(
                    DBAnalyzer.sitemap_URL, params=parameters)
                response.raise_for_status()
                logger.debug("Creating sitemap-soup")
                sitemap_soup = bs.BeautifulSoup(response.content,
                                                DBAnalyzer.sitemap_parser)

                # Loop through articlelinks, generating DBArticle-objects
                logger.debug("Retrieving URLs in soup")
                for article_node in sitemap_soup.find_all("url"):
                    article_URL = article_node.find("loc").get_text()
                    article_ts_iso = article_node.find("lastmod").get_text()
                    article_ts = datetime.fromisoformat(article_ts_iso)
                    if self.check_age(article_ts) and self.relevant(article_URL):
                        logger.debug(f"Creating article from {article_URL}")
                        self.articles.append(
                            DB.DBArticle(article_URL, article_ts))
                        articles_pulled += 1
                        if articles_pulled == self.num_articles:
                            break
                    else:
                        logger.debug(f"Skipping {article_URL}")

                URLs_checked += self.block_size

            logger.info(f"Articles retrieved: {articles_pulled}")
        except Exception as e:
            logger.exception("Exception occurred in method get_article_info")

    def check_age(self, article_ts):
        age = datetime.today() - article_ts.replace(tzinfo=None)
        return age.days < self.max_age_days

    def set_log_level(self, level):
        self.logger.info("Setting logging level = " + str(level))
        self.logger.setLevel(level)

    def fetch_articles(self):
        logger = self.logger

        try:
            logger.info("Fetching articles from web")
            logger.debug("Creating session")
            # Create session
            session = AsyncHTMLSession()

            # Create list of routines to call
            tasks = []
            for article in self.articles:
                article.session = session
                task = article.afetch
                tasks.append(task)

            # Fetch in batches
            while len(tasks) > 0:
                tasks_to_run = tasks[:self.fetch_limit]
                tasks = tasks[self.fetch_limit:]
                logger.debug(
                    f"Fetching {len(tasks_to_run)} articles (Fetch limit: {self.fetch_limit})")
                session.run(*tasks_to_run)

            logger.info("All articles fetched")

        except Exception as e:
            logger.exception("Exception occurred in method fetch_articles")

    @staticmethod
    def __file_to_list(filepath):
        with open(filepath) as f:
            return f.read().splitlines()

    def relevant(self, URL):
        if self.URL_filter is not None:
            return self.URL_filter(URL)
        else:
            path = URL.split("dagbladet.no", 1)[1]
            for substring in self.excl_substrings_url:
                if substring in URL:
                    return False
            for regex in self.excl_re:
                if re.search(regex, URL):
                    return False

            return True

    def fetch_articles_std(self):
        logger = self.logger
        try:
            from requests_html import HTMLSession  # HTMLSession
            session = HTMLSession()
            for article in self.articles:
                article.session = session
                article.fetch_std()

        except Exception as e:
            logger.exception("Exception occurred in method fetch_articles")

    def __str__(self):
        return str(self.articles)


    def read_articles(self):
        logger = self.logger
        try:
            # Lemmatize each article
            for art in self.articles:
                logger.debug("Reading " + art.URL)
                art.read()
            logger.info(f"Finished reading {len(self.articles)} articles")
            
        except Exception as e:
            logger.exception("Exception occurred in method read_articles")

    def lemmatize_articles(self):
        logger = self.logger
        try:
            # Grab translation
            translations = build_lemma_translations()

            # Lemmatize each article
            for art in self.articles:
                logger.debug("Lemmatizing " + art.URL)
                art.lemmatize(translations)
            logger.info(f"Finished lemmatizing {len(self.articles)} articles")
            
        except Exception as e:
            logger.exception("Exception occurred in method lemmatize_articles")

    def create_wordcloud(self, use_articles = None, stopwords = import_stopwords()):
        logger = self.logger
        try:
            # Use self.articles unless otherwise specified
            articles = self.articles if use_articles == None else use_articles

            articles_words = []
            # Concatenate word from each article
            logger.info("Concatenate word from each article")
            for art in articles:
                logger.debug(f"Concatenating words in {art.URL}")
                articles_words.append(" ".join(word for word in art.text.GRUNNFORM))
            
            # Concatenate words into a single long string
            logger.info("Concatenate words into a single long string")
            words = " ".join(s for s in articles_words)
            print(words)
            
        except Exception as e:
            logger.exception("Exception occurred in method create_wordcloud")

    @staticmethod
    def __display_wordcloud(words):
        pass
