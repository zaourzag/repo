# -*- coding: utf-8 -*-

import json,os,re,sys,urllib,urlparse
import time,datetime
import xbmc,xbmcaddon,xbmcgui,xbmcplugin,xbmcvfs
import uuid
from hashlib import md5

addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()
dialog = xbmcgui.Dialog()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
version = addon.getAddonInfo('version')
icon = addon.getAddonInfo('icon')
fanart = addon.getAddonInfo('fanart')
force_view = addon.getSetting('force_view') == 'true'
content = addon.getSetting('content')
view_id = addon.getSetting('view_id')
userid = addon.getSetting('userid')
hkey = addon.getSetting('hkey')
store_creds = addon.getSetting('store_creds') == 'true'
if not store_creds:
    addon.setSetting('email', '')
    addon.setSetting('password', '')

base_url = 'http://www.eurosportplayer.com'

def log(msg):
    xbmc.log(str(msg), xbmc.LOGNOTICE)
    
def getString(id):
    return utfenc(addon.getLocalizedString(id))

def build_url(query):
    return sys.argv[0] + '?' + urllib.urlencode(query)
    
def utfenc(str):
    try:
        str = str.encode('utf-8')
    except:
        pass
    return str

def clearString(str):
    try:
        str = re.sub('\(  .+?\)$|<.+?>|wifi tablet ios|none', '', str, flags=re.I)
    except:
        pass
    return str

def timedelta_total_seconds(timedelta):
    return (
        timedelta.microseconds + 0.0 +
        (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6

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
        dialog.ok(addon_name, getString(30051))
        return False