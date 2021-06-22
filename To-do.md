# To-do list:

* Caching?
* Exception handling
  * Invalid argument values
* Propper logging **Ongoing**
* Request delay / Batching **Ongoing**
  * Batching has been implemented in fetch_articles()
* Article might not need soup? See https://docs.python-requests.org/projects/requests-html/en/latest/
* Async / Concurrency ?
  * Implementing a common session in analyzer-class?
  * https://realpython.com/python-concurrency/#what-is-concurrency
  * Remember request-delays!
  * fetch is I/O Bound but render is CPU bound?
    * Therefore split fetch and render and design them differently?
* Methods for analysis:
  * Most common words
    * Blacklist
  * Wordclouds
* Documentation

# Next time:
* Logic for identifying relevant URLs
  * Use some sort of filter function? Static: DBArticle.filter()
