# -*- coding: utf-8 -*-

from common import *

class Events:

    def __init__(self, i):
        self.item = {}
        self.item['mode'] = 'event'
        self.item['title'] = utfenc(i['title'])
        self.item['id'] = i['contentId']
        self.item['thumb'] = i['heroImage'][0]['rawImage']
        self.item['fanart'] = i['heroImage'][0]['rawImage']
        self.item['plot'] = '{0} - {1}'.format(i['startDate'][:10], i['endDate'][:10])
            