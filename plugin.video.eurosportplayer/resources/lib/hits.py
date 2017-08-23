# -*- coding: utf-8 -*-

from common import *

class Hits:

    def __init__(self, i, epg=False):
        self.item = {}
        self.epg = epg
        self.type = i['type']
        self.now = datetime.datetime.now().strftime(time_format)
        self.titles = i['titles']
        self.photos = i['photos']
        self.duration = runtime_to_seconds(i['runTime'])
        self.linear = False
        self.language = addon.getSetting('language')
        if self.type == 'Airing':
            self.airing(i)
        elif self.type == 'Video':
            self.video(i)
    
    def airing(self, i):
        self.channel = i['channel']
        self.start = utc2local(i['startDate'])
        self.end = utc2local(i['endDate'])
        self.playback = i['playbackUrls']
        self.config = i['mediaConfig']
        self.livebroadcast = i['liveBroadcast']
        self.linear = i['linear']
        self.airing_item()
        
    def airing_info(self):
        for i in self.titles:
            self.title = i['title']
            self.plot = i['descriptionLong']
            if i['language'] == self.language:
                break
        if not self.title:
            self.title = self.plot
    
    def airing_images(self):
        for i in self.photos:
            if i['width'] == 770 and i['height'] == 432:
                self.item['thumb'] = i['uri']
            if i['width'] == 1600:
                self.item['fanart'] = i['uri']
    
    def airing_item(self):
        self.airing_info()
        name = self.channel['callsign']
        producttype = self.config['productType']
        start = plot_time(self.start)
        end = plot_time(self.end)
        if producttype == 'LIVE' and self.livebroadcast and not self.epg:
            self.title = '{0} [COLOR red]LIVE[/COLOR] [I]{1}[/I]'.format(utfenc(name), utfenc(self.title))
        elif self.epg:
            if not self.playback:
                self.title = '{0} [COLOR dimgray]{1} {2}[/COLOR]'.format(start, utfenc(name), utfenc(self.title))
            else:
                self.title = '{0} [COLOR dimgray]{1}[/COLOR] {2}'.format(start, utfenc(name), utfenc(self.title))
        else:
            self.title = '{0} [I]{1}[/I]'.format(utfenc(name), utfenc(self.title))
        if producttype == 'LIVE':
            self.plot = '{0} - {1}\n{2}'.format(start, end, utfenc(self.plot))
            if not self.epg:
                self.duration = timedelta_total_seconds(time_stamp(self.end)-time_stamp(self.now))
        else:
            self.plot = utfenc(self.plot)
        self.airing_images()
        self.create_item()
    
    def video(self, i):
        media = i['media']
        self.playback = media[0]['playbackUrls']
        self.video_item()
    
    def video_info(self):
        for i in self.titles:
            self.title = i['title']
            self.plot = i['summaryLong']
            tags = i['tags']
            for t in tags:
                if t['type'] == 'language':
                    if t['value'] == self.language:
                        break
        if not self.title:
            self.title = self.plot
    
    def video_images(self):
        photos = self.photos[0]['photos']
        for i in photos:
            if i['width'] == 770 and i['height'] == 432:
                self.item['thumb'] = i['imageLocation']
            if i['width'] == 1600:
                self.item['fanart'] = i['imageLocation']
    
    def video_item(self):
        self.video_info()
        self.title = utfenc(self.title)
        self.plot = utfenc(self.plot)
        self.create_item()
        self.video_images()
    
    def playback_id(self):
        id = ''
        for i in self.playback:
            id = i['href']
            if self.linear and not self.epg and i['rel'] == 'linear':
                break
            elif self.epg and i['rel'] == 'video':
                break
        return id
        
    def create_item(self):
        self.item['mode'] = 'play'
        self.item['title'] = self.title
        self.item['id'] = self.playback_id()
        self.item['plot'] = self.plot
        self.item['duration'] = self.duration