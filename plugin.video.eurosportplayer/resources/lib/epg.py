# -*- coding: utf-8 -*-

from common import *

class EPG:

    def __init__(self, i):
        self.item = {}
        self.item['mode'] = 'tvschedule'
        self.item['title'] = utfenc(i['name'])
        self.item['id'] = utfenc(i['channel'])
        self.item['thumb'] = i['logourl']