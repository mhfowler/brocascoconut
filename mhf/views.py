from django import shortcuts
from django.http import HttpResponse
from mhf.models import Stat
from django.core.mail import send_mail
from django.shortcuts import render
import random, os, re
from settings.common import PROJECT_PATH, SECRETS_DICT, ADMIN_EMAILS, getTrueSpeakBucket, getOrCreateS3Key
from django.views.decorators.csrf import ensure_csrf_cookie
from boto.s3.connection import S3Connection, Key
import stripe, json, mailchimp

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

def brocasCoconut(request):
    stat = getNumVisitors()
    return render(request, 'brocasCoconut.html', {"stat":stat})

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
    return render(request, 'capitalistTees.html')

def buyShirt(request):
    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here https://dashboard.stripe.com/account
    stripe_secret_key = SECRETS_DICT["STRIPE_SECRET_KEY"]
    stripe.api_key = stripe_secret_key

    # Get the credit card details submitted by the form
    json_token = request.POST['stripeToken']
    token = json.loads(json_token)
    user_email = token["email"]
    token_id = token["id"]
    color = request.POST["color"]
    size = request.POST["size"]
    cost = request.POST["cost"]
    address = request.POST["address"]
    costincents = int(cost) * 1000
    try:
        charge = stripe.Charge.create(
            amount=costincents, # amount in cents, again
            currency="usd",
            card=token_id,
            description=user_email
        )
        # successful charge
        sendOrderEmail(True, user_email, color, size, cost, address)
        return HttpResponse("success")
    except stripe.CardError, e:
        # The card has been declined
        sendOrderEmail(False, user_email, color, size, cost, address)
        return HttpResponse("failure")

# send an email about success or failure of order
def sendOrderEmail(success, email, color, size, cost, address):
    base_price = 15
    message = \
    "email: " + email + "\n" + \
    "color: " + color + "\n" + \
    "size: " + size + "\n" + \
    "number: " + str(int(cost)-base_price) + "\n" + \
    "cost: " + cost + "\n" + \
    "address: " + address + "\n"
    if success:
        subject = "Capitalist Tee Order Placed"
    else:
        subject = "Capitalist Tee Order Failure"
    send_mail(subject, message, 'order@robertmarvin.com',
    ADMIN_EMAILS, fail_silently=False)

# main pages
def art(request):
     return render(request, 'art.html')

def writing(request):
     return render(request, 'writing.html')

def about(request):
     return render(request, 'about.html')

def contact(request):
     return render(request, 'contact.html')

# truespeak ######################################################################################
def truespeak(request):
    names = getRecentlyOut()
    return render(request, 'truespeak.html', {"names":names})

def getRecentlyOut():
    to_return = []
    for key in getTrueSpeakRawKeys():
        try:
            name,appendage = key.name.split("|")
            name = name[4:] # remove the raw/ that it starts with
            url = name + "/" + appendage
            display_name = name.replace("_", " ")
            to_return.append({
                "url":url,
                "name":display_name,
                "date":key.last_modified
            })
        except Exception as e:
            pass
    to_return.sort(key=lambda x: x["date"], reverse=True)
    return to_return

def comparatorFun(x, y):
    if x and x[0].isalpha():
        if (not y) or (not y[0].isalpha()):
            return -1
        else:
            if (x > y):
                return 1
            else:
                return -1
    else:
        if y and y[0].isalpha():
            return 1
        else:
            if (x > y):
                return 1
            else:
                return -1


def truespeakPublicDetail(request, name, appendage):
    display_name = name.replace("_", " ")
    conversations = getConversations(name, appendage)
    people = [x[0] for x in conversations]
    return render(request, 'truespeakDetail.html', {"name":display_name, "conversations":conversations, "people":people})

@ensure_csrf_cookie
def truespeakSecretLink(request, name, appendage):
    display_name = name.replace("_", " ")
    conversations = getConversations(name, appendage)
    people = [x[0] for x in conversations]
    return render(request, 'truespeakDetail.html', {"name":display_name, "conversations":conversations, "people":people, "secret":True})


def publishTexts(request):
    current_url = request.POST["current_url"]
    result = re.match("^/secretlink/([A-z]+)/(\d+)/$", current_url)
    name = result.group(1)
    appendage = result.group(2)
    include_which = json.loads(request.POST["conversations"])
    publishConversations(name, appendage, include_which)
    return HttpResponse("published text history.")


def getConversations(name, appendage):
    key_name = "raw/" + name + "|" + appendage
    key, key_dict = getOrCreateS3Key(key_name)
    conversations = key_dict["conversations"]
    people = list(conversations.keys())
    people.sort(cmp=comparatorFun)
    to_return = []
    for person in people:
        conversation = conversations[person]
        to_return.append((person, conversation))
    return to_return


def publishConversations(name, appendage, include_which):
    key_name = "raw/" + name + "|" + appendage
    key, key_dict = getOrCreateS3Key(key_name)
    conversations = key_dict["conversations"]
    people = list(conversations.keys())
    published_conversations = {}
    for person in people:
        if person in include_which:
            published_conversations[person] = conversations[person]
    # now save to s3
    new_appendage = str(random.randint(0,100000000000))  # new appendage so they cant find the original
    public_key_name = "public/" + name + "|" + new_appendage
    public_key, public_key_dict = getOrCreateS3Key(public_key_name)
    published_conversations_json = json.dumps(published_conversations)
    public_key.set_contents_from_string(published_conversations_json)
    return published_conversations


# return all keys in the raw folder
def getTrueSpeakRawKeys():
    bucket = getTrueSpeakBucket()
    keys = bucket.list()
    keys_list = []
    for key in keys:
        name = key.name
        result = re.match("raw/.+", name)
        if result:
            keys_list.append(key)
    return keys_list