# -*- coding: utf-8 -*-

from common import *

class Details:

    def __init__(self, i):
        self.item = {}
        self.data = i
        self.stream = re.search('class="stream"', i)
        self.vod = re.search('class="vod"', i)
        self.highlight = re.search('class="highlight"', i)
        self.video = ''
        self.language = ''
        self.set_content()
        
        if self.video:
            self.update_item()
        
    def set_content(self):
        if self.vod:
            self.video = self.data
            self.link = '%s/?pageid=113&clean=1&getVodEmbed=%s'
        elif self.highlight:
            self.video = self.data
            self.link = '%s/?pageid=113&clean=1&getHighlightEmbed=%s'
        elif self.stream:
            self.video = self.data
            self.link = '%s/?pageid=113&clean=1&getStreamEmbed=%s'
        elif re.search('<a href="http', self.data):
            self.video = self.data
            self.link = re.search('<a href="(.+?)"', self.video).group(1)
        img = re.search('src="(.+?/flag/.+?)"', self.video)
        if img:
            self.language = '(%s)' % (re.search('/flag/(.+?)\.', img.group(1)).group(1))
            
    def get_title(self):
        name = re.sub('<.+?>', '', self.video).strip()
        return utfenc('%s %s' % (name, self.language))
        
    def update_item(self):
        self.item['mode'] = 'play'
        self.item['title'] = self.get_title()
        
        if not self.link.startswith('http'):
            _id_ = re.search('id="(\d+)"', self.video).group(1)
            self.item['id'] = self.link % (base_hltv, _id_)
        else:
            self.item['id'] = self.link