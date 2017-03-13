# -*- coding: utf-8 -*-

from common import *

def get_playback_url(url, data):
    src = re.search('src\s*=\s*"(.+?)"', data)
    if src:
        return src.group(1)
    else:
        return url