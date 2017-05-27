# -*- coding: utf-8 -*-

from common import *

class Archive:

    def __init__(self, i):
        self.item = {}
        unixtime = re.search('unix="(.+?)"', i).group(1)[:10]
        self.date = date(unixtime)
        self.teams = re.findall('<td class="teams">(.+?)</td>', i, re.DOTALL)
        self.url = re.search('<a href="(.+?)"', i, re.DOTALL).group(1)
        self.info = re.search('<div class="online text-ellipsis">(.+?)</div>', i, re.DOTALL)
        
        self.title = self.get_title()
        
        if self.title:
            self.update_item()
        
    def get_title(self):
        if self.teams:
            team1 = re.search('title="(.+?)"', self.teams[0]).group(1)
            team2 = re.search('title="(.+?)"', self.teams[1]).group(1)
            return utfenc('%s %s vs %s' % (self.date, team1, team2))
        else:
            return None
        
    def get_plot(self):
        if self.info:
            info = self.info.group(1).strip()
        else:
            info = ''
        return utfenc('%s\n%s' % (self.title, info))
        
    def update_item(self):
        self.item['mode'] = 'details'
        self.item['title'] = self.title
        self.item['id'] = self.url
        self.item['plot'] = self.get_plot()