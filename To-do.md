# To-do list:

* Caching?
* Exception handling
  * Invalid argument values
* Propper logging
  * Log level as attribute - kwargs
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
* GUI

# Next time:
* Download for source
* Build database
  * Strucutre
  * Lemmaing etc
* Wordclouds
