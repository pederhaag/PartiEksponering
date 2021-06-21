from datetime import datetime
import bs4 as bs
import requests

import DB.DBAnalyzer as DB


num_articles = 3
obj = DB.DBAnalyzer(num_articles, block_size=2)
obj.get_article_info()
# obj.fetch_articles()
