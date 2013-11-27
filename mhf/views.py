from django.http import HttpResponse
from django import shortcuts
from mhf.models import Stat
from django.shortcuts import render


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
    return render(request, 'home.html', {"stat":stat})
    #return HttpResponse(
    #    "<p>" + str(stat.number) + "</p>"
    #                                                          "<a href='/blog/'> go to the blog </a>")
    # return shortcuts.redirect("/blog/")