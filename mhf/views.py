from django.http import HttpResponse
from django import shortcuts
from mhf.models import Stat


def redirect(request, page='/home'):
    return shortcuts.redirect(page)


def viewWrapper(view):
    def new_view(request, *args, **kwargs):
        return view(request,*args,**kwargs)
    return new_view


def home(request):
    stat = Stat.xg.get_or_none(name="test")
    if not stat:
        stat = Stat(name="test")
        stat.save()
    else:
        stat.number += 1
        stat.save()
    return HttpResponse("Miley do what she want doe yup" + str(stat.number))
    # return shortcuts.redirect("/blog/")