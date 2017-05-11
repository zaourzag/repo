# -*- coding: utf-8 -*-

from .common import *
from resources import resources

class Tiles:

    def __init__(self, i):
        self.item = {}
        self.title = i['Title']
        self.subtitle = i.get('SubTitle', '')
        self.description = i['Description']
        self.start = utc2local(i.get('Start', ''))
        self.end = utc2local(i.get('End', ''))
        self.now = datetime.datetime.now().strftime(time_format)
        self.sport = i.get('Sport', [])
        self.competition = i.get('Competition', [])
        self.type = i.get('Type', '')
        self.nav = i.get('NavigateTo', '')
        self.related = i.get('Related', [])
        if self.nav:
            self.mode = 'rails'
            self.id = i['NavigateTo']
            self.params = i['NavParams']
        else:
            self.mode = 'play'
            self.id = i['AssetId']
            self.params = i['EventId']
        self.update_item(i)

    def add_duration(self, i):
        if 'UpComing' in self.type:
            self.end = self.start
            self.start = self.now
        elif 'Live' in self.type:
            self.start = self.now
        if self.start and self.end:
            self.item['duration'] = timedelta_total_seconds(time_stamp(self.end)-time_stamp(self.start))

    def add_thumb(self, i):
        url = api_base+'v2/image?id=%s&Quality=95&Width=%s&Height=%s&ResizeAction=fill&VerticalAlignment=top&Format=%s'
        image = i.get('Image', '')
        if image:
            self.item['thumb'] = url % (image['Id'], '720', '404', image['ImageMimeType'])
            self.item['fanart'] = url % (image['Id'], '1280', '720', image['ImageMimeType'])

    def update_item(self, i):
        self.item['mode'] = self.mode
        self.item['title'] = utfenc(self.title)
        self.item['plot'] = utfenc(self.description)
        self.item['id'] = self.id
        self.item['type'] = utfenc(resources(self.type))

        if self.params:
            self.item['params'] = self.params

        if 'Epg' in i.get('Id', ''):
            if self.competition:
                competition = self.competition['Title']
            if self.sport:
                sport = self.sport['Title']
            time = self.start[11:][:5]
            if self.type == 'Live':
                self.item['title'] = utfenc(unicode('[COLOR red]%s[/COLOR] [COLOR dimgray]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR]' % (time, sport, self.title, competition)))
            else:
                self.item['title'] = utfenc(unicode('%s [COLOR dimgray]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR]' % (time, sport, self.title, competition)))

        elif (self.type == 'UpComing' or 'Scheduled' in i.get('Id', '')) or (self.type == 'Highlights'):
            if self.type == 'UpComing':
                day = resources(days(self.type, self.now, self.start))
                sub_title = unicode('%s %s' % (day, self.start[11:][:5]))
            else:
                sub_title = resources(self.type)
            self.item['title'] = utfenc(unicode('%s (%s)' % (self.title, sub_title)))

        if self.start:
            self.item['date'] = self.start[:10]

        self.item['related'] = self.related
        self.item['sport'] = self.sport
        self.item['competition'] = self.competition

        self.add_thumb(i)
        self.add_duration(i)