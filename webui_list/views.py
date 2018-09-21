from django.http import HttpResponse
from webui_list.tasks import add
from webui_list.scrape_movie import scrape_movie
import logging

logger = logging.getLogger(__name__)


def list(request):
    add_task = add.delay(2, 2)  #  + str(add_task.get(timeout=1))
    #logger.error('from view')
    scrape_movie()
    return HttpResponse("Hello: ")

