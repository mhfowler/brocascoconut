import os

from bots.twitter_helper import get_latest_mentions
from bots.trashbot import trash_takers, trashBot


DIR_PATH = os.path.dirname(__file__)

latest_mention_file_path = os.path.join(DIR_PATH, 'latest_mention.txt')


def get_latest_mention_id():
    if not os.path.isfile(latest_mention_file_path):
        return None
    with open(latest_mention_file_path, 'r') as latest_mention_file:
        contents = latest_mention_file.read()
        id = int(contents)
    return id


def save_latest_mention_id(id):
    with open(latest_mention_file_path, 'w') as latest_mention_file:
        latest_mention_file.write(str(id))


def check_for_mentions(previous_mention_id):
    latest_mentions = get_latest_mentions(previous_mention_id)
    if latest_mentions:
        mentions_by_trashtaker = []
        for mention in latest_mentions:
            user = mention['user']['screen_name']
            if user in trash_takers:
                mentions_by_trashtaker.append(mention)
        if mentions_by_trashtaker:
            latest_mention = mentions_by_trashtaker[0]
            new_id = latest_mention['id']
            save_latest_mention_id(new_id)
            trashBot(None)


if __name__ == '__main__':
    previous_mention_id = get_latest_mention_id()
    check_for_mentions(previous_mention_id)
