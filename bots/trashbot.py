import random
from django import shortcuts
from django.http import HttpResponse

from bots.twitter_helper import fetch_hashtag, post_tweet

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
]

def trashBot(request):
    who_next = random.choice(trash_takers)
    saying = random.choice(sayings)
    post_tweet(saying.format(who_next))
    return HttpResponse(': trash bot notified :')
