# -*- coding: utf-8 -*-

from common import *

class Playback:

    def __init__(self, data):
        empty            = [{'ManifestUrl':'', 'LaUrl':'', 'CdnName':''}]
        details          = data.get('PlaybackDetails', empty)
        n                = self.location(details)
        self.ManifestUrl = self.parse_data(n, details, 'ManifestUrl')
        self.LaUrl       = self.parse_data(n, details, 'LaUrl')
        
    def parse_data(self, n, data, id):
        return data[n][id].replace('https','http')
        
    def location(self, data):
        l = ['auto-auto', 'akamai-dc1', 'akamai-dc2', 'footprint-dc1', 'footprint-dc2']
        n = 0
        for s in data:
            url = s['ManifestUrl']
            spl = l[cdn].split('-')
            if spl[0] in url and spl[1] in url:
                return n
            n += 1
        return 0