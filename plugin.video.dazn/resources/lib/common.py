# -*- coding: utf-8 -*-

import json,os,sys,urllib,urlparse
import time,datetime,random,re
import xbmc,xbmcaddon,xbmcgui,xbmcplugin,xbmcvfs
from uuid import UUID
from hashlib import md5

addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()
dialog = xbmcgui.Dialog()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
version = addon.getAddonInfo('version')
icon = addon.getAddonInfo('icon')
fanart = addon.getAddonInfo('fanart')
content = addon.getSetting('content')
view_id = addon.getSetting('view_id')
force_view = addon.getSetting('force_view') == 'true'
email = addon.getSetting('email')
password = addon.getSetting('password')
token = addon.getSetting('token')
language = xbmc.getLanguage(0, False)
country = addon.getSetting('country')
cdn = int(addon.getSetting('server'))

api_base = 'https://isl.dazn.com/misl/'

time_format = '%Y-%m-%dT%H:%M:%SZ'
date_format = '%Y-%m-%d'

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
    
def getString(id):
    return addon.getLocalizedString(id)

def time_stamp(str_date):
    return datetime.datetime.fromtimestamp(time.mktime(time.strptime(str_date,time_format)))

def timedelta_total_seconds(timedelta):
    return (
        timedelta.microseconds + 0.0 +
        (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6

def utc2local(date_string):
    if date_string:
        utc = datetime.datetime(*(time.strptime(date_string, time_format)[0:6]))
        epoch = time.mktime(utc.timetuple())
        offset = datetime.datetime.fromtimestamp(epoch) - datetime.datetime.utcfromtimestamp(epoch)
        return (utc + offset).strftime(time_format)

def uniq_id():
    mac_addr = xbmc.getInfoLabel('Network.MacAddress')
    if not ":" in mac_addr: mac_addr = xbmc.getInfoLabel('Network.MacAddress')
    # hack response busy
    i = 0
    while not ":" in mac_addr and i < 3:
        i += 1
        time.sleep(1)
        mac_addr = xbmc.getInfoLabel('Network.MacAddress')
    if ":" in mac_addr:
        mac_addr = str(UUID(md5(str(mac_addr.decode("utf-8"))).hexdigest()))
        addon.setSetting('device_id', mac_addr)
        return True
    else:
        log("[%s] error: failed to get device id (%s)" % (addon_id, str(mac_addr)))
        dialog.ok(addon_name, getString(30051))
        return False
    
def days(title, now, start):
    today = datetime.date.today()
    if start and not title == 'Live':
        if now[:10] == start[:10]:
            return 'Today'
        elif str(today + datetime.timedelta(days=1)) == start[:10]:
            return 'Tomorrow'
        for i in range(2,8):
            if str(today + datetime.timedelta(days=i)) == start[:10]:
                return (today + datetime.timedelta(days=i)).strftime('%A')
    return title

def epg_date(date):
    return datetime.datetime.fromtimestamp(time.mktime(time.strptime(date, date_format)))

def get_prev_day(date):
    return (date - datetime.timedelta(days=1))

def get_next_day(date):
    return (date + datetime.timedelta(days=1))

def input_date():
    date = 'today'
    dg = dialog.input(getString(30230), type=xbmcgui.INPUT_DATE)
    if dg:
        spl = dg.split('/')
        date = '%s-%s-%s' % (spl[2], spl[1], spl[0])
    return date