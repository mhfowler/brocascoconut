from settings.common import SECRETS_DICT

import json
import smtplib
import urllib2
import time
import random
import numpy

from mhf.models import TwitterID


PS1_ID_KEY = 'ps1_id'
PS1_DATE_KEY = 'ps1_date'

PS1_ID_SENT = 'ps_id_sent'


def get_previous_value_helper(key):
    the_object = TwitterID.xg.get_or_none(key=key)
    if the_object:
        return the_object.value
    else:
        return None


def save_value_helper(key, val):
    twitter_id = TwitterID.xg.get_or_none(key=key)
    if not twitter_id:
        twitter_id = TwitterID(key=key, value=val)
    twitter_id.value = val
    twitter_id.save()
    print 'val: {}'.format(val)


def get_previous_ps1_id():
    return get_previous_value_helper(key=PS1_ID_KEY)


def get_previous_ps1_date():
    return get_previous_value_helper(key=PS1_DATE_KEY)


def save_latest_ps1_date(date_string):
    save_value_helper(key=PS1_DATE_KEY, val=date_string)


def save_latest_ps1_id(fb_id):
    save_value_helper(key=PS1_ID_KEY, val=fb_id)


def send_text_to_me(msg):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login('maximusfowler@gmail.com', SECRETS_DICT['TEXT_SECRET'])
    my_phone_number = SECRETS_DICT['MY_PHONE_NUMBER']
    server.sendmail('max', my_phone_number, msg)


def check_for_ps1():
    access_token = SECRETS_DICT['FB_FRIENDSFRIENDS_ACCESS_TOKEN']
    url = "https://graph.facebook.com/472307929618113/feed?key=value&access_token={}".format(access_token)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    returned = json.loads(the_page)
    messages = returned['data']

    # if id is different send message
    # most_recent = messages[0]
    # previous_id = get_previous_ps1_id()
    # most_recent_id = most_recent['id']
    # if most_recent.get('type') == 'status':
    #     most_recent_message = most_recent['message']
    # elif most_recent.get('type') == 'link':
    #     most_recent_message = most_recent['link']
    # else:
    #     most_recent_message = 'uNkNoWn'
    #
    # if most_recent_id != previous_id:
    #     save_latest_ps1_id(most_recent_id)
    #     ascii_message = most_recent_message.encode('ascii', 'ignore')
    #     msg = str(ascii_message)
    #     print msg
    #     send_text_to_me(msg)
    # else:
    #     print '++ no new posts'

    # also check for mo recent date
    previous_latest_date_string = get_previous_ps1_date()
    if not previous_latest_date_string:
        first_date_string = messages[0]['created_time']
        save_latest_ps1_date(date_string=first_date_string)

    previous_latest_date = numpy.datetime64(previous_latest_date_string)
    latest_found = previous_latest_date
    for message in messages:
        updated_time_string = message.get('created_time')
        if updated_time_string:
            message_date = numpy.datetime64(updated_time_string)
            if message_date > previous_latest_date:
                if message_date > latest_found:
                    latest_found = message_date
                    save_latest_ps1_date(date_string=updated_time_string)
                message_text = message.get('message')
                ascii_message = message_text.encode('ascii', 'ignore')
                message_id = message['id']
                already_sent = TwitterID.xg.get_or_none(key=PS1_ID_SENT, value=message_id)
                if not already_sent:
                    already_sent = TwitterID(key=PS1_ID_SENT, value=message_id)
                    already_sent.save()
                    send_text_to_me(msg=ascii_message)



if __name__ == '__main__':
    expo_sleep = 0
    while True:
        try:
            check_for_ps1()
            expo_sleep = 0
            time.sleep(20 + random.randint(0,5))
        except:
            print 'XX exception'
            send_text_to_me('XX ' + str(expo_sleep))
            expo_sleep += 1
            time.sleep(2**expo_sleep * 60)