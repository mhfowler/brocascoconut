import random, os
from django.http import HttpResponse

from bots.twitter_helper import post_tweet, get_latest_dms
from mhf.models import TwitterID, Stat


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

LATEST_DM_ID_KEY = 'latest_dm_id'

def get_latest_dm_id():
    twitter_id = TwitterID.xg.get_or_none(key=LATEST_DM_ID_KEY)
    if twitter_id:
        return twitter_id.value
    else:
        return None


def save_latest_dm_id(dm_id):
    twitter_id = TwitterID.xg.get_or_none(key=LATEST_DM_ID_KEY)
    if not twitter_id:
        twitter_id = TwitterID(key=LATEST_DM_ID_KEY, value=dm_id)
    twitter_id.value = dm_id
    twitter_id.save()
    print 'dm_id: {}'.format(dm_id)


def save_latest_mention_id(id):
    with open(latest_mention_file_path, 'w') as latest_mention_file:
        latest_mention_file.write(str(id))


def check_for_dms(previous_dm_id):
    latest_dms = get_latest_dms(previous_dm_id)
    if latest_dms:
        dms_by_trashtaker = []
        for dm in latest_dms:
            user = dm['sender']['screen_name']
            if user in trash_takers:
                dms_by_trashtaker.append(dm)
        if dms_by_trashtaker:
            latest_dm = dms_by_trashtaker[0]
            new_id = latest_dm['id']
            save_latest_dm_id(new_id)
            trashBot(None)


def check_for_dms_endpoint(request):
    previous_dm_id = get_latest_dm_id()
    check_for_dms(previous_dm_id)
    return HttpResponse(': checking for mentions: {}'.format(previous_dm_id))