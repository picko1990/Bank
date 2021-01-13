# 
# Author: Nikhil Taneja (taneja.nikhil03@gmail.com)
# tw_post.py (c) 2021
# Desc: description
# Created:  Fri Jan 08 2021 04:23:36 GMT+0530 (India Standard Time)
# Modified: Fri Jan 08 2021 18:19:58 GMT+0530 (India Standard Time)
# 

import re
import os
import requests
import logging
from urllib.parse import urlparse
from .model import PostModel
from .utils import find_account_number, validate_hashtag
import configparser

def parse_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

logging.basicConfig(
    filename='faucet.log',
    filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()


def get_twitter_access_token(consumer_key, consumer_secret):
    url = 'https://api.twitter.com/oauth2/token'

    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, data=data, auth=(consumer_key, consumer_secret))
    if response.status_code != 200:
        logger.error(f'Failed to authenticate <{response.status_code}> <Error:{response.text}>')
        return None

    return response.json()['access_token']

# config = parse_config(settings.BASE_DIR+'\\config.cfg')
access_token = os.getenv('ACCESS_TOKEN_TWITTER') # config['TWITTER']['access_token']

def process(tweet_url):
    url = urlparse(tweet_url)
    path = url.path
    if path[-1] == '/':
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

    response = requests.get('https://api.twitter.com/1.1/statuses/show.json', headers=headers, params=params)
    if response.status_code != 200:
        logger.error(f'Cannot find tweet of id <{tweet_id}> <Error:{response.text}>')
        return
    data = response.json()
    post = PostModel(tweet_id)
    post.set_platform('twitter')
    account_number = find_account_number(data['text'])
    if not account_number:
        logger.error('Invalid account number for <User:{user_id}> via <Facebook:{tweet_id}>')
        return
    post.set_account_number(account_number)
    post.set_user(data['user']['id'])
    if validate_hashtag((tag['text'] for tag in data['entities']['hashtags'])):
        logger.info(str(post))
        return post
