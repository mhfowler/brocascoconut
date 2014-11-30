# python curl mailgun
import requests
from settings.common import SECRETS_DICT
MAILGUN_KEY = SECRETS_DICT["MAILGUN_KEY"]

import mailchimp

def create_receive_route():
    return requests.post(
        "https://api.mailgun.net/v2/routes",
        auth=("api", MAILGUN_KEY),
        data={"priority": 0,
              "description": "Receiving Email Route",
              "expression": "match_recipient('test@brocascoconut.com')",
              "action": ["forward('maxhfowler@gmail.com')", "stop()"]})


def testSendEmail():
    return requests.post(
        "https://api.mailgun.net/v2/brocascoconut.com/messages",
        auth=("api", MAILGUN_KEY),
        data={"from": "Excited User <testmax@brocascoconut.com>",
              "to": ["maxhfowler@gmail.com"],
              "subject": "Hello Hello",
              "text": "Testing some Mailgun awesomnessss!"})

# mailchimp subscribe
mailchimp_url = "https://us9.api.mailchimp.com/2.0/"
mailchimp_key = SECRETS_DICT["MAILCHIMP_KEY"]
mailchimp_data = {
    "apikey": mailchimp_key,
}
response = requests.post(mailchimp_url + "lists/list", data=mailchimp_data)
print response.content

# subscribe_data = {
#     "apikey": mailchimp_key,
#     "id": "e0e4391628",
#     "email": ("email", "max_fowler@brown.edu")
# }
#
# response = requests.post(mailchimp_url + "lists/subscribe", data=subscribe_data)
# print response.content

mchimp = mailchimp.Mailchimp(apikey=mailchimp_key)
mchimp.lists.subscribe(id="e0e4391628",email={"email":"maximusfowler@gmail.com"})
print "subscribed"



