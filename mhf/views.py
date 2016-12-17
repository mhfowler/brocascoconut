import random
import os
import json

from django import shortcuts
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import stripe
import mailchimp

from mhf.models import Stat
from bots.abridged_bot import DIR_PATH as BOT_PATH
from settings.common import PROJECT_PATH, SECRETS_DICT, ADMIN_EMAILS
from mhf.common import send_mailgun_message


# abridged space #######################################################################################################
@ensure_csrf_cookie
def abridged_space(request, coordinates=None):
    return render(request, 'abridged_space.html', {'coordinates': coordinates})

def abridged_space2(request, coordinates=None):
    return render(request, 'abridged_space2.html', {'coordinates': coordinates})

@csrf_exempt
def abridged_space_take_me_anywhere(request):
    cities_file_path = os.path.join(BOT_PATH, 'world_cities.csv')
    with open(cities_file_path, 'r') as cities_file:
        cities = []
        for line in cities_file:
            cities.append(line)

    # randomly choose
    which_city = random.choice(cities)
    which_city = which_city.replace('"', '')
    num, country, city, lat, lon, _ = which_city.split(';')
    if request.method == 'POST':
        place_str = city + ', ' + country
        return HttpResponse(json.dumps({
            'lat': lat,
            'lon': lon,
            'place_str': place_str
        }))
    else:
        return shortcuts.redirect('/gmaps/{},{},{}/'.format(str(lat), str(lon), '15'))

# boiler ###############################################################################################################
def vr_landing(request):
    return render(request, 'vr_landing.html')

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

def helloPage(request, image_url):
    return render(request, 'hello.html', {"background_image_url":image_url})

def bananaPage(request):
    return render(request, 'banana.html')

# data science blog posts ##############################################################################################
def machine_learning(request):
    return render(request, 'dataScienceClass/cs195_assignment3.html', {})

def twitter_visualization(request):
    return render(request, 'dataScienceClass/cs195_assignment4/writeup.html', {})

def map_reduce(request):
    return render(request, 'dataScienceClass/map_reduce.html', {})


# robert marvin ########################################################################################################
def monkeySkull(request):
    if request.COOKIES.get("brocas"):
        return shortcuts.redirect("/______/")
    else:
        response = render(request, 'monkeySkull.html')
        response.set_cookie("brocas", 666)
        return response

def brocasCoconut(request):
    stat = getNumVisitors()
    return render(request, 'brocasCoconut.html', {"stat":stat})

def loadingCrazy(request, page):
    stat = getNumVisitors()
    saying = getSaying()
    return render(request, 'loadingCrazy.html', {"saying":saying, "page":page})

def getSaying():
    sayings_file = os.path.join(PROJECT_PATH, "mhf/static/sayings.txt")
    with open(sayings_file, "r") as f:
        lines = []
        for line in f:
            line = line.replace("\n", "")
            lines.append(line)
        saying = random.choice(lines)
    return saying

@ensure_csrf_cookie
def theHome(request):
    stat = getNumVisitors()
    return render(request, 'theHome.html', {"stat":stat})

def submitEmail(request):
    email = request.POST["email"]
    mailchimp_key = SECRETS_DICT["MAILCHIMP_KEY"]
    mailchimp_id = SECRETS_DICT["MAILCHIMP_ID"]
    try:
        mchimp = mailchimp.Mailchimp(apikey=mailchimp_key)
        mchimp.lists.subscribe(id=mailchimp_id,email={"email":email})
        print "subscribed email: " + email
    except:
        print "error subscribing email: " + email
    return HttpResponse("yup")


# capitalist tees ######################################################################################################
def capitalistTees(request):
    return render(request, 'capitalistPrints.html')

def buyShirt(request):
    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here https://dashboard.stripe.com/account
    # stripe_secret_key = SECRETS_DICT["STRIPE_SECRET_TEST_KEY"]
    stripe_secret_key = SECRETS_DICT["STRIPE_SECRET_LIVE_KEY"]
    stripe.api_key = stripe_secret_key

    # Get the credit card details submitted by the form
    which_product = request.POST["which_product"]
    json_token = request.POST['stripeToken']
    token = json.loads(json_token)
    user_email = token["email"]
    token_id = token["id"]
    cost = request.POST["cost"]
    base_price = getBasePriceOfProduct(request)
    number = str(int(cost)-base_price)
    if number < 0: # they trying to hack!
        return HttpResponse("not today friend")
    costincents = int(cost) * 100
    try:
        charge = stripe.Charge.create(
            amount=costincents, # amount in cents, again
            currency="usd",
            card=token_id,
            description=user_email + ": " + which_product
        )
        # successful charge
        sendOrderEmail(True, request, user_email)
        return HttpResponse("success")
    except stripe.CardError, e:
        # The card has been declined
        sendOrderEmail(False, request, user_email)
        return HttpResponse("failure")

# send an email about success or failure of order to publisher and to the customer
def sendOrderEmail(success, request, email):
    which_product = request.POST["which_product"]
    color = request.POST["color"]
    shirtsize = request.POST["shirtsize"]
    bootysize = request.POST["bootysize"]
    printsize = request.POST["printsize"]
    cost = request.POST["cost"]
    address = request.POST["address"]
    base_price = getBasePriceOfProduct(request)
    number = str(int(cost)-base_price)
    message = \
        "product: " + which_product + "\n" + \
        "email: " + email + "\n" + \
        "color: " + color + "\n" + \
        "shirtsize: " + shirtsize + "\n" + \
        "printsize: " + printsize + "\n" + \
        "bootysize: " + bootysize + "\n" + \
        "number: " + number + "\n" + \
        "cost: " + cost + "\n" + \
        "address: " + address + "\n"
    receipt = False
    error = False
    if success:
        subject = "Capitalist Tee Order Placed"
        # send receipt to customer
        try:
            customer_subject = "Broca's Coconut Receipt"
            template = ""
            if which_product == "tshirt":
                template = "emails/tshirt_success.html"
            elif which_product == "print":
                template = "emails/print_success.html"
            elif which_product == "booty":
                template = "emails/booty_success.html"
            template_dict = request.POST.copy()
            template_dict["number"] = number
            customer_message = render(request, template, template_dict)
            result = send_mailgun_message(send_to_list=[email], subject=customer_subject, message=customer_message, from_name="Brocas Coconut", from_email="receipt@brocascoconut.com")
            receipt = True
        except Exception as e:
            pass
    else:
        try:
            customer_subject = "Broca's Coconut Order Failure"
            customer_message =  render(request, "emails/order_failure.html", request.POST)
            result = send_mailgun_message(send_to_list=[email], subject=customer_subject, message=customer_message, from_name="Brocas Coconut", from_email="error@brocascoconut.com")
            receipt = True
            error = True
        except Exception as e:
            pass
        subject = "Capitalist Tee Order Failure"
    # send email to publishers so they know to print it TODO: add order tracking
    message += "\nreceipt: " + str(receipt)
    message += "\nerror: " + str(error)
    result = send_mailgun_message(send_to_list=ADMIN_EMAILS, subject=subject, message=message, from_name="Brocas Coconut", from_email="neworder@brocascoconut.com")

# gets the base price of a product from what the product is
def getBasePriceOfProduct(request):
    which_product = request.POST["which_product"]
    printsize = request.POST["printsize"]
    base_price = None
    if which_product == "tshirt":
        base_price = 15
    elif which_product == "print":
        if printsize == "7x5":
            base_price = 15
        elif printsize == "20x16":
            base_price = 30
        elif printsize == "54x36":
            base_price = 200
    elif which_product == "booty":
        base_price = 10
    return base_price


# main pages
def art(request):
    return render(request, 'art.html')

def writing(request):
    return render(request, 'writing.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def projects(request):
    return render(request, 'projects.html')

def store(request):
    return render(request, 'store.html')


