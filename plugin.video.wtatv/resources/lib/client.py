# -*- coding: utf-8 -*-

import simple_requests as requests
from credentials import Credentials
from .common import *
import xmltodict

class Client:

    def __init__(self):

        self.HEADERS = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'http://www.wtatv.com',
            'Referer': 'http://www.wtatv.com/home',
            'Cookie': cookie
        }
        
    def login(self):
        credentials = Credentials()
        LOGIN_DATA = {
            'login.username': utfenc(credentials.email),
            'login.password': utfenc(credentials.password),
            'login.successRedirectUrl': '/on-demand',
            'login.failureRedirectUrl': '/login?loginError=1'
        }
        r = requests.post('https://secure.wtatv.com/system/userlogin', headers=self.HEADERS, data=LOGIN_DATA, allow_redirects=False)
        if '/on-demand' in r.headers.get('location', '') and r.headers.get('set-cookie', ''):
            cookie = r.headers['set-cookie']
            self.HEADERS.update({'Cookie': cookie})
            addon.setSetting('cookie', cookie)
            log('[%s] info: loginsuccess' % (addon_id))
            credentials.save()
        else:
            log('[%s] info: loginerror' % (addon_id))
            credentials.reset()
            
    def logout(self):
        r = requests.get('https://secure.wtatv.com/system/userlogout', headers=self.HEADERS, allow_redirects=False)

    def events(self):
        return requests.get(base_url + '/json/wtaEvents').json()
        
    def features(self):
        return requests.post(base_url + '/json/videos/pageSize/50/type/features/').json()
    
    def ondemand(self):
        return requests.post(base_url + '/json/videos/pageSize/50/type/on-demand/').json()
    
    def streaming(self, id):
        return self.request_xml_to_json('http://www.wtatv.com/streaming/multiformat/streaminfo/index.html?partnerId=8084&eventId=%s' % id)
    
    def vod(self, url):
        return requests.get(base_url + url, headers=self.HEADERS).text
        
    def request_xml_to_json(self, url):
    
        result = {}
        
        def get_data(url):
            return requests.get(url, headers=self.HEADERS).text
        
        data = get_data(url)
        
        if 'usernotloggedin' in data:
            self.login()
            data = get_data(url)
            
        notices = ['usernotloggedin','eventnotstarted','invalideventid','geoblocked','nopurchaseorderfound','eventover']
        if any(x in data for x in notices):
            log('[%s] info: %s' % (addon_id, data))
            dialog.ok('WTA TV Error', data)
            
        else:
            try:
                o = xmltodict.parse(data)
                json_data = json.loads(json.dumps(o))
                return json_data
            except:
                pass
            
        return result