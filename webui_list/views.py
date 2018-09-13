from django.http import HttpResponse
from webui_list.tasks import add
from webui_list.scrape_movie import scrape_movie


def list(request):
    add_task = add.delay(2, 2)  #  + str(add_task.get(timeout=1))
    scrape_movie()
    return HttpResponse("Hello: ")

