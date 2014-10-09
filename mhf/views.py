from django import shortcuts
from django.http import HttpResponse
from mhf.models import Stat
from django.shortcuts import render
import random, os
from settings.common import PROJECT_PATH
from django.views.decorators.csrf import csrf_exempt

# boiler ###############################################################################################################
def redirect(request, page='/home'):
    return shortcuts.redirect(page)

@csrf_exempt
def viewWrapper(view):
    def new_view(request, *args, **kwargs):
        return view(request,*args,**kwargs)
    return new_view


# home #################################################################################################################
def getNumVisitors():
    stat = Stat.xg.get_or_none(name="test")
    if not stat:
        stat = Stat(name="test")
        stat.save()
    else:
        stat.number += 1
        stat.save()
    return stat

def home(request):
    stat = getNumVisitors()
    return render(request, 'home.html', {"stat":stat})


# data science blog posts ##############################################################################################
def machine_learning(request):
    return render(request, 'dataScienceClass/cs195_assignment3.html', {})

def twitter_visualization(request):
    return render(request, 'dataScienceClass/cs195_assignment4/writeup.html', {})

def map_reduce(request):
    return render(request, 'dataScienceClass/map_reduce.html', {})


# robert marvin ########################################################################################################

def monkeySkull(request):
    stat = getNumVisitors()
    return render(request, 'monkeySkull.html', {"stat":stat})

def loadingCrazy(request):
    stat = getNumVisitors()
    saying = getSaying()
    return render(request, 'loadingCrazy.html', {"saying":saying})

def getSaying():
    sayings_file = os.path.join(PROJECT_PATH,"mhf/static/sayings.txt")
    with open(sayings_file, "r") as f:
        lines = []
        for line in f:
            line = line.replace("\n", "")
            lines.append(line)
        saying = random.choice(lines)
    return saying

def theHome(request):
    stat = getNumVisitors()
    return render(request, 'theHome.html', {"stat":stat})

@csrf_exempt
def submitEmail(request):
    email = request.POST["email"]
    # TODO: save email
    return HttpResponse("yup")


