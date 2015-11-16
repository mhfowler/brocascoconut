import oauth2 as oauth
import urllib2 as urllib
import json


class TwitterHelper():

    def __init__(self, access_token_key, access_token_secret, consumer_key, consumer_secret):
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

        _debug = 0

        self.oauth_token = oauth.Token(key=self.access_token_key, secret=self.access_token_secret)
        self.oauth_consumer = oauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)

        self.signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()


        self.http_handler  = urllib.HTTPHandler(debuglevel=_debug)
        self.https_handler = urllib.HTTPSHandler(debuglevel=_debug)

    '''
    Construct, sign, and open a twitter request
    using the hard-coded credentials above.
    '''
    def twitterreq(self, url, method, parameters):
        req = oauth.Request.from_consumer_and_token(self.oauth_consumer,
                                                 token=self.oauth_token,
                                                 http_method=method,
                                                 http_url=url,
                                                 parameters=parameters)

        req.sign_request(self.signature_method_hmac_sha1, self.oauth_consumer, self.oauth_token)

        headers = req.to_header()

        if method == "POST":
            encoded_post_data = req.to_postdata()
        else:
            encoded_post_data = None
            url = req.to_url()

        opener = urllib.OpenerDirector()
        opener.add_handler(self.http_handler)
        opener.add_handler(self.https_handler)

        response = opener.open(url, encoded_post_data)

        return response

    FILTER_LEVEL = "medium"
    def fetch_hashtag(self, hashtag):
        url = "https://api.twitter.com/1.1/search/tweets.json"
        parameters = [("q", hashtag), ("result_type","recent")]
        response = self.twitterreq(url, "GET", parameters)
        for line in response:
            parsed = json.loads(line)
            break
        return parsed


    def post_tweet(self, tweet_str):
        url = "https://api.twitter.com/1.1/statuses/update.json"
        parameters = [("status", tweet_str)]
        response = self.twitterreq(url, "POST", parameters)
        return response


    def post_tweet_with_image(self, tweet_text, img_screenshot_path):
        url = "https://api.twitter.com/1.1/statuses/update.json"
        parameters = [("status", tweet_text)]
        response = self.twitterreq(url, "POST", parameters)
        return response


    def get_latest_mentions(self, since_id):
        url = "https://api.twitter.com/1.1/statuses/mentions_timeline.json"
        if since_id:
            parameters = [("since_id", str(since_id))]
        else:
             parameters = []
        response = self.twitterreq(url, "GET", parameters)
        for line in response:
            parsed = json.loads(line)
            break
        return parsed


    def get_latest_dms(self, since_id):
        url = "https://api.twitter.com/1.1/direct_messages.json"
        if since_id:
            parameters = [("since_id", str(since_id))]
        else:
             parameters = []
        response = self.twitterreq(url, "GET", parameters)
        for line in response:
            parsed = json.loads(line)
            break
        return parsed