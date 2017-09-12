# -*- coding: utf-8 -*-

from common import *

class Sports:

    def __init__(self, i):
        self.item = {}
        self.item['mode'] = 'videos'
        self.item['title'] = utfenc(i['tags'][0]['displayName'])
        self.item['id'] = i['sport']
        self.item['thumb'] = i['logoImage'][0]['rawImage']