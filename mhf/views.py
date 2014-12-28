from django import shortcuts
from django.http import HttpResponse
from mhf.models import Stat
from django.core.mail import send_mail
from django.shortcuts import render
import random, os, re
from settings.common import PROJECT_PATH, SECRETS_DICT, ADMIN_EMAILS, getTrueSpeakBucket, getOrCreateS3Key
from common import send_mailgun_message
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
    return render(request, 'newCapitalistTee.html')
    # return render(request, 'capitalistTees.html')

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
    costincents = int(cost) * 100
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

# send an email about success or failure of order to publisher and to the customer
def sendOrderEmail(success, email, color, size, cost, address):
    base_price = 10
    number = str(int(cost)-base_price)
    message = \
    "email: " + email + "\n" + \
    "color: " + color + "\n" + \
    "size: " + size + "\n" + \
    "number: " + number + "\n" + \
    "cost: " + cost + "\n" + \
    "address: " + address + "\n"
    receipt = False
    if success:
        subject = "Capitalist Tee Order Placed"
        # send receipt to customer
        try:
            customer_subject = "Capitalist T-Shirt Receipt"
            customer_message = "Thank you for your Capitalist T-Shirt Order! \n\n" + \
                "We received payment of " + cost + " dollars, and in less than a month we will print your shirt " + \
                "(size: " + size + ", color: " + color + ", number: " + number + ") and mail it to the address: \n\n" + address + \
                "\n\nIf you have any questions please send an email to questions@brocascoconut.com.\n\n" + \
                "Sincerely,\n\nBroca's Coconut \nhttp://brocascoconut.com"
            result = send_mailgun_message(send_to_list=[email], subject=customer_subject, message=customer_message, from_name="Brocas Coconut", from_email="receipt@brocascoconut.com")
            receipt = True
        except Exception as e:
            pass
    else:
        try:
            customer_subject = "Capitalist T-Shirt Order Failure"
            customer_message = "Thank you for your Capitalist T-Shirt order, \n" + \
                "Unfortunately there was some error processing your payment. \n\n" + \
                "You will not be charged and we will look into the issue, but sorry for the inconvenience." + \
                "\n\nIf you have any questions please send an email to questions@brocascoconut.com.\n\n" + \
                "Sincerely,\nBroca's Coconut \n\nhttp://brocascoconut.com"
            result = send_mailgun_message(send_to_list=[email], subject=customer_subject, message=customer_message, from_name="Brocas Coconut", from_email="error@brocascoconut.com")
            receipt = True
        except Exception as e:
            pass
        subject = "Capitalist Tee Order Failure"
    # send email to publishers so they know to print it
    if receipt:
        message += "\nreceipt successfully sent"
    result = send_mailgun_message(send_to_list=ADMIN_EMAILS, subject=subject, message=message, from_name="Brocas Coconut", from_email="neworder@brocascoconut.com")

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

# truespeak ######################################################################################
def truespeak(request):
    names = getRecentlyOut()
    return render(request, 'truespeak.html', {"names":names})

def getRecentlyOut():
    to_return = []
    for key in getTrueSpeakPublicKeys():
        try:
            name,appendage = key.name.split("|")
            name = name[7:] # remove the public/ that it starts with
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
    conversations = getConversations(name, appendage, public=True)
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
    obfuscations_map = json.loads(request.POST["include"])
    orig_username = request.POST["orig_username"]
    publishConversations(name, appendage, obfuscations_map, orig_username)
    return HttpResponse("published text history.")


def getConversations(name, appendage, public=False):
    if public == False:
        key_name = "raw/" + name + "|" + appendage
    else:
        key_name = "public/" + name + "|" + appendage
    key, key_dict = getOrCreateS3Key(key_name)
    conversations = key_dict["conversations"]
    people = list(conversations.keys())
    people.sort(cmp=comparatorFun)
    to_return = []
    for person in people:
        conversation = conversations[person]
        to_return.append((person, conversation))
    return to_return


def publishConversations(name, appendage, obfuscations_map, orig_username):
    key_name = "raw/" + name + "|" + appendage
    key, key_dict = getOrCreateS3Key(key_name)
    conversations = key_dict["conversations"]
    alias_username = name.replace("_"," ")
    people = list(conversations.keys())
    published_conversations = {}
    to_include = obfuscations_map.keys()
    for person in people:
        if person in to_include:
            obfuscated_name = obfuscations_map[person] or person
            obfuscated_conversation = obfuscate(conversations[person], person, obfuscated_name, orig_username, alias_username)
            published_conversations[obfuscated_name] = obfuscated_conversation
    # now save to s3
    new_appendage = str(random.randint(0,100000000000))  # new appendage so they cant find the original
    public_key_name = "public/" + name + "|" + new_appendage
    public_key, public_key_dict = getOrCreateS3Key(public_key_name)
    to_write = {
        "conversations":published_conversations,
        "username":alias_username
    }
    to_write_json = json.dumps(to_write)
    public_key.set_contents_from_string(to_write_json)
    return published_conversations


# return all keys in the raw folder
def getTrueSpeakPublicKeys():
    bucket = getTrueSpeakBucket()
    keys = bucket.list()
    keys_list = []
    for key in keys:
        name = key.name
        result = re.match("public/.+", name)
        if result:
            keys_list.append(key)
    return keys_list


def obfuscate(conversation, orig_convowith, alias_convowith, orig_username, alias_username):
    from_name_words = orig_convowith.split()
    to_name_words = alias_convowith.split()
    replace_mappings = {}
    # mappings for this conversation
    for index,name in enumerate(from_name_words):
        if len(to_name_words) > index:
            replace_mappings[name.lower()] = to_name_words[index]
        else:
            replace_mappings[name.lower()] = ""
    # mappings for username
    if orig_username and alias_username:
        orig_username_words = orig_username.split()
        username_alias_words = alias_username.split()
        for index,name in enumerate(orig_username_words):
            if len(username_alias_words) > index:
                replace_mappings[name.lower()] = username_alias_words[index]
            else:
                replace_mappings[name.lower()] = ""
    # obfuscate conversation
    for text in conversation:
        obfuscated_message = ""
        text_message = text["text_message"]
        if text_message:
            text_words = text_message.split()
        else:
            text_words = []
        for index,word in enumerate(text_words):
            # get alpha characters at start of word
            result = re.match("^([A-z]+)(.*)", word)
            if result:
                matching = result.group(1)
                extra = result.group(2)
            else:
                matching = word
                extra = ""
            replace_with = replace_mappings.get(matching.lower()) or matching
            replace_with = replace_with + extra
            if index > 0:
                obfuscated_message += " "
            obfuscated_message += replace_with
        text["text_message"] = obfuscated_message
        # replace to and from
        if text["from_name"] == orig_convowith:
            text["from_name"] = alias_convowith
            text["to_name"] = alias_username
        else:
            text["from_name"] = alias_username
            text["to_name"] = alias_convowith
    return conversation


