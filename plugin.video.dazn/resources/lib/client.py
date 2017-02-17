# -*- coding: utf-8 -*-

import simple_requests as requests
from .common import *

class Client:

    def __init__(self):

        self.TOKEN = token
        self.POST_DATA = {}

        self.HEADERS = {
            'Content-Type': 'application/json',
            'Referer':  base_url
        }

        self.PARAMS = {
            '$format': 'json',
            'LanguageCode': '%s' % language,
            'Country': '%s' % country
        }

        self.STARTUP = api_base % ('v1') + 'Startup'
        self.RAIL = api_base % ('v1') + 'Rail'
        self.RAILS = api_base % ('v1') + 'Rails'
        self.EPG = api_base % ('v1') + 'Epg'
        self.PLAYBACK = api_base % ('v1') + 'Playback'
        self.SIGNIN = api_base % ('v2') + 'SignIn'
        self.SIGNOUT = api_base % ('v1') + 'SignOut'
        self.REFRESH = api_base % ('v2') + 'RefreshAccessToken'

    def rails(self, id, params=''):
        self.PARAMS['groupId'] = '%s' % id
        self.PARAMS['params'] = '%s' % params
        return self.request(self.RAILS)
        
    def rail(self, id, params=''):
        self.PARAMS['id'] = '%s' % id
        self.PARAMS['params'] = '%s' % params
        return self.request(self.RAIL)
    
    def epg(self, date='today'):
        self.PARAMS['date'] = date
        return self.request(self.EPG)
        
    def playback_data(self, id):
        self.POST_DATA = {
            'AssetId': id,
            'Format': 'MPEG-DASH',
            'PlayerId': 'DAZN-' + addon.getSetting('device_id'),
            'Secure': 'true',
            'PlayReadyInitiator': 'false',
            'BadManifests': [],
            'LanguageCode': '%s' % language,
        }
        return self.request(self.PLAYBACK)
        
    def playback(self, id):
        self.HEADERS['Authorization'] = 'Bearer ' + self.TOKEN
        data = self.playback_data(id)
        if data.get('odata.error', None):
            self.errorHandler(data)
            if self.TOKEN:
                data = self.playback_data(id)
        return data
        
    def setToken(self, auth, result):
        log('[%s] signin: %s' % (addon_id, result))
        if auth and result == 'SignedIn':
            self.TOKEN = auth['Token']
            self.HEADERS['Authorization'] = 'Bearer ' + self.TOKEN
        else:
            self.signOut()
        addon.setSetting('token', self.TOKEN)
        
    def signIn(self):
        if re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) and len(password) > 4:
            self.POST_DATA = {
                'Email': utfenc(email),
                'Password': utfenc(password),
                'DeviceId': addon.getSetting('device_id'),
                'Platform': 'web'
            }
            data = self.request(self.SIGNIN)
            if data.get('odata.error', None):
                self.errorHandler(data)
            else:
                if data['AuthTokens']:
                    auth = data['AuthTokens'][0]
                else:
                    auth = ''
                self.setToken(auth, data.get('Result', 'SignInError'))
        else:
            addon.openSettings()
            
    def signOut(self):
        self.HEADERS['Authorization'] = 'Bearer ' + self.TOKEN
        self.POST_DATA = {
            'DeviceId': addon.getSetting('device_id')
        }
        r = self.request(self.SIGNOUT)
        self.TOKEN = ''
        
    def refreshToken(self):
        self.POST_DATA = {
            'OriginalToken': self.TOKEN,
            'DeviceId': addon.getSetting('device_id')
        }
        data = self.request(self.REFRESH)
        if data.get('odata.error', None):
            self.errorHandler(data)
        else:
            self.setToken(data['AuthToken'], data.get('Result', 'RefreshAccessTokenError'))
            
    def startUp(self):
        self.POST_DATA = {
            'LandingPageKey': 'generic',
            'Languages': language,
            'Platform': 'web',
            'Manufacturer': '',
            'PromoCode': ''
        }
        data = self.request(self.STARTUP)
        if data:
            allowed = data['Region']['isAllowed']
            if allowed == True:
                addon.setSetting('language', data['Region']['Language'])
                addon.setSetting('country', data['Region']['Country'])
                if not self.TOKEN:
                    self.signIn()
            else:
                dialog.ok(addon_name, getString(30101))
        self.POST_DATA  = {}
        
    def request(self, url):
        if self.POST_DATA:
            r = requests.post(url, headers=self.HEADERS, data=self.POST_DATA, params=self.PARAMS)
        else:
            r = requests.get(url, headers=self.HEADERS, params=self.PARAMS)
        if r.headers.get('content-type', '').startswith('application/json'):
            return r.json()
        else:
            if not r.status_code == 204:
                log('[%s] error: %s (%s, %s)' % (addon_id, url, str(r.status_code), r.headers.get('content-type', '')))
            return {}
            
    def errorHandler(self, data):
        msg  = data['odata.error']['message']['value']
        code = str(data['odata.error']['code'])
        log('[%s] error: %s (%s)' % (addon_id, msg, code))
        if code == '1':
            self.refreshToken()
        elif code == '2':
            self.signIn()
        elif code == '7':
            dialog.ok(addon_name, getString(30107))
        elif code == '10000':
            self.refreshToken()
        elif code == '10008':
            dialog.ok(addon_name, getString(30108))
        elif code == 'InvalidAccount' or code == 'InvalidPassword':
            dialog.ok(addon_name, getString(30151))
        elif code == 'unableFindEmail':
            dialog.ok(addon_name, getString(30152))
        else:
            dialog.ok(addon_name, msg)