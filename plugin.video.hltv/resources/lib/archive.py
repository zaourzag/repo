# -*- coding: utf-8 -*-

from common import *

class Archive:

    def __init__(self, i):
        self.item = {}
        self.team1 = self.clean(re.search('<a.+?src=".*?>(.+?)vs', i, re.DOTALL).group(1))
        self.team2 = self.clean(re.search('vs <img.+?src=".*?>(.+?)$', i, re.DOTALL).group(1))
        self.time = re.search('<a href=".+?">(.+?)</a>', i).group(1)
        self.link = re.search('<a href="(.+?)"', i).group(1)
        self.name = re.search('title="(.+?)"', i).group(1)
        
        self.update_item()
        
    def clean(self, string):
        return re.sub('<.*?>', '', string)
        
    def update_item(self):
        self.item['mode'] = 'details'
        self.item['title'] = utfenc('{0} {1} vs {2}'.format(self.time, self.team1.strip(), self.team2.strip()))
        self.item['id'] = self.link
        self.item['plot'] = utfenc(self.name)