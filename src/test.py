

import DB.DBAnalyzer as DB
import time


<<<<<<< HEAD
num_articles = 3
obj = DB.DBAnalyzer(num_articles, block_size=2)
=======
num_articles = 2
block_size = 10
obj = DB.DBAnalyzer(num_articles, block_size)
>>>>>>> main
obj.get_article_info()
###
start_time = time.time()
obj.fetch_articles()
# obj.fetch_articles_std()
duration = time.time() - start_time
print(f"Downloaded {num_articles} sites in {duration} seconds")
obj.articles[0].read()
