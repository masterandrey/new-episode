from webui.celeryapp import app
import logging

logger = logging.getLogger(__name__)


@app.task   #  soft_time_limit, time_limit
def add(x, y):
    # logger.error('There was some crazy error', exc_info=True, extra={
    #     # Optionally pass a request and we'll grab any information we can
    #     'request': (x, y),
    # })
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)