#!/usr/bin/env python3


# from src.Database.database_tools import store_article_data
from requests_html import AsyncHTMLSession  # HTMLSession
from datetime import datetime, timedelta, timezone
import bs4 as bs
from datetime import datetime
import requests
import re
import logging as log
from itertools import chain

from wordcloud.wordcloud import WordCloud
import matplotlib.pyplot as plt
import DB.DBArticle as DB
import pandas as pd
import numpy as np
from Database.database_tools import *

# Add parent folder to path
import sys
from pathlib import Path
file = Path(__file__).resolve()
package_root_directory = file.parents[1]
sys.path.append(str(package_root_directory))


class DBAnalyzer:

    sitemap_URL = "https://www.dagbladet.no/sitemap"
    sitemap_parser = "lxml"
    sitemaps = None

    def __init__(self, **kwargs):
        # default values
        self.block_size = 250 # Size of sitemap to request in each batch
        self.max_age_days = 99 # For articles older than 100 days Dagbladet requires a log in
        self.URL_filter = None
        self.fetch_limit = 10
        self.logging_level = log.INFO
        self.articles = []

        self.__init_logging()
        self.__dict__.update(kwargs)

        if not hasattr(self, "excl_substrings_url"):
            path = str(Path(__file__).resolve().parents[0]) + "\exclusion_substrings_url.txt"
            self.excl_substrings_url = DBAnalyzer.__file_to_list(path)

        if not hasattr(self, "excl_re"):
            path = str(Path(__file__).resolve().parents[0]) + "\exclusion_regex.txt"
            self.excl_re = DBAnalyzer.__file_to_list(path)


        if hasattr(self, "num_articles") and hasattr(self, "use_urls"):
            raise ValueError("'num_articles' and 'use_urls' cannot both be passed!")

        elif hasattr(self, "use_urls") and not hasattr(self, "num_articles"):            
            [self.articles.append(DB.DBArticle(URL, None)) for URL in self.use_urls]
            self.num_articles = len(self.articles)

        elif not hasattr(self, "use_urls") and not hasattr(self, "num_articles"):
            raise ValueError("Either 'num_articles' or 'use_urls' must be passed!")

        

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

            if hasattr(self, "use_urls"):
                logger.info("No need for sitemap when 'use_urls'-parameter set.")
                logger.info(f"Articles URLs retrieved: {articles_pulled}")
            else:
                logger.info("Processing sitemaps")
                while (articles_pulled < self.num_articles):
                    # Build request-parameters
                    parameters = {"start": URLs_checked+1,
                                "count": self.block_size, "pageType": "article"}

                    # Request sitemap
                    logger.debug("Requesting a new sitemap")
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

                logger.info(f"Articles URLs retrieved: {articles_pulled}")
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

            
            # List of routines to call later with session
            tasks = []
            for article in self.articles:
                # Try to fetch data from database
                db_data, raw_text = fetch_from_database(article.URL)
                # If database has data, use it, else add task for fetching from web
                if len(db_data) > 0:
                    # Send the data to the article-object
                    article.give_data(db_data)
                    article.raw_text = raw_text
                    logger.debug(f"Retrieving {article.URL} from database.")
                else:
                    # Create tasks for web-fetching
                    article.session = session
                    task = article.afetch
                    tasks.append(task)
                    logger.debug(f"Creating task for fetching {article.URL} from the web.")

            # Fetch from web in batches
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

            if hasattr(self, "incl_substrings_url"):
                for inclusion_substring in self.incl_substrings_url:
                    if inclusion_substring in URL:
                        return True
                return False

            return True

    # Non-async version
    def fetch_articles_std(self):
        logger = self.logger
        try:
            from requests_html import HTMLSession  # HTMLSession
            session = HTMLSession()
            for article in self.articles:
                if not article.processed:
                    article.session = session
                    article.fetch_std()
                else:
                    logger.debug(f"Ignoring article {article.URL} already processed.")

        except Exception as e:
            logger.exception("Exception occurred in method fetch_articles")

    def __str__(self):
        return str(self.articles)

    # Get list of articles passed through filter
    def filter_articles(self, filter):
        logger = self.logger
        try:
            if not callable(filter):
                raise TypeError("Filter must be callable!")

            new_articles = []
            for art in self.articles:
                if filter(art):
                    new_articles.append(art)

            return new_articles
        except Exception as e:
            logger.exception("Exception occurred in method remove_articles")

    # Get list of articles where wordcount is less than passed minimum
    def filter_by_wordcount(self, minimum):
        filter = lambda article: article.get_number_of_words() < minimum
        return self.filter_articles(filter)

    # Remove list of articles
    def remove_articles(self, removeables):
        logger = self.logger
        try:
            new_articles = []
            for art in self.articles:
                if art not in removeables:
                    new_articles.append(art)
                else:
                    logger.debug(f"Marking {art.URL} for removal.")
            
            logger.info(f"Discarded {len(self.articles) - len(new_articles)} articles")
            self.articles = new_articles
        except Exception as e:
            logger.exception("Exception occurred in method remove_articles")

    def read_articles(self):
        logger = self.logger
        try:
            # Lemmatize each article
            for art in self.articles:
                if not art.processed:
                    logger.debug("Reading " + art.URL)
                    art.read()
                else:
                    logger.debug(f"Ignoring article {art.URL} already processed.")

            logger.info(f"Finished reading {len(self.articles)} articles")
            
        except Exception as e:
            logger.exception("Exception occurred in method read_articles")

    def lemmatize_articles(self):
        logger = self.logger
        try:
            logger.info("Starting to lemmatize articles")
            # Grab translation
            translations = build_lemma_translations()

            # Lemmatize each article
            for art in self.articles:
                if not art.processed:
                    logger.debug("Lemmatizing " + art.URL)
                    art.lemmatize(translations)
                else:
                    logger.debug(f"Ignoring article {art.URL} already processed.")
            logger.info(f"Finished lemmatizing {len(self.articles)} articles")
            
        except Exception as e:
            logger.exception("Exception occurred in method lemmatize_articles")

    def store_articles(self, refresh=False):
        logger = self.logger
        try:
            stored_count = 0
            for art in self.articles:
                if art.processed:
                    log_msgs = store_article_data(art, refresh=refresh)
                    for msg in log_msgs:
                        logger.debug(msg)
                    stored_count += 1
            
            logger.info(f"{stored_count} articles stored into database.")
            
        except Exception as e:
            logger.exception("Exception occurred in method store_articles")

    def wordcloud(self, use_articles = None, ignore_articles=[], stopwords = import_stopwords(), **kwargs):
        logger = self.logger
        try:
            # Use self.articles unless otherwise specified
            if use_articles == None:
                articles = self.articles
            else:
                if use_articles == []:
                    print("use_articles argumment cannot be an empty list!")
                    return None
                articles = use_articles
            
            # Ignore articles
            articles = [art for art in articles if art not in ignore_articles]

            articles_words = []
            # Concatenate word from each article
            logger.info("Concatenating word from each article")
            for art in articles:
                logger.debug(f"Concatenating words in {art.URL}")
                articles_words.append(" ".join(word for word in art.text.GRUNNFORM))
            
            # Concatenate words into a single long string
            logger.info("Concatenating words into a single long string")
            words = " ".join(s for s in articles_words)
            
            # Display
            DBAnalyzer.__display_wordcloud(WordCloud(stopwords=stopwords).generate(words))
            
        except Exception as e:
            logger.exception("Exception occurred in method create_wordcloud")

    @staticmethod
    def merge_article_data(articles):
        # Get all tags presents in articles
        categories = set(chain.from_iterable(art.tags for art in articles))
        
        data = pd.DataFrame(columns=["GRUNNFORM"]+list(categories))
        for art in articles:
            art_df = art.text.drop(columns=["WORD"])
            for tag in art.tags:
                art_df[tag] = True
            data = data.append(art_df, ignore_index=True)
        
        return data

    def categorize_url(self):
        self.clear_categories()

        for art in self.articles:
            match = re.search("dagbladet\.no/(.*?)/", art.URL)
            if match:
                art.set_tag(match[1])
            else:
                art.clear_tags()

    def categorize_party(self, max_candidate_number = 3):
        logger = self.logger

        self.clear_categories()

        logger.debug("Import data on politicians.")
        pol_df = import_politicians()

        # Only consider the politicians based on candidate number
        pol_df = pol_df[pol_df["kandidatnr"] <= max_candidate_number]

        logger.debug(f"Starting to categorize.")

        # container for the categorizations
        categorizations = dict()
        for party in pol_df["partikode"].unique():
            categorizations[party] = []

        party_names = {
                    "A" : ["AP", " Ap ", "Arbeiderpartiet", "Arbeidarpartiet"],
                    "FNB" : ["FNB", "Folkeaksjonen Nei til mer bompenger"],
                    "FRP" : ["FRP", "Fremskrittspartiet", "FrP", "Framstegspartiet"],
                    "H" : ["Høyre", "Høgre"],
                    "KRF" : ["KRF", "KrF", "Kristelig Folkeparti", "Kristeleg Folkeparti"],
                    "MDG" : ["MDG", "Miljøpartiet De Grønne", "Miljøpartiet Dei Grøne"],
                    "RØDT" : ["Rødt", "Raudt"],
                    "SP" : ["SP", " Sp ", "Senterpartiet"],
                    "SV" : ["SV", " Sv ", "Sosialistisk Venstreparti"],
                    "V" : ["Venstre"]
                }
        for i, article in enumerate(self.articles):

            logger.debug(f"Categorizing ({i+1}/{len(self.articles)}) {article.URL}")
            # For each party....
            for party in pol_df["partikode"].unique():
                # Search for representatives' name in article
                for name in pol_df[pol_df["partikode"] == party]["navn"]:
                    if name in article.raw_text:
                        categorizations[party].append(article)
                        break # No need to scan for further for the same party

                # If not already classified, look for party name/abbreviations
                if article not in categorizations[party]:
                    for party_name in party_names[party]:
                        if party_name in article.raw_text:
                            categorizations[party].append(article)
                            break # No need to scan for further for the same party
        
        
        # Set tags on articles
        for party in categorizations:
            for article in categorizations[party]:
                article.set_tag(party)
        logger.info("Categorizations complete")

    
    def clear_categories(self):
        [art.clear_tags() for art in self.articles]
        self.logger.info("Cleared tags for all articles.")

    def frequency_plot(self, **kwargs):
        logger = self.logger
        try:


            # Use self.articles unless otherwise specified
            articles = kwargs.get("use_articles", self.articles)
            
            # Ignore articles
            articles = [art for art in articles if art not in kwargs.get("ignore_articles", [])]

            # Merge data-sets
            logger.debug("Merging data from articles")
            if kwargs.get("only_categorized", False):
                articles = [art for art in articles if art.is_tagged()]
            data = DBAnalyzer.merge_article_data(articles)

            # Ensure all lowercase
            data["GRUNNFORM"] = data["GRUNNFORM"].str.lower()

            # Remove stopwords
            stopwords = kwargs.get("stopwords", import_stopwords())
            logger.debug("Removing stopwords")
            data = data[~data["GRUNNFORM"].isin(stopwords)]

            # Pass through filters - filters
            words_to_filter = []
            for filter in kwargs.get("filters", []):
                for word in data["GRUNNFORM"]:
                    if filter(word): words_to_filter.append(word) 
            if len(words_to_filter) > 0:
                data = data[~data["GRUNNFORM"].isin(set(words_to_filter))]
            

            total_number_of_words = len(data["GRUNNFORM"])
            total_number_of_articles = len(articles)

            # Get n most frequent words
            n = kwargs.get("n", 20)
            logger.debug(f"Retrieving {n} most popular words across all articles")
            words_to_model = data["GRUNNFORM"].value_counts()[:n].index.tolist()
            
            # Gather plot data
            categories = data.columns.tolist()[1:]
            counting_data = []
            for category in categories:
                # Get series of words for the given category
                words = data.query(f"{category}==True")["GRUNNFORM"]

                # Do a normalized count
                logger.debug(f"Counting words in category '{category}'")
                counts = words.value_counts(normalize=True)

                # Add data to a dataframe used in plot
                logger.debug(f"Adding data from category '{category}' to plot")
                counting_data.append([counts.get(word, 0) for word in words_to_model])
                
            counting_df = pd.DataFrame(counting_data).transpose().rename(columns=lambda i: categories[i])

            # Create plot
            logger.info("Creating frequency plot")
            plot = counting_df.plot(kind = "bar", ylabel="Realtive frequency of word", xlabel="Word")
            plot.set_xticklabels(words_to_model)
            if "title" in kwargs:
                plt.title(kwargs.get("title"))
            else:
                plt.title(
                    f"Frequency plot for n = {n} most frequent words.\n"
                    f"Total number of words {total_number_of_words} from {total_number_of_articles} articles."
                )
            plt.show()
             
        except Exception as e:
            logger.exception("Exception occurred in method frequency_plot")


    @staticmethod
    def __display_wordcloud(wordcloud, title = None):
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")

        plt.show()
