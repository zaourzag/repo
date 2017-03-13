# -*- coding: utf-8 -*-

import json,os,re,sys,urllib,urlparse
import time,datetime
import xbmc,xbmcaddon,xbmcgui,xbmcplugin,xbmcvfs

addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()
dialog = xbmcgui.Dialog()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
version = addon.getAddonInfo('version')
icon = addon.getAddonInfo('icon')
fanart = addon.getAddonInfo('fanart')
email = addon.getSetting('email')
password = addon.getSetting('password')
cookie = addon.getSetting('cookie')

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