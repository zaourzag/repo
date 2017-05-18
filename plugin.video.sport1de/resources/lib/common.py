# -*- coding: utf-8 -*-

import json,os,re,sys,urllib,urlparse
import time,datetime,uuid
import xbmc,xbmcaddon,xbmcgui,xbmcplugin,xbmcvfs

addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()
dialog = xbmcgui.Dialog()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
version = addon.getAddonInfo('version')
icon = addon.getAddonInfo('icon')
fanart = addon.getAddonInfo('fanart')
cookie = addon.getSetting('cookie')
store_creds = addon.getSetting('store_creds') == 'true'
if not store_creds:
    addon.setSetting('email', '')
    addon.setSetting('password', '')

www_base = 'http://www.sport1.de'
video_base = 'http://video.sport1.de'
tv_base = 'http://tv.sport1.de'
api_base = 'http://api.sport1.de'

def log(msg):
    xbmc.log(str(msg), xbmc.LOGNOTICE)

def build_url(query):
    return sys.argv[0] + '?' + urllib.urlencode(query)
    
def utfenc(str):
    try:
        str = str.encode('utf-8')
    except:
        pass
    return str

def uniq_id(t=1):
    mac_addr = xbmc.getInfoLabel('Network.MacAddress')
    if not ":" in mac_addr: mac_addr = xbmc.getInfoLabel('Network.MacAddress')
    # hack response busy
    i = 0
    while not ":" in mac_addr and i < 3:
        i += 1
        time.sleep(t)
        mac_addr = xbmc.getInfoLabel('Network.MacAddress')
    if ":" in mac_addr and t == 1:
        addon.setSetting('device_id', str(uuid.UUID(md5(str(mac_addr.decode("utf-8"))).hexdigest())))
        return True
    elif ":" in mac_addr and t == 2:
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(mac_addr)).bytes
    else:
        log("[%s] error: failed to get device id (%s)" % (addon_id, str(mac_addr)))
        dialog.ok(addon_name, 'Fehler beim Abrufen der Geräte-ID. Bitte erneut versuchen.')
        return False