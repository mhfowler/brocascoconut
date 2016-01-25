from settings.common import SECRETS_DICT

import json
import urllib2
import time
import random
import numpy

from bots.text_helper import send_text
from mhf.models import TwitterID


PS1_ID_KEY = 'ps1_id'
PS1_DATE_KEY = 'ps1_date'
PS1_ID_SENT = 'ps_id_sent'


def get_ps1_id_key(event_id, to_phone_number):
   return PS1_ID_KEY + str(event_id) + str(to_phone_number)

def get_ps1_date_key(event_id, to_phone_number):
    return PS1_ID_KEY + str(event_id) + str(to_phone_number)

def get_ps1_id_sent_key(event_id, to_phone_number):
    return PS1_ID_SENT + str(event_id) + str(to_phone_number)


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


def get_previous_ps1_id(event_id, to_phone_number):
    return get_previous_value_helper(key=get_ps1_id_key(event_id, to_phone_number))


def get_previous_ps1_date(event_id, to_phone_number):
    return get_previous_value_helper(key=get_ps1_date_key(event_id, to_phone_number))


def save_latest_ps1_date(date_string, event_id, to_phone_number):
    save_value_helper(key=get_ps1_date_key(event_id, to_phone_number), val=date_string)


def save_latest_ps1_id(fb_id, event_id, to_phone_number):
    save_value_helper(key=get_ps1_id_key(event_id, to_phone_number), val=fb_id)


def check_for_ps1(fb_event_id, to_phone_number):
    access_token = SECRETS_DICT['FB_FRIENDSFRIENDS_ACCESS_TOKEN']
    url = "https://graph.facebook.com/{}/feed?key=value&access_token={}".format(fb_event_id, access_token)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    returned = json.loads(the_page)
    messages = returned['data']

    # also check for mo recent date
    previous_latest_date_string = get_previous_ps1_date(event_id=fb_event_id, to_phone_number=to_phone_number)
    if not previous_latest_date_string:
        first_date_string = messages[0]['created_time']
        save_latest_ps1_date(date_string=first_date_string, event_id=fb_event_id, to_phone_number=to_phone_number)

    previous_latest_date = numpy.datetime64(previous_latest_date_string)
    latest_found = previous_latest_date
    for message in messages:
        updated_time_string = message.get('created_time')
        if updated_time_string:
            message_date = numpy.datetime64(updated_time_string)
            if previous_latest_date == numpy.datetime64('NaT') or message_date > previous_latest_date:
                if latest_found == numpy.datetime64('NaT') or message_date > latest_found:
                    latest_found = message_date
                    save_latest_ps1_date(date_string=updated_time_string, event_id=fb_event_id, to_phone_number=to_phone_number)
                message_text = message.get('message') if message.get('message') else ''
                message_id = message['id']
                link_to_comment = 'http://facebook.com/{}/'.format(message_id)
                message_text += '--> {}'.format(link_to_comment)
                already_sent = TwitterID.xg.get_or_none(key=get_ps1_id_sent_key(event_id=fb_event_id,
                                                                                to_phone_number=to_phone_number),
                                                        value=message_id)
                if not already_sent:
                    already_sent = TwitterID(key=get_ps1_id_sent_key(event_id=fb_event_id,
                                                                     to_phone_number=to_phone_number
                                                                     ),
                                             value=message_id)
                    already_sent.save()
                    send_text(msg=message_text, to_phone_number=to_phone_number)


if __name__ == '__main__':

    fb_e_id = '1007079329351257'

    expo_sleep = 0
    while True:
        try:
            check_for_ps1(fb_event_id=fb_e_id)
            expo_sleep = 0
            time.sleep(20 + random.randint(0,5))
        except:
            print 'XX exception'
            send_text('XX ' + str(expo_sleep))
            expo_sleep += 1
            time.sleep(2**expo_sleep * 60)