# 
# Author: Nikhil Taneja (taneja.nikhil03@gmail.com)
# main.py (c) 2021
# Desc: description
# Created:  Thu Jan 07 2021 02:33:54 GMT+0530 (India Standard Time)
# Modified: Fri Jan 08 2021 04:57:03 GMT+0530 (India Standard Time)
# 

import fb_post
import tw_post
import configparser

def parse_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

if __name__ == '__main__':
    config = parse_config('./config.cfg')

    tw_url = 'https://twitter.com/TOP_photographr/status/1346925367424995328'
    fb_url = 'https://www.facebook.com/nikhil.taneja.1276/posts/4271612509533719'

    access_token = config['TWITTER']['access_token']
    
    twitter_post = tw_post.process(access_token, tw_url)
    facebook_post = fb_post.process(fb_url)