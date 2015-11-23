# -*- coding: utf-8 -*-
import urllib2
import json
import sys
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import os.path
from resources.lib.functions import translate

def add_folder(title, thumb, mode, desc = '', fanart = '', icon = ''):
    link = '%s?%s' % (sys.argv[0], mode)
    item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    item.setProperty('fanart_image', fanart or thumb)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=True)

def list_index():
    addon_path = xbmc.translatePath(xbmcaddon.Addon('plugin.video.arte_tv').getAddonInfo('path')).decode('utf-8')
    add_folder(translate(30001), os.path.join(addon_path, 'resources', 'media', 'highlights.png'), 'mode=highlights&site=index')
    add_folder(translate(30002), os.path.join(addon_path, 'resources', 'media', 'plus7.png') , 'mode=plus7')
    add_folder(translate(30003), os.path.join(addon_path, 'resources', 'media', 'plus7.png'), 'mode=epg')
    add_folder(translate(30004), os.path.join(addon_path, 'resources', 'media', 'livetv.png'), 'mode=live-tv')
    #add_folder('INFO', os.path.join(addon_path, 'resources', 'media', 'info.png'), '')
    #add_folder('FUTURE', os.path.join(addon_path, 'resources', 'media', 'future.png'), '')
    #add_folder('CREATIVE', os.path.join(addon_path, 'resources', 'media', 'creative.png'), '')
    #add_folder('CONCERT', os.path.join(addon_path, 'resources', 'media', 'concert.png'), '')
    #add_folder('CINEMA', os.path.join(addon_path, 'resources', 'media', 'cinema.png'), '')
    #add_folder(translate(30005), os.path.join(addon_path, 'resources', 'media', 'plus7.png'), 'mode=plus7-search')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))