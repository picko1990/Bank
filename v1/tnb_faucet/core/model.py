# 
# Author: Nikhil Taneja (taneja.nikhil03@gmail.com)
# model.py (c) 2021
# Desc: description
# Created:  Fri Jan 08 2021 04:06:55 GMT+0530 (India Standard Time)
# Modified: Fri Jan 08 2021 18:19:26 GMT+0530 (India Standard Time)
# 

import logging

logging.basicConfig(
    filename='faucet.log',
    filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()


class PostModel:
    __account_number = ''
    __user_id = -1
    __platform = 'Twitter'
    
    def __init__(self, post_id: int):
        if isinstance(post_id, int) and post_id > 0:
            self.__post_id = post_id
        else: logger.error(f'Invalid post id <{post_id}>!')
    
    def get_id(self):
        return self.__post_id

    def set_platform(self, platform: str):
        if not self.__post_id:
            return
        if platform.lower() == 'twitter':
            self.__platform = 'Twitter'
        elif platform.lower() == 'facebook':
            self.__platform = 'Facebook'
        else: logger.error(f'Invalid platform <{platform}> via <{self.__platform}:{self.__post_id}>')

    def get_platform(self):
        return self.__platform

    def set_user(self, user_id: int):
        if not self.__post_id:
            return
        if isinstance(user_id, int) and user_id > 0:
            self.__user_id = user_id
        else: logger.error(f'Invalid user id <User:{user_id}> via <{self.__platform}:{self.__post_id}>')
        
    def get_user(self):
        if self.__post_id:
            return self.__user_id

    def set_account_number(self, account_number: str):
        if not self.__post_id:
            return
        if isinstance(account_number, str) and len(account_number) == 64:
            self.__account_number = account_number
        else: logger.error(f'Invalid account number for <User:{self.__user_id}> via <{self.__platform}:{self.__post_id}>')
        
    def get_account_number(self):
        if self.__post_id:
            return self.__account_number

    def __str__(self):
        return f'<User:{self.__user_id}> requested funds to <{self.__account_number}> via <{self.__platform}:{self.__post_id}>'        
