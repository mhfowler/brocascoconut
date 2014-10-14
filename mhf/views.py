from django import shortcuts
from django.http import HttpResponse
from mhf.models import Stat
from django.shortcuts import render
import random, os
from settings.common import PROJECT_PATH, SECRETS_DICT

# boiler ###############################################################################################################
def redirect(request, page='/home'):
    return shortcuts.redirect(page)

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
    return render(request, 'monkeySkull.html')

def robertMarvin(request):
    stat = getNumVisitors()
    return render(request, 'robertMarvin.html', {"stat":stat})

def loadingCrazy(request, page):
    stat = getNumVisitors()
    saying = getSaying()
    return render(request, 'loadingCrazy.html', {"saying":saying, "page":page})

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

def submitEmail(request):
    email = request.POST["email"]
    # TODO: save email
    return HttpResponse("yup")


# capitalist tees ######################################################################################################
def capitalistTees(request):
    return render(request, 'capitalistTees.html')

def buyShirt(request):
    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here https://dashboard.stripe.com/account
    stripe.api_key = SECRETS_DICT["STRIPE_SECRET_KEY"]

    # Get the credit card details submitted by the form
    token = request.POST['stripeToken']

    # Create the charge on Stripe's servers - this will charge the user's card
    try:
        charge = stripe.Charge.create(
            amount=100, # amount in cents, again
            currency="usd",
            card=token,
            description="payinguser@example.com"
        )
    except stripe.CardError, e:
        # The card has been declined
        pass
