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
country = addon.getSetting('country')
language = xbmc.getLanguage(0, False)
if not language:
    language = addon.getSetting('language')

base_url = 'http://www.eurosportplayer.com'
global_base = 'https://global-api.svcs.eurosportplayer.com/'
search_base = 'https://search-api.svcs.eurosportplayer.com/'

time_format = '%Y-%m-%dT%H:%M:%SZ'
date_format = '%Y-%m-%d'

def log(msg):
    xbmc.log(str(msg), xbmc.LOGNOTICE)
    
def getString(_id):
    return utfenc(addon.getLocalizedString(_id))

def build_url(query):
    return sys.argv[0] + '?' + urllib.urlencode(query)
    
def utfenc(string):
    try:
        string = string.encode('utf-8')
    except:
        pass
    return string

def time_stamp(str_date):
    return datetime.datetime.fromtimestamp(time.mktime(time.strptime(str_date,time_format)))

def plot_time(date_string, event):
    if event:
        return datetime.datetime(*(time.strptime(date_string, time_format)[0:6])).strftime('%a, %d %b, %H:%M')
    else:
        return datetime.datetime(*(time.strptime(date_string, time_format)[0:6])).strftime('%H:%M')

def add_zero(s):
    s = s.strip()
    if not len(s) == 2:
        s = '0'+s
    return s

def remove_zero(s):
    if s.startswith('0'):
        s = s[1:]
    return s

def runtime_to_seconds(runtime):
    spl = runtime.split(':')
    seconds = 0
    seconds += int(remove_zero(spl[0]))*60*60
    seconds += int(remove_zero(spl[1]))*60
    seconds += int(remove_zero(spl[2]))
    return seconds

def timedelta_total_seconds(timedelta):
    return (
        timedelta.microseconds + 0.0 +
        (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6

def utc2local(date_string):
    if str(date_string).startswith('2'):
        utc = datetime.datetime(*(time.strptime(date_string, time_format)[0:6]))
        epoch = time.mktime(utc.timetuple())
        offset = datetime.datetime.fromtimestamp(epoch) - datetime.datetime.utcfromtimestamp(epoch)
        return (utc + offset).strftime(time_format)

def epg_date(date=False):
    if not date:
        date = datetime.datetime.now().strftime(date_format)
    return datetime.datetime.fromtimestamp(time.mktime(time.strptime(date, date_format)))

def get_prev_day(date):
    return (date - datetime.timedelta(days=1))

def get_next_day(date):
    return (date + datetime.timedelta(days=1))

def get_date():
    date = epg_date()
    dlg = dialog.numeric(1, getString(30230))
    if dlg:
        spl = dlg.split('/')
        date = '%s-%s-%s' % (spl[2], add_zero(spl[1]), add_zero(spl[0]))
    prev_date = get_prev_day(epg_date(date))
    return prev_date.strftime(date_format), date

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
        device_id = str(uuid.UUID(md5(str(mac_addr.decode("utf-8"))).hexdigest()))
        addon.setSetting('device_id', device_id)
        return True
    elif ":" in mac_addr and t == 2:
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(mac_addr)).bytes
    else:
        log("[{0}] error: failed to get device id ({1})".format(addon_id, str(mac_addr)))
        dialog.ok(addon_name, getString(30051))
        return False