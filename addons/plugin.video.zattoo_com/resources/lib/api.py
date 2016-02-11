# -*- coding: utf-8 -*-
import urllib
import urllib2
from re import search
import xbmcaddon

addon = xbmcaddon.Addon(id = 'plugin.video.zattoo_com')

def get_app_token():
    try:
        html = urllib2.urlopen('http://zattoo.com/').read()
        return search("window\.appToken\s*=\s*'(.*)'", html).group(1)
    except urllib2.URLError:
        from resources.lib.functions import warning
        return warning('Keine Netzwerkverbindung!', exit = True)
    except:
        return ''
    
def extract_session_id(cookie):
    if cookie:
        return search('beaker\.session\.id\s*=\s*([^\s;]*)', cookie).group(1)
    return ''
    
def get_session_cookie():
    header = {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    post_data = 'lang=en&client_app_token=%s&uuid=d7512e98-38a0-4f01-b820-5a5cf98141fe&format=json' % get_app_token()
    req = urllib2.Request('http://zattoo.com/zapi/session/hello', post_data, header)
    return extract_session_id(urllib2.urlopen(req).info().getheader('Set-Cookie'))

def update_pg_hash(hash):
    addon.setSetting(id = 'pg_hash', value = hash)
    
def update_session(session): 
    addon.setSetting(id = 'session', value = session)
    
def get_json_data(api_url, cookie, post_data = None):
    header = {
            'Accept': 'application/json', 
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'beaker.session.id=' + cookie
        }
    if post_data:
        post_data = urllib.urlencode(post_data)
    req = urllib2.Request(api_url, post_data, header)
    response = urllib2.urlopen(req)
    new_cookie = extract_session_id(response.info().getheader('Set-Cookie'))
    if new_cookie:
        update_session(new_cookie)
    return response.read()
    
def login():
    USER_NAME = addon.getSetting('username')
    PASSWORD = addon.getSetting('password')
    if not USER_NAME or not PASSWORD:
        from resources.lib.functions import warning
        return warning('Bitte Benutzerdaten eingeben!', exit = True)
    handshake_cookie = get_session_cookie()
    try:
        login_json_data = get_json_data('https://zattoo.com/zapi/account/login', handshake_cookie, {'login': USER_NAME, 'password': PASSWORD})
    except urllib2.HTTPError:
        from resources.lib.functions import warning
        return warning('Falsche Logindaten!', exit = True)        
    import json
    pg_hash = json.loads(login_json_data)['account']['power_guide_hash']
    update_pg_hash(pg_hash)
    
    