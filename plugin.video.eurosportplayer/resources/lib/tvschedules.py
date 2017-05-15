# -*- coding: utf-8 -*-

from common import *

class TVSchedules:

    def __init__(self, i):
        self.item = {}
        self.item['mode'] = ''
        self.time = i['startdate']['time']
        self.date = i['startdate']['date']
        self.name = i['name']
        self.item['title'] = utfenc(unicode('%s %s %s' % (self.date, self.time, self.name)))
        self.item['plot'] = utfenc(i['description'])
        self.item['thumb'] = i['sportpictureurl']