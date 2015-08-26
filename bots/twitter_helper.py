import oauth2 as oauth
import urllib2 as urllib
import json

from settings.common import SECRETS_DICT

# See Assignment 1 instructions for how to get these credentials
access_token_key = SECRETS_DICT['TRASHBOT_TWITTER_ACCESS_TOKEN_KEY']
access_token_secret = SECRETS_DICT['TRASHBOT_TWITTER_ACCESS_TOKEN_SECRET']

consumer_key = SECRETS_DICT['TRASHBOT_TWITTER_CONSUMER_KEY']
consumer_secret = SECRETS_DICT['TRASHBOT_TWITTER_CONSUMER_SECRET']

_debug = 0

oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()


http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''
def twitterreq(url, method, parameters):
    req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                             token=oauth_token,
                                             http_method=method,
                                             http_url=url,
                                             parameters=parameters)

    req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

    headers = req.to_header()

    if method == "POST":
        encoded_post_data = req.to_postdata()
    else:
        encoded_post_data = None
        url = req.to_url()

    opener = urllib.OpenerDirector()
    opener.add_handler(http_handler)
    opener.add_handler(https_handler)

    response = opener.open(url, encoded_post_data)

    return response

FILTER_LEVEL = "medium"
def fetch_hashtag(hashtag):
    url = "https://api.twitter.com/1.1/search/tweets.json"
    parameters = [("q", hashtag), ("result_type","recent")]
    response = twitterreq(url, "GET", parameters)
    for line in response:
        parsed = json.loads(line)
        break
    return parsed


def post_tweet(tweet_str):
    url = "https://api.twitter.com/1.1/statuses/update.json"
    parameters = [("status", tweet_str)]
    response = twitterreq(url, "POST", parameters)
    return response
