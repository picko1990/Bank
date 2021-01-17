#
# Author: Nikhil Taneja (taneja.nikhil03@gmail.com)
# tw_post.py (c) 2021
# Desc: description
# Created:  Fri Jan 08 2021 04:23:36 GMT+0530 (India Standard Time)
# Modified: Fri Jan 08 2021 18:19:58 GMT+0530 (India Standard Time)
#

import configparser
import logging
from urllib.parse import urlparse

import requests

from .model import PostModel
from .utils import find_account_number, validate_hashtag

logger = logging.getLogger('faucet')


def parse_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def get_twitter_access_token(consumer_key, consumer_secret):
    url = 'https://api.twitter.com/oauth2/token'

    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(
        url, data=data,
        auth=(consumer_key, consumer_secret))
    if response.status_code != 200:
        logger.debug((
            'Failed to authenticate '
            f'<{response.status_code}> <Error:{response.text}>'))
        logger.error((
            f'Failed to authenticate <{response.status_code}>'))
        return None

    return response.json()['access_token']


config = parse_config('v1/tnb_faucet/core/config.cfg')


def process(tweet_url, amount):
    access_token = config['TWITTER']['ACCESS_TOKEN_TWITTER']
    url = urlparse(tweet_url)
    path = url.path
    if path and path[-1] == '/':
        path = path[:-1]
    endpoint = path.split('/')[-1]
    if not endpoint.isnumeric():
        logger.error(f'Cannot determine tweet id for <{tweet_url}>')
        return

    tweet_id = int(endpoint)

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = (('id', tweet_id),)

    response = requests.get(
        'https://api.twitter.com/1.1/statuses/show.json',
        headers=headers, params=params)
    if response.status_code != 200:
        logger.debug((
            'Cannot find tweet of id '
            f'<{tweet_id}> <Error:{response.text}>'))
        logger.error((
            f'Cannot find tweet of id for <{tweet_url}>'))
        return
    data = response.json()
    user_id = data['user']['id']
    post = PostModel(tweet_id, amount.coins, amount.delay)
    post.set_platform('twitter')
    account_number = find_account_number(data['text'])
    if not account_number:
        logger.debug(('Invalid account number for '
                      f'<User:{user_id}> via <Twitter:{tweet_id}>'))
        logger.error(f'Invalid account number for <{tweet_url}>')
        return
    post.set_account_number(account_number)
    post.set_user(user_id)
    if validate_hashtag(
            (tag['text'] for tag in data['entities']['hashtags'])):
        logger.debug(str(post))
        logger.info(f'Successfully sent <{str(amount)}> via <{tweet_url}>')
        return post


if __name__ == '__main__':
    config = parse_config('./config.cfg')
    print(get_twitter_access_token(
        config['DEFAULT']['consumer_key'],
        config['DEFAULT']['consumer_secret']))
