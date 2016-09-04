import os
import sys
import requests
import time

class EweTv():
    def __init__(self, username, password):
        self.app_id = app_id = 'HJ8n59WO0Jcmr9l0U0FLXYlXaQOyzn'
        self.session = requests.Session()
        self.session.headers["User-Agent"] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
        self.username = username
        self.password = password
        self.valid_until = str(time.time()).replace('.', '')
        self.current_channel_id = ''

    def login(self):
        url = 'https://tvonline.ewe.de/external/client/core/Login.do'
        headers = self.session.headers
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {'appId': self.app_id, 'userId': self.username, 'password': self.password}
        r = self.session.post(url, data=payload, headers=headers)
        print r.text
        if 'errors' in r.json():
            return False

        return True       

    def getChannelUrl(self):
        channels = self.getChannelList()
        for c in channels:
            if c['vodkatvChannelId'] == self.current_channel_id:
                return c['url']

        return ''

    def getChannelList(self):
        url = 'https://tvonline.ewe.de/external/client/plugins/television/FindChannels.do'
        headers = self.session.headers
        r = self.session.get(url, headers=headers)
        data = r.json()
        if 'errors' in data:
            if data['errors'][0]['code'] == 'access_denied':
                if self.login():
                    self.getChannelList()
        else:
            return r.json()['channels']['elements']

    def generateM3U(self, path, port):
        channels = self.getChannelList()
        f = open(path, 'w+')
        f.write('#EXTM3U\n')
        for c in channels:
            line = '#EXTINF:-1 tvg-id=%s.de tvg-logo=%s.de tvg-name=%s, %s' % (c['name'].replace(' ', ''), c['name'].replace(' ', ''), c['name'].replace(' ', '_'), c['name'])
            line2 = 'http://127.0.0.1:' + str(port) + '/channel.m3u8?channel_id=' + c['vodkatvChannelId']
            f.write(line.encode('utf8') + '\n')
            f.write(line2.encode('utf8') + '\n')

        f.close()

    
