

import DB.DBAnalyzer as DB


num_articles = 2
block_size = 2
obj = DB.DBAnalyzer(num_articles, block_size)
obj.get_article_info()
obj.fetch_articles()
