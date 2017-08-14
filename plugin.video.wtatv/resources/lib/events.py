# -*- coding: utf-8 -*-

from common import *

class Events:

    def __init__(self, i):
        self.item = {}
        self.start = utc2local(i['startDateTime'])
        self.now = datetime.datetime.now().strftime(time_format)
        self.end = utc2local(i['endDate'])
        self.title = i['title']
        self.logo = i['competitionLogo']
        self.item['mode'] = 'play_live'
        self.item['id'] = i['id']
        self.item['plot'] = utfenc(re.sub('<BR>', '\n', i['fullDescription']))
        
        self.update_item()
        
    def update_item(self):
        label = self.start[:-3]
        if time_stamp(self.start) <= time_stamp(self.now):
            label = '[COLOR red]LIVE[/COLOR]'
        else:
            self.end = self.start
        self.start = self.now
        if not self.logo.startswith('http'):
            self.logo = base_url + self.logo
        self.item['title'] = utfenc(label + ' ' + self.title)
        self.item['duration'] = timedelta_total_seconds(time_stamp(self.end)-time_stamp(self.start))
        self.item['thumb'] = self.logo