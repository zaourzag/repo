# -*- coding: utf-8 -*-

from common import *

class Videos:

    def __init__(self, i):
        self.item = {}
        self.item['mode'] = 'play_vod'
        self.item['title'] = utfenc(i['header'])
        self.item['plot'] = utfenc(i['teaserText'])
        self.item['id'] = i['url']
        self.item['duration'] = i['duration']
        self.item['thumb'] = i['teaserImageUrl']