import random
import os

from django.http import HttpResponse

from settings.common import SECRETS_DICT
from bots.twitter_helper import TwitterHelper
from mhf.models import TwitterID

DIR_PATH = os.path.dirname(__file__)

latest_mention_file_path = os.path.join(DIR_PATH, 'latest_mention.txt')

trash_takers = [
    'hubbabhab',
    'jordibeard',
    'notplants'
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

LATEST_DM_ID_KEY = 'latest_dm_id'


access_token_key = SECRETS_DICT['TRASHBOT_TWITTER_ACCESS_TOKEN_KEY']
access_token_secret = SECRETS_DICT['TRASHBOT_TWITTER_ACCESS_TOKEN_SECRET']
consumer_key = SECRETS_DICT['TRASHBOT_TWITTER_CONSUMER_KEY']
consumer_secret = SECRETS_DICT['TRASHBOT_TWITTER_CONSUMER_SECRET']

twitter_helper = TwitterHelper(access_token_secret=access_token_secret, access_token_key=access_token_key,
                               consumer_key=consumer_key, consumer_secret=consumer_secret)


def trashBot(request):
    who_next = random.choice(trash_takers)
    saying = random.choice(sayings)
    twitter_helper.post_tweet(saying.format(who_next))
    return HttpResponse(': trash bot notified :')


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


def check_for_dms(previous_dm_id):
    latest_dms = twitter_helper.get_latest_dms(previous_dm_id)
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
    return HttpResponse(': checking for dms: {}'.format(previous_dm_id))


