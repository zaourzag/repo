# -*- coding: utf-8 -*-

import simple_requests as requests
from common import *

class Client:

    def __init__(self):
        
        VS_URL = 'http://videoshop.ws.eurosport.com/JsonProductService.svc/'
        CRM_URL = 'https://playercrm.ssl.eurosport.com/JsonPlayerCrmApi.svc/'
        
        self.CRM_LOGIN = CRM_URL + 'Login'
        self.VIDEO_CHANNELS = VS_URL  + 'GetAllChannelsCache'
        self.VIDEO_CATCHUPS = VS_URL  + 'GetAllCatchupCache'
        self.VIDEO_TOKEN = VS_URL  + 'GetToken'

        self.headers = {
            'User-Agent': 'iPhone',
            'Referer': base_url
        }

        self.context = {
            'g': '', 
            'd': '2',
            's': '1', 
            'p': '1',
            'b': 'apple'
        }

        self.dvs = {
            'userid': '', 
            'hkey': '', 
            'languageid': '',
        }
        
        self.set_user_data()
        
    def set_user_data(self):
        self.set_location()
        self.dvs['userid'] = userid
        self.dvs['hkey'] = hkey

    def set_location(self):
        data = self.get_data(base_url)
        c = re.search("crmlanguageid\s*:\s*'(\d+)'", data)
        if c:
            self.dvs['languageid'] = c.group(1)
        g = re.search("geoloc\s*:\s*'(\w+)'", data)
        if g:
            self.context['g'] = g.group(1)
        log('[%s] geolocation: %s' % (addon_id, self.context['g']))

    def set_user_ref(self):
        user_ref = self.ep_login()
        if user_ref.get('Response', None):
            log('[%s] login: %s' % (addon_id, utfenc(user_ref['Response']['Message'])))
        if user_ref.get('Id', '') and user_ref.get('Hkey', ''):
            self.dvs['userid'] = user_ref['Id']
            addon.setSetting('userid', user_ref['Id'])
            self.dvs['hkey'] = user_ref['Hkey']
            addon.setSetting('hkey', user_ref['Hkey'])
    
    def channels(self):
    
        encoded = urllib.urlencode({'data':json.dumps(self.dvs), 'context':json.dumps(self.context)})
        url = self.VIDEO_CHANNELS + '?' + encoded
        return self.json_request(url)

    def catchups(self):
        encoded = urllib.urlencode({'data':json.dumps(self.dvs), 'context':json.dumps(self.context)})
        url = self.VIDEO_CATCHUPS + '?' + encoded
        return self.json_request(url)
        
    def ep_login(self):
        login_data = {
            'email': utfenc(email), 
            'password': utfenc(password), 
            'udid': addon.getSetting('device_id')
        }
        encoded = urllib.urlencode({'data':json.dumps(login_data), 'context':json.dumps(self.context)})
        url = self.CRM_LOGIN + '?' + encoded
        return self.json_request(url)
        
    def logged_in(self, data):
        if data.get('Response', None):
            code = data['Response']['ResponseCode']
            msg = data['Response']['ResponseMessage']
            if code == 1 or code == 4:
                return True
            else:
                if not code == 2:
                    dialog.ok(addon_name, utfenc(msg))
                log('[%s] error: %s' % (addon_id, utfenc(msg)))
        return False
        
    def token(self):
    
        def get_url():
            encoded = urllib.urlencode({'data':json.dumps(self.dvs), 'context':json.dumps(self.context)})
            return self.VIDEO_TOKEN + '?' + encoded
        
        data = self.json_request(get_url())
        if not self.logged_in(data):
            self.set_user_ref()
            data = self.json_request(get_url())
        return data
        
    def get_data(self, url):
        r = requests.get(url, headers=self.headers, allow_redirects=True)
        if r:
            return r.text
        else:
            log('[%s] error: request failed (%s)' % (addon_id, str(r.status_code)))
            return ''
            
    def json_request(self, url):
        r = requests.get(url, headers=self.headers)
        if r.headers.get('content-type', '').startswith('application/json'):
            return r.json()
        else:
            log('[%s] error: json request failed (%s)' % (addon_id, str(r.status_code)))
            return {}