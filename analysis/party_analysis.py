# Add parent and 'src folder to path
import sys
from pathlib import Path
file = Path(__file__).resolve()
package_root_directory = file.parents[1]
sys.path.append(str(package_root_directory))
sys.path.append(str(package_root_directory)+"\src")

# Imports
from src.DB.DBAnalyzer import DBAnalyzer
import logging as log

# If not already done, be sure to download sources for analysis,
# i.e. 'Ordbank' and 'valglister' (/src/Database/sources/download_sources.py)

#######################################################
# Grab up to 500 articles containing '/meninger/' in URL
#######################################################
analyzer = DBAnalyzer(num_articles = 500, logging_level = log.DEBUG,
    incl_substrings_url = ["/meninger/"])

# Initialize article-data
analyzer.read_sitemap()
analyzer.fetch_articles()
analyzer.read_articles()

# Lemmatize
analyzer.lemmatize_articles()

# Store fetched articles into database for future usage
analyzer.store_articles()


# Search for references to political parties in the
# contents of the articles
categories = analyzer.categorize_party()

# Grab the articles with a wordcount less than 100 words
short_articles = analyzer.filter_by_wordcount(100)

# Display figures on screen?
display_figures = False

############### Frequency plot ###############
# Consider the 20 words where the std. dev
# between the different parties is the largest
title = f"'std_n'={15} - {len(analyzer.articles) - len(short_articles)} articles read"
analyzer.frequency_plot(std_n = 15,
        only_categorized=True,
        ignore_articles=short_articles,
        save="FreqPlot",
        title=title,
        display = display_figures
        )

############### WordClouds ###############
for party in categories:
    analyzer.wordcloud(only_categorized=True,
        ignore_articles=short_articles,
        category=party, mask=party, save=party+"Masked",
        display = display_figures)
