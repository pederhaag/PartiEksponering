

import DB.DBAnalyzer as DB
import time
import logging
from Visuals.Visualizer import Visualizer
# import Visuals.Visualizer as Visualizer


num_articles = 1
obj = DB.DBAnalyzer(num_articles, block_size = 5, logging_level = logging.WARNING)
obj.build_articles()
obj.fetch_articles()
a = obj.articles[0]
a.read()
print(a.text)
Visualizer.wordcloud([a])
###
# start_time = time.time()
# obj.fetch_articles()
# # obj.fetch_articles_std()
# duration = time.time() - start_time
# print(f"Downloaded {num_articles} sites in {duration} seconds")
# [print(a.URL) for a in obj.articles]
