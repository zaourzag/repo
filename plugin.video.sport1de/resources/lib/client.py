# -*- coding: utf-8 -*-

import requests
from credentials import Credentials
from common import *

class Client:

    def __init__(self):
        
        self.headers = {
            'Referer': video_base,
            'Host': 'video.sport1.de'
        }
        self.cookie = cookie

    def get_video_root(self):
        return self.json_request(video_base + '/api/navigations/video_navigation_root')
    
    def get_resource(self, url):
        return self.json_request(url)

    def get_playlist(self,url):
        return self.json_request(url)

    def get_video(self,id):
        return self.json_request(video_base + '/api/video/%s' % (id))

    def get_tv_epg(self):
        return self.json_request(video_base + '/api/epg/tv')

    def get_fm_epg(self):
        return self.json_request(video_base + '/api/epg/fm/amazon')
        
    def get_tv(self, url=False):
        self.headers['Referer'] = tv_base
        self.headers['Host'] = 'tv.sport1.de'
        
        if url:
            if not '/sport1/' in url:
                s = requests.Session()
                self.headers['cookie'] = cookie
                text = s.get(tv_base + '/home/index.php', headers=self.headers).text
                if 'sso_tv_sport1_logged_in=true' in text:
                    self.cookie = cookie
                    log('[%s] logged in' % (addon_id))
                else:
                    self.login(s)
        else:
            url = tv_base + '/'
        
        if self.cookie:
            self.headers['cookie'] = self.cookie
        
        return self.get_data(url)

    def login(self, s):
        credentials = Credentials()
        if credentials.email and credentials.password:
            post_data = {
                'LOGIN_NAME': credentials.email,
                'LOGIN_PW': credentials.password,
                'AID': '3',
                'STLO': '0',
                'JSON': '302'
            }
            login_url = 'https://account.sport1.de/de/api/sso/public/login.js'
            login_r = s.post(login_url, data=post_data)
            data = login_r.json()
            if data.get('redirect', False):
                sspost_data = {
                    '_SSO_SSID': data['_SSO_SSID'],
                    'type': 'login'
                }
                session_url = 'https://tv.sport1.de/exif/sso/notifySession.php'
                r = s.post(session_url, data=sspost_data)
                self.cookie = get_cookie(r.headers['set-cookie'])
                addon.setSetting('cookie', self.cookie)
                log('[%s] login successful' % (addon_id))
                credentials.save()
            else:
                error = data.get('error', 'error')
                response = data.get('response', 'response')
                log('[%s] login error: %s response: %s' % (addon_id, utfenc(error), utfenc(response)))
                dialog.ok(addon_name, utfenc(response))
                credentials.reset()
        
    def get_data(self, url):
        r = requests.get(url, headers=self.headers)
        if r:
            return r.text
        else:
            return ''
            
    def json_request(self, url):
        r = requests.get(url, headers=self.headers)
        if r.headers.get('content-type', '').startswith('application/json'):
            return r.json()
        else:
            log('[%s] error: json request failed with %s response' % (addon_id, str(r.status_code)))
            return {}