__author__ = 'maxfowler'

import requests
from settings.common import SECRETS_DICT

MAILGUN_KEY = SECRETS_DICT["MAILGUN_KEY"]

def send_mailgun_message(send_to_list, subject, message, from_name, from_email):
    result = requests.post(
        "https://api.mailgun.net/v2/brocascoconut.com/messages",
        auth=("api", MAILGUN_KEY),
        data={"from": from_name + "<" + from_email + ">",
              "to": send_to_list,
              "subject": subject,
              "text": message})
    return result
