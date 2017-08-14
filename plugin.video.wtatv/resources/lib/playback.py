# -*- coding: utf-8 -*-

from common import *

class Live:

    def __init__(self, data):
        self.path = ''
        if data:
            self.parse_data(data)
        
    def parse_data(self, data):
        mediaFormat = data['eventInfo']['availableMediaFormats']['mediaFormat']
        for i in mediaFormat:
            if i['@id'] == '52':
                auth = i['stream']['streamAuth']
                code = i['stream']['streamLaunchCode']
                self.path = code + '?' + auth
                break
        
class Vod:

    def __init__(self, data):
        self.path = ''
        self.parse_data(data)
        
    def parse_data(self, data):
        match = re.findall("data-src='(http.+?)'", data, re.DOTALL)
        if match:
            self.path = match[1]