# -*- coding: utf-8 -*-

from common import *

class Sports:

    def __init__(self, i):
        self.item = {}
        self.item['mode'] = 'videos'
        self.item['title'] = utfenc(i['tags'][0]['displayName'])
        sport = i['sport']
        logo = i['logoImage']
        if logo and sport:
            if sport.isdigit():
                self.item['id'] = sport
            self.item['thumb'] = logo[0]['rawImage']