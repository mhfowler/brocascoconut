import re
import random
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from settings.common import getOrCreateS3Key, getS3Connection, getS3Credentials, getTrueSpeakBucket


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

