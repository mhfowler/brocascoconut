import csv, StringIO

from boto.s3.connection import S3Connection
from settings.common import SECRETS_DICT

from boto.s3.key import Key

CRON_BUCKET = 'citigroup-cron'
ACTIVE_ALERTS_KEY = 'gl_active_alerts.txt'


def get_active_alerts_contents():
    cron_bucket = CRON_BUCKET
    cron_key = ACTIVE_ALERTS_KEY
    aws_access_key = SECRETS_DICT['CRONBOX_ACCESS_KEY']
    aws_secrets_key = SECRETS_DICT['CRONBOX_SECRET_KEY']
    conn = S3Connection(aws_access_key, aws_secrets_key)
    bucket = conn.get_bucket(cron_bucket)
    k = Key(bucket)
    k.key = cron_key
    cron_contents = k.get_contents_as_string()
    print cron_contents
    return cron_contents


def set_active_alerts_contents(new_alerts_contents):
    cron_bucket = CRON_BUCKET
    cron_key = ACTIVE_ALERTS_KEY
    aws_access_key = SECRETS_DICT['CRONBOX_ACCESS_KEY']
    aws_secrets_key = SECRETS_DICT['CRONBOX_SECRET_KEY']
    conn = S3Connection(aws_access_key, aws_secrets_key)
    bucket = conn.get_bucket(cron_bucket)
    k = Key(bucket)
    k.key = cron_key
    k.set_contents_from_string(new_alerts_contents)


def get_facebook_active_alerts():
    s3_contents = get_active_alerts_contents()
    active_alerts = set()
    csv_reader = csv.reader(StringIO.StringIO(s3_contents))
    csv_reader.next()
    for row in csv_reader:
        fb_id = row[0]
        phone = row[1]
        active_alerts.add((fb_id, phone))
    return active_alerts


def set_facebook_active_alerts(active_alerts):
    csv_contents = 'fb_id, phone\n'
    for alert in active_alerts:
       csv_contents += alert[0] + ',' + alert[1] + '\n'
    set_active_alerts_contents(csv_contents)


def add_facebook_cron_alert(phone, fb_id):
    active_alerts = get_facebook_active_alerts()
    if not (fb_id, phone) in active_alerts:
        active_alerts.add((fb_id, phone))
        set_facebook_active_alerts(active_alerts)


def remove_facebook_cron_alert(phone, fb_id):
    active_alerts = get_facebook_active_alerts()
    if (fb_id, phone) in active_alerts:
        active_alerts.remove((fb_id, phone))
        set_facebook_active_alerts(active_alerts)


if __name__ == '__main__':
    get_facebook_active_alerts()