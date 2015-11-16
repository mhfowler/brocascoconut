from settings.common import SECRETS_DICT

from bots.screenshot import get_screenshot_for_url

import os
import random
import tweepy
from pygeocoder import Geocoder
import requests

from mhf.models import TwitterID


DIR_PATH = os.path.abspath(os.path.dirname(__file__))


access_token_key = SECRETS_DICT['ABRIDGED_TWITTER_ACCESS_TOKEN_KEY']
access_token_secret = SECRETS_DICT['ABRIDGED_TWITTER_ACCESS_TOKEN_SECRET']
consumer_key = SECRETS_DICT['ABRIDGED_TWITTER_CONSUMER_KEY']
consumer_secret = SECRETS_DICT['ABRIDGED_TWITTER_CONSUMER_SECRET']


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)

abridged_base_url = 'http://abridgedmaps.com/'


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


def reverse_geocode(lat, lon):
    results = Geocoder.reverse_geocode(lat, lon)
    first_result = results[0]
    return first_result.formatted_address
    # data = first_result.data[0]
    # address_components = data['address_components']
    # return address_components[-2] + ', ' + address_components[-1]


def geocode_and_tweet(place_str):
    lat, lon = get_coords_from_place_string(place_str)
    print 'lat: {}, lon: {}'.format(lat, lon)
    zoom=14
    url = '{}{},{},{}/'.format(abridged_base_url, str(lat)[:6], str(lon)[:6], str(zoom))
    tweet_text = '{}\n{}'.format(place_str, url)
    # tweet_text = tweet_text[(len(tweet_text) - 140):]
    print 'tweet_text: {}'.format(tweet_text)
    tweet_coordinates(ab_url=url, lat=lat, lon=lon, zoom=zoom, tweet_text=place_str)


def reverse_geocode_and_tweet(lat, lon):
    place_str = reverse_geocode(lat=float(lat), lon=float(lon))
    zoom = 14
    url = '{}{},{},{}/'.format(abridged_base_url, str(lat)[:6], str(lon)[:6], str(zoom))
    tweet_text = u'{}\n{}'.format(place_str, url)
    print u'tweet_text: {}'.format(tweet_text)
    tweet_coordinates(ab_url=url, lat=lat, lon=lon, zoom=zoom, tweet_text=place_str)


def tweet_using_cities_file():
    cities_file_path = os.path.join(DIR_PATH, 'cities.csv')
    with open(cities_file_path, 'r') as cities_file:
        cities = []
        for line in cities_file:
            cities.append(line)

    # randomly choose
    which_city = random.choice(cities)
    lat, lon, city_name = which_city.split(',')
    reverse_geocode_and_tweet(lat=lat, lon=lon)


def tweet_using_world_cities_file():
    cities_file_path = os.path.join(DIR_PATH, 'world_cities.csv')
    with open(cities_file_path, 'r') as cities_file:
        cities = []
        for line in cities_file:
            cities.append(line)

    # randomly choose
    which_city = random.choice(cities)
    which_city = which_city.replace('"', '')
    num, country, city, lat, lon, _ = which_city.split(';')
    place_str = city + ', ' + country

    zoom=14
    url = '{}{},{},{}/'.format(abridged_base_url, str(lat)[:6], str(lon)[:6], str(zoom))
    tweet_text = '{}\n{}'.format(place_str, url)
    # tweet_text = tweet_text[(len(tweet_text) - 140):]
    print 'tweet_text: {}'.format(tweet_text)
    tweet_coordinates(ab_url=url, lat=lat, lon=lon, zoom=zoom, tweet_text=place_str)


if __name__ == '__main__':
    tweet_using_cities_file()
    # tweet_using_world_cities_file()


