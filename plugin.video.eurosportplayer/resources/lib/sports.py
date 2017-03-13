# -*- coding: utf-8 -*-

from common import *

class Sports:

    def __init__(self, i):
        self.item = {}
        self.item['mode'] = 'videos'
        self.item['title'] = utfenc(i['name'])
        self.item['id'] = i['id']
        self.item['thumb'] = i['pictureurl']