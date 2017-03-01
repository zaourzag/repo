# -*- coding: utf-8 -*-
import sys
import xbmcplugin

def add_folder(title, thumb, mode, desc = '', fanart = '', icon = ''):
    import xbmcgui
    link = '%s?%s' % (sys.argv[0], mode)
    item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    item.setProperty('fanart_image', fanart or thumb)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=True)

def list_index():
    import xbmc
    import xbmcaddon
    import os.path
    from resources.lib.functions import translate
    addon_path = xbmc.translatePath(xbmcaddon.Addon('plugin.video.arte_tv').getAddonInfo('path')).decode('utf-8')
    add_folder(translate(30001), os.path.join(addon_path, 'resources', 'media', 'highlights.png'), 'mode=highlights&site=index')
    add_folder(translate(30002), os.path.join(addon_path, 'resources', 'media', 'plus7.png') , 'mode=plus7')
    add_folder(translate(30003), os.path.join(addon_path, 'resources', 'media', 'plus7.png'), 'mode=epg')
    add_folder(translate(30004), os.path.join(addon_path, 'resources', 'media', 'livetv.png'), 'mode=live-tv')
    add_folder('Arte Concert', os.path.join(addon_path, 'resources', 'media', 'concert.png'), 'mode=concert')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))