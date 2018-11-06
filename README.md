[![Build Status](https://travis-ci.org/masterandrey/TRegExpr.png)](https://travis-ci.org/masterandrey/TRegExpr)
# new-episode
Scrape data about new episodes of the movies you watch.

## Implementation details
I am using Python 3 with libraries:
* [Django](https://docs.djangoproject.com/en/2.1/intro/tutorial02/) for
rapid web-ui development

[Tried Celery](https://github.com/masterandrey/new-episode/commit/84b1f902e2bd37807a16f8b67358098998be9da6)
but choose [Channels](https://channels.readthedocs.io/en/latest/introduction.html) as more
lightweight and Django-centric approach.

## Installation

### Sentry
Error and logs in [sentry](https://docs.sentry.io/).
Overkill for the project, just for practice sake.

