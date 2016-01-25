import re

from boto.s3.connection import S3Connection
from settings.common import SECRETS_DICT

from boto.s3.key import Key

CRON_BUCKET = 'citigroup-cron'
CRON_KEY = 'cronbox_crontab.txt'


def get_cron_contents():
    cron_bucket = CRON_BUCKET
    cron_key = CRON_KEY
    aws_access_key = SECRETS_DICT['CRONBOX_ACCESS_KEY']
    aws_secrets_key = SECRETS_DICT['CRONBOX_SECRET_KEY']
    conn = S3Connection(aws_access_key, aws_secrets_key)
    bucket = conn.get_bucket(cron_bucket)
    k = Key(bucket)
    k.key = cron_key
    cron_contents = k.get_contents_as_string()
    print cron_contents
    return cron_contents


def set_cron_contents(new_cron_contents):
    cron_bucket = CRON_BUCKET
    cron_key = CRON_KEY
    aws_access_key = SECRETS_DICT['CRONBOX_ACCESS_KEY']
    aws_secrets_key = SECRETS_DICT['CRONBOX_SECRET_KEY']
    conn = S3Connection(aws_access_key, aws_secrets_key)
    bucket = conn.get_bucket(cron_bucket)
    k = Key(bucket)
    k.key = cron_key
    k.set_contents_from_string(new_cron_contents)


def get_facebook_cron_alerts():
    cron_contents = get_cron_contents()
    lines = cron_contents.split('\n')
    found_alerts = []
    for line in lines:
        matched = re.match(
            pattern='\* \* \* \* \* curl http://brocascoconut.com/get_tix/(\d+)/(.+)/ >> /home/ec2-user/crontab_tix_2.log',
            string=line
        )
        if matched:
            fb_id = matched.group(1)
            phone = matched.group(2)
            print '{} / {}'.format(fb_id, phone)
            found_alerts.append((fb_id, phone))
    return found_alerts


def add_facebook_cron_alert(phone, fb_id):
    active_alerts = get_facebook_cron_alerts()
    if not (fb_id, phone) in active_alerts:
        cron_line = create_line_string_from_numbers(phone=phone, fb_id=fb_id)
        cron_contents = get_cron_contents()
        new_cron_contents = cron_contents + '\n' + cron_line + '\n'
        set_cron_contents(new_cron_contents)
        print 'new_cron_contents: {}'.format(new_cron_contents)


def remove_facebook_cron_alert(phone, fb_id):
    active_alerts = get_facebook_cron_alerts()
    if (fb_id, phone) in active_alerts:
        cron_contents = get_cron_contents()
        cron_line = create_line_string_from_numbers(phone=phone, fb_id=fb_id)
        new_cron_contents = cron_contents.replace(cron_line, '\n')
        print 'new_cron_contents: {}'.format(new_cron_contents)
        set_cron_contents(new_cron_contents)


def create_line_string_from_numbers(fb_id, phone):
    line_string_template = \
        '* * * * * curl http://brocascoconut.com/get_tix/{fb_id}/{phone}/ >> /home/ec2-user/crontab_tix_2.log'
    line_string = line_string_template.format(fb_id=fb_id, phone=phone)
    return line_string


if __name__ == '__main__':
    get_facebook_cron_alerts()