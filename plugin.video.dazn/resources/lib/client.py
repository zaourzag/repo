# -*- coding: utf-8 -*-

import simple_requests as requests
from credentials import Credentials
from common import *

class Client:

    def __init__(self):
        self.TOKEN = token
        self.POST_DATA = {}
        self.ERRORS = 0

        self.HEADERS = {
            'Content-Type': 'application/json',
            'Referer': api_base
        }

        self.PARAMS = {
            '$format': 'json',
            'LanguageCode': language,
            'Country': country
        }

        self.STARTUP = api_base + 'v2/Startup'
        self.RAIL = api_base + 'v2/Rail'
        self.RAILS = api_base + 'v3/Rails'
        self.EPG = api_base + 'v1/Epg'
        self.EVENT = api_base + 'v2/Event'
        self.PLAYBACK = api_base + 'v1/Playback'
        self.SIGNIN = api_base + 'v3/SignIn'
        self.SIGNOUT = api_base + 'v1/SignOut'
        self.REFRESH = api_base + 'v3/RefreshAccessToken'
        
        if not self.TOKEN:
            self.signIn()
            
    def content_data(self, url):
        data = self.request(url)
        if data.get('odata.error', None):
            self.errorHandler(data)
        return data

    def rails(self, _id, params=''):
        self.PARAMS['groupId'] = _id
        self.PARAMS['params'] = params
        return self.content_data(self.RAILS)
        
    def rail(self, _id, params=''):
        self.PARAMS['id'] = _id
        self.PARAMS['params'] = params
        return self.content_data(self.RAIL)
    
    def epg(self, params):
        self.PARAMS['date'] = params
        return self.content_data(self.EPG)
    
    def event(self, _id):
        self.PARAMS['Id'] = _id
        return self.content_data(self.EVENT)
        
    def playback_data(self, _id):
        self.HEADERS['Authorization'] = 'Bearer ' + self.TOKEN
        self.POST_DATA = {
            'AssetId': _id,
            'Format': 'MPEG-DASH',
            'PlayerId': 'DAZN-' + addon.getSetting('device_id'),
            'Secure': 'true',
            'PlayReadyInitiator': 'false',
            'BadManifests': [],
            'LanguageCode': language,
        }
        return self.request(self.PLAYBACK)
        
    def playback(self, _id):
        data = self.playback_data(_id)
        if data.get('odata.error', None):
            self.errorHandler(data)
            if self.TOKEN:
                data = self.playback_data(_id)
        return data
        
    def setToken(self, auth, result):
        log('[{0}] signin: {1}'.format(addon_id, result))
        if auth and result == 'SignedIn':
            self.TOKEN = auth['Token']
            self.HEADERS['Authorization'] = 'Bearer ' + self.TOKEN
        else:
            if result == 'HardOffer':
                dialog.ok(addon_name, getString(30161))
            self.signOut()
        addon.setSetting('token', self.TOKEN)
        
    def signIn(self):
        credentials = Credentials()
        if '@' in credentials.email and len(credentials.password) > 4:
            self.POST_DATA = {
                'Email': utfenc(credentials.email),
                'Password': utfenc(credentials.password),
                'DeviceId': addon.getSetting('device_id'),
                'Platform': 'web'
            }
            data = self.request(self.SIGNIN)
            if data.get('odata.error', None):
                self.errorHandler(data)
            else:
                self.setToken(data['AuthToken'], data.get('Result', 'SignInError'))
        else:
            dialog.ok(addon_name, getString(30004))
        if self.TOKEN:
            credentials.save()
        else:
            credentials.reset()
            
    def signOut(self):
        self.HEADERS['Authorization'] = 'Bearer ' + self.TOKEN
        self.POST_DATA = {
            'DeviceId': addon.getSetting('device_id')
        }
        r = self.request(self.SIGNOUT)
        self.TOKEN = ''
        addon.setSetting('token', self.TOKEN)
        
    def refreshToken(self):
        self.HEADERS['Authorization'] = 'Bearer ' + self.TOKEN
        self.POST_DATA = {
            'DeviceId': addon.getSetting('device_id')
        }
        data = self.request(self.REFRESH)
        if data.get('odata.error', None):
            self.signOut()
            self.errorHandler(data)
        else:
            self.setToken(data['AuthToken'], data.get('Result', 'RefreshAccessTokenError'))
            
    def startUp(self):
        kodi_language = get_language()
        self.POST_DATA = {
            'LandingPageKey': 'generic',
            'Languages': '{0}, {1}'.format(kodi_language, language),
            'Platform': 'web',
            'Manufacturer': '',
            'PromoCode': ''
        }
        data = self.request(self.STARTUP)
        region = data.get('Region', {})
        if region.get('isAllowed', False) == True:
            addon.setSetting('country', region['Country'])
            supported = False
            languages = data['SupportedLanguages']
            for i in languages:
                if i == kodi_language:
                    supported = True
                    addon.setSetting('language', i)
                    break
            if not supported:
                addon.setSetting('language', region['Language'])
        else:
            dialog.ok(addon_name, getString(30101))
        
    def request(self, url):
        if self.POST_DATA:
            r = requests.post(url, headers=self.HEADERS, data=self.POST_DATA, params=self.PARAMS)
            self.POST_DATA  = {}
        else:
            r = requests.get(url, headers=self.HEADERS, params=self.PARAMS)
        if r.headers.get('content-type', '').startswith('application/json'):
            return r.json()
        else:
            if not r.status_code == 204:
                log('[{0}] error: {1} ({2}, {3})'.format(addon_id, url, str(r.status_code), r.headers.get('content-type', '')))
            return {}
            
    def errorHandler(self, data):
        self.ERRORS += 1
        msg  = data['odata.error']['message']['value']
        code = str(data['odata.error']['code'])
        log('[{0}] error: {1} ({2})'.format(addon_id, msg, code))
        if code == '10000' and self.ERRORS < 3:
            self.refreshToken()
        elif (code == '401' or code == '10033') and self.ERRORS < 3:
            self.signIn()
        elif code == '7':
            dialog.ok(addon_name, getString(30107))
        elif code == '3001':
            self.startUp()
        elif code == '10006':
            dialog.ok(addon_name, getString(30101))
        elif code == '10008':
            dialog.ok(addon_name, getString(30108))
        elif code == '10049':
            dialog.ok(addon_name, getString(30151))
