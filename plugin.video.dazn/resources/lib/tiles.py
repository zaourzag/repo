# -*- coding: utf-8 -*-

from .common import *
from resources import resources

class Tiles:

    def __init__(self, i):
        self.item           = {}
        self.title          = i['Title']
        self.subtitle       = i['SubTitle']
        self.description    = i['Description']
        self.start          = utc2local(i.get('Start', ''))
        self.end            = utc2local(i.get('End', ''))
        self.now            = datetime.datetime.now().strftime(time_format)
        self.sport          = i.get('Sport', '')
        self.competition    = i.get('Competition', '')
        self.type           = i.get('Type', '')
        self.nav            = i.get('NavigateTo', '')
        self.related        = i.get('Related', [])
        if self.nav:
            self.mode   = 'rails'
            self.id     = i['NavigateTo']
            self.params = i['AssetId']
        else:
            self.mode   = 'play'
            self.id     = i['AssetId']
            self.params = ''
        self.update_item(i)
        
    def add_duration(self, i):
        if 'upcoming' in self.type.lower():
            self.end   = self.start
            self.start = self.now
        elif 'live' in self.type.lower():
            self.start = self.now
        if self.start and self.end:
            start = datetime.datetime.fromtimestamp(time.mktime(time.strptime(self.start,time_format)))
            end = datetime.datetime.fromtimestamp(time.mktime(time.strptime(self.end,time_format)))
            self.item['duration'] = timedelta_total_seconds(end-start)
        
    def add_thumb(self, i):
        url = api_base+"/img('%s')/$value?Quality=95&Width=256&Height=256&Format='%s'"
        image = i.get('Image', '')
        if image:
            self.item['thumb'] = url % (image['Id'], image['ImageMimeType'])
            
    def plot(self):
        if self.competition:
            self.competition = self.competition['Title']
        if self.sport:
            self.sport = self.sport['Title']
        return utfenc(unicode('%s\n\nStart: %s\nSport: %s\nCompetition: %s' % (self.description, self.start, self.sport, self.competition)))
        
    def update_item(self, i):
        self.item['mode']  = self.mode
        self.item['title'] = utfenc(self.title)
        self.item['plot']  = utfenc(self.description)
        self.item['id']    = self.id
        self.item['type']  = utfenc(resources(self.type))

        if self.params:
            self.item['params'] = self.params
            
        if (self.type == 'UpComing' or 'Scheduled' in i.get('Id', '')) or (self.type == 'Highlights'):
            if self.type == 'UpComing':
                day = resources(days(self.type, self.now, self.start))
                sub_title = unicode('%s %s' % (day, self.start[11:][:5]))
            else:
                sub_title = resources(self.type)
            self.item['params'] = i['Id'].split(':')[0]
            self.item['title']  = utfenc(unicode('%s (%s)' % (self.title, sub_title)))
            
        if i.get('ListingStartTime', None):
            self.item['date'] = utc2local(i['ListingStartTime'])[:10]
            
        if self.related:
            self.item['cm'] = self.related
        
        self.add_thumb(i)
        self.add_duration(i)