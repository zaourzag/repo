# -*- coding: utf-8 -*-

from common import *

class Matches:

    def __init__(self, i, date):
        self.item = {}
        self.date = date
        self.time = re.search('<div class="matchTimeCell.*?">(.+?)</div>', i).group(1)
        self.team1 = re.search('<div class="matchTeam1Cell"><.*?>(.+?)<', i, re.DOTALL)
        self.team2 = re.search('<div class="matchTeam2Cell">.*?</span>(.+?)<', i, re.DOTALL)
        self.name = re.search('</div><div style=".+?">(.+?)</div>', i, re.DOTALL)
        self.action = re.search('<div class="matchActionCell"><a href="(.+?)">', i, re.DOTALL).group(1)
        self.info = re.search('style="width:100%.*?">(.+?)</div>', i, re.DOTALL)
        
        self.title = self.get_title()
        
        if self.title:
            self.update_item()
        
    def get_title(self):
        if self.team1 and self.team2:
            return utfenc('{0} {1} vs {2}'.format(self.time, self.team1.group(1).strip(), self.team2.group(1).strip()))
        elif self.name:
            return utfenc('{0} {1}'.format(self.time, self.name.group(1)))
        else:
            return None
        
    def get_plot(self):
        if self.info:
            info = self.info.group(1).strip()
        else:
            info = ''
        return utfenc('%s\n%s\n%s' % (self.date, self.title, info))
        
    def update_item(self):
        self.item['mode'] = 'details'
        self.item['title'] = self.title
        self.item['id'] = self.action
        self.item['plot'] = self.get_plot()