import random, os
from django import shortcuts
from django.http import HttpResponse

from bots.twitter_helper import post_tweet, get_latest_mentions


DIR_PATH = os.path.dirname(__file__)

latest_mention_file_path = os.path.join(DIR_PATH, 'latest_mention.txt')

trash_takers = [
    '_coffee_banana',
    'jefffwii',
    'jordibeard'
]

sayings = [
    'plz take out the trash @{}',
    'yo trash @{}',
    'trash if you plz @{}',
    'hey @{}, plz trash',
    'trash trash trash @{}',
    'the trash isn\'t going to take out itself @{}',
    'plz help @{} SOS',
    '@{} the righteous man knows not what he wants but what he must do',
    'take the trash to its maker @{}',
    'yo @{}',
    'your time has come @{}',
    'you can do it if you believe @{}',
    'take no prisoners @{}',
    'sometimes you are called on @{}',
    'I kissed a girl and I liked it @{}',
    'lets get rooted @{}',
    'sorry @{}'
]


def trashBot(request):
    who_next = random.choice(trash_takers)
    saying = random.choice(sayings)
    post_tweet(saying.format(who_next))
    return HttpResponse(': trash bot notified :')


def get_latest_mention_id():
    if not os.path.isfile(latest_mention_file_path):
        return None
    with open(latest_mention_file_path, 'r') as latest_mention_file:
        contents = latest_mention_file.read()
        id = int(contents)
    return id


def save_latest_mention_id(id):
    with open(latest_mention_file_path, 'w') as latest_mention_file:
        latest_mention_file.write(str(id))


def check_for_mentions(previous_mention_id):
    latest_mentions = get_latest_mentions(previous_mention_id)
    if latest_mentions:
        mentions_by_trashtaker = []
        for mention in latest_mentions:
            user = mention['user']['screen_name']
            if user in trash_takers:
                mentions_by_trashtaker.append(mention)
        if mentions_by_trashtaker:
            latest_mention = mentions_by_trashtaker[0]
            new_id = latest_mention['id']
            save_latest_mention_id(new_id)
            trashBot(None)


def check_for_mentions_endpoint(request):
    previous_mention_id = get_latest_mention_id()
    check_for_mentions(previous_mention_id)
    return HttpResponse(': checking for mentions: {}'.format(previous_mention_id))