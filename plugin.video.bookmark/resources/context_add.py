# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import sys, re, os
import json
import time
import codecs
from lib._json import read_json, write_json

loglevel = 1
xbmc.log('plugin.video.bookmark - init context add')

addonID = "plugin.video.bookmark"
addon = xbmcaddon.Addon(id=addonID)
home = addon.getAddonInfo('path').decode('utf-8')
icon = os.path.join(home, 'icon.png')
userdataDir = xbmc.translatePath(addon.getAddonInfo('profile'))
dbDir = os.path.join(userdataDir, 'db') + '/'
path = xbmc.getInfoLabel("ListItem.Path")
fanart = ''
log_msg = 'plugin.video.bookmark - '
time_now = time.strftime("%Y-%m-%d - %H:%M:%S")
TRANSLATE = addon.getLocalizedString


def main():
    addon_id = get_addon_id(path)
    db_file = dbDir + addon_id + '.json'
    new_data = get_data_episode()
    add_to_db(new_data, db_file)


def get_data_episode():
    name = xbmc.getInfoLabel("ListItem.Label").decode('UTF-8')
    link = xbmc.getInfoLabel("ListItem.FileNameAndPath").decode('UTF-8')
    plot = xbmc.getInfoLabel("ListItem.Plot").decode('UTF-8')
    dura = xbmc.getInfoLabel("ListItem.Duration").decode('UTF-8')
    icon = xbmc.getInfoLabel("ListItem.Thumb").decode('UTF-8')
    fana = xbmc.getInfoLabel("ListItem.Art(fanart)").decode('UTF-8')
    date = time_now
    data = {'name': name, 'link': link, 'icon': icon, 'fana': fana, 'plot': plot, 'dura': dura, 'date': date}
    return data


def add_to_db(new_data, db_file):
    xbmc.log(log_msg + '!ADD TO DB!', loglevel)
    xbmc.log(log_msg + 'File: ' + db_file, loglevel)
    db_data = read_json(db_file)
    for i in db_data:
        if i['name'] == new_data['name']:
            dialog = xbmcgui.Dialog()
            # 30210 = bookmark video addon || 30211 = Already bookmarked!
            # keep item icon?
            dialog.notification(TRANSLATE(30210), TRANSLATE(30211), i['icon'], 3000)
            return
    db_data.append(new_data)
    write_json(db_file, db_data)


def get_addon_id(path):
    xbmc.log(log_msg + '!GET ADDON ID!', loglevel)
    xbmc.log(log_msg + 'Path: ' + path, loglevel)
    addon_id = 'unknown'
    match = re.match(r'plugin://(.*?)\/', path)
    if match:
        addon_id = match.group(1)
    elif not path.startswith("plugin"):
        addon_id = "Kodi-DB"
    xbmc.log(log_msg + 'AddonID: ' + addon_id, loglevel)
    return addon_id


if __name__ == '__main__':
    main()
