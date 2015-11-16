from django import shortcuts
from django.http import HttpResponse
from mhf.models import Stat
from django.core.mail import send_mail
from django.shortcuts import render
from bots.abridged_bot import DIR_PATH as BOT_PATH
import random, os, re
from settings.common import PROJECT_PATH, SECRETS_DICT, ADMIN_EMAILS, getTrueSpeakBucket, getOrCreateS3Key
from common import send_mailgun_message
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from boto.s3.connection import S3Connection, Key
import stripe, json, mailchimp


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
    place_str = city + ', ' + country
    return HttpResponse(json.dumps({
        'lat': lat,
        'lon': lon,
        'place_str': place_str
    }))

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


