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
    # return shortcuts.redirect("/machine_learning/")

# data science blog posts
def machine_learning(request):
    return render(request, 'cs195_assignment3.html', {})

def twitter_visualization(request):
    return render(request, 'cs195_assignment4/writeup.html', {})

def map_reduce(request):
    return render(request, 'map_reduce.html', {})
