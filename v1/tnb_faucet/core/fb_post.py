# 
# Author: Nikhil Taneja (taneja.nikhil03@gmail.com)
# fb_post.py (c) 2021
# Desc: description
# Created:  Fri Jan 08 2021 04:19:09 GMT+0530 (India Standard Time)
# Modified: Fri Jan 08 2021 18:19:22 GMT+0530 (India Standard Time)
# 

import re
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, parse_qs
from .model import PostModel
from .utils import find_account_number, validate_hashtag

logging.basicConfig(
    filename='faucet.log',
    filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()


def process(fb_url):
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

    post = PostModel(post_id)
    post.set_platform('facebook')

    response = requests.get(post_url)
    if response.status_code != 200:
        logger.error(f'Cannot find post of id <{post_id}> <Error:{response.text}>')
        return

    soup = BeautifulSoup(response.text, 'lxml')
    element = soup.select_one('#mobile_login_bar a')
    if not element:
        logger.error(f'Cannot extract text for <Facebook:{post_id}>')
        return

    url = urlparse(unquote(element['href']))
    params = parse_qs(url.query)
    user_id_str = params.get('rid')
    if not user_id_str:
        logger.error(f'Cannot determine user id for <Facebook:{post_id}>')
        return
    
    user_id = int(user_id_str[0])
    post.set_user(user_id)

    text = ''
    element = soup.select_one('.msg div')
    if element:
        text = element.text
    else:
        element = soup.select_one('#m_story_permalink_view div div div div:nth-child(2)')
        if element:
            text = element.text
    if not text:
        logger.error('Invalid account number for <User:{user_id}> via <Facebook:{post_id}>')
        return

    account_number = find_account_number(text)
    if not account_number:
        logger.error('Invalid account number for <User:{user_id}> via <Facebook:{post_id}>')
        return
    post.set_account_number(account_number)

    hashtags = re.findall(r'#\w+', text)
    if validate_hashtag(hashtags):
        logger.info(str(post))
        return post
