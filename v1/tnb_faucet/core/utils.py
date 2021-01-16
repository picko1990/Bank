#
# Author: Nikhil Taneja (taneja.nikhil03@gmail.com)
# utils.py (c) 2021
# Desc: description
# Created:  Fri Jan 08 2021 04:16:11 GMT+0530 (India Standard Time)
# Modified: Fri Jan 08 2021 04:16:38 GMT+0530 (India Standard Time)
#

import re


def validate_hashtag(tags, to='TNBFaucet'):
    for tag in tags:
        if (tag.lower() == to.lower()
                or '#' + to.lower()):
            return True
    return False


def find_account_number(text):
    match = re.search(r'[0-9a-fA-F]{64}', text)
    if match:
        return match.group()
