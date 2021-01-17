#
# Author: Nikhil Taneja (taneja.nikhil03@gmail.com)
# fb_post.py (c) 2021
# Desc: description
# Created:  Fri Jan 08 2021 04:19:09 GMT+0530 (India Standard Time)
# Modified: Fri Jan 08 2021 18:19:22 GMT+0530 (India Standard Time)
#

import logging
import re
from urllib.parse import parse_qs, unquote, urlparse

import requests
from bs4 import BeautifulSoup

from .model import PostModel
from .utils import find_account_number, validate_hashtag


logger = logging.getLogger('faucet')


def process(fb_url, amount):
    post_url = f'https://mbasic.facebook.com{urlparse(fb_url).path}'

    url = urlparse(post_url)
    params = parse_qs(url.query)
    path = url.path
    if path and path[-1] == '/':
        path = path[:-1]
    endpoint = path.split('/')[-1]
    if endpoint.isnumeric():
        post_id = int(endpoint)
    else:
        endpoint = params.get('story_fbid')
        if endpoint:
            post_id = int(endpoint[0])
        else:
            logger.error('Cannot determine post id for <{fb_url}>')
            return

    post = PostModel(post_id, amount.coins, amount.delay)
    post.set_platform('facebook')

    response = requests.get(post_url)
    if response.status_code != 200:
        logger.debug((
            'Cannot find post of id '
            f'<{post_id}> <Error:{response.text}>'))
        logger.error((
            f'Cannot find post of id for <{post_url}>'))
        return

    soup = BeautifulSoup(response.text, 'lxml')
    element = soup.select_one('#mobile_login_bar a')
    if not element:
        logger.debug((
            'Cannot extract text for '
            f'<Facebook:{post_id}>'))
        logger.error((
            f'Cannot extract text for <{post_url}>'))
        return

    url = urlparse(unquote(element['href']))
    params = parse_qs(url.query)
    user_id_str = params.get('rid')
    if not user_id_str:
        logger.debug((
            'Cannot determine user id '
            f'for <Facebook:{post_id}>'))
        logger.error((
            'Cannot determine user id '
            f'for <{post_url}>'))
        return

    user_id = int(user_id_str[0])
    post.set_user(user_id)

    text = ''
    element = soup.select_one('.msg div')
    if element:
        text = element.text
    else:
        element = soup.select_one((
            '#m_story_permalink_view div '
            'div div div:nth-child(2)'))
        if element:
            text = element.text
    if not text:
        logger.debug((
            'Invalid account number for '
            f'<User:{user_id}> via <Facebook:{post_id}>'))
        logger.error((
            'Invalid account number for '
            f'<{post_url}>'))
        return

    account_number = find_account_number(text)
    if not account_number:
        logger.debug((
            'Invalid account number for '
            f'<User:{user_id}> via <Facebook:{post_id}>'))
        logger.error((
            'Invalid account number for '
            f'<{post_url}>'))
        return
    post.set_account_number(account_number)

    hashtags = re.findall(r'#\w+', text)
    if validate_hashtag(hashtags):
        logger.debug(str(post))
        logger.info(f'Successfully sent <{str(amount)}> via <{post_url}>')
        return post
