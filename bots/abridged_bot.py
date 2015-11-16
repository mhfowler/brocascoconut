from settings.common import SECRETS_DICT

from bots.screenshot import get_screenshot_for_url

from bots.twitter_helper import TwitterHelper

import json
import smtplib
import urllib2
import time
import random
import numpy
import tweepy
import requests

from mhf.models import TwitterID


access_token_key = SECRETS_DICT['ABRIDGED_TWITTER_ACCESS_TOKEN_KEY']
access_token_secret = SECRETS_DICT['ABRIDGED_TWITTER_ACCESS_TOKEN_SECRET']
consumer_key = SECRETS_DICT['ABRIDGED_TWITTER_CONSUMER_KEY']
consumer_secret = SECRETS_DICT['ABRIDGED_TWITTER_CONSUMER_SECRET']


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)

abridged_base_url = 'http://brocascoconut.com/gmaps/'


def get_coords_from_place_string(place_str):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'sensor': 'false', 'address': place_str}
    r = requests.get(url, params=params)
    results = r.json()['results']
    location = results[0]['geometry']['location']
    return location['lat'], location['lng']


def tweet_coordinates(ab_url, lat, lon, zoom, tweet_text):
    ab_screenshot_path = get_screenshot_for_url(url=ab_url)
    api.update_with_media(status=tweet_text, filename=ab_screenshot_path)


if __name__ == '__main__':
    print 'abridged bot'
    place_str = 'Toronto, Canada'
    lat, lon = get_coords_from_place_string(place_str)
    print 'lat: {}, lon: {}'.format(lat, lon)
    zoom=15
    url = '{}{},{},{}/'.format(abridged_base_url, str(lat)[:6], str(lon)[:6], str(zoom))
    tweet_text = '{}\n{}'.format(place_str, url)
    # tweet_text = tweet_text[(len(tweet_text) - 140):]
    print 'tweet_text: {}'.format(tweet_text)
    tweet_coordinates(ab_url=url, lat=lat, lon=lon, zoom=zoom, tweet_text=place_str)
