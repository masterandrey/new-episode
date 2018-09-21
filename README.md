# new-episode
Scrape data about new episodes of the serial movies you watch.

## Implementation details
I am using Python 3 with libraries:
* [Django](https://docs.djangoproject.com/en/2.1/intro/tutorial02/) for
rapid web-ui development
* [Celery](http://www.celeryproject.org/) as async task engine (of cause
this is overkill for the project, I just wanted to learn it). As broker for
Clery I am using [RabbitMQ](https://www.rabbitmq.com/), and Django as backend.
* [Scrapy](https://scrapy.org/) to scrape data from torrent index sites - again
I could use just lxml as well but I want take a look at this library as well.

## Installation

### RabbitMQ

[RabbitMQ](https://www.rabbitmq.com/)
And do not forget to run the server. 
For MacOS:

    brew services start rabbitmq

### Celery
Do not forget to run worker (from the project folder) with default hard 
timeout 30 seconds

    celery -E -A webui worker -l info --time-limit 30 --loglevel=INFO
    
### Sentry
Error and logs in [sentry](https://docs.sentry.io/).
Again - overkill for the project, just for practice sake.
