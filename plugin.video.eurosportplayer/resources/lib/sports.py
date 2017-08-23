# -*- coding: utf-8 -*-

from common import *

class Sports:

    def __init__(self, i):
        self.item = {}
        self.item['mode'] = 'videos'
        self.item['title'] = utfenc(i['tags'][0]['displayName'])
        self.item['id'] = i['id']
        self.photos = i['defaultAssetImage'][0]['photos']
        self.images()
        
    def images(self):
        for i in self.photos:
            if i['width'] == 770 and i['height'] == 432:
                self.item['thumb'] = i['imageLocation']
            if i['width'] == 1600:
                self.item['fanart'] = i['imageLocation']