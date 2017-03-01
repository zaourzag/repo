# -*- coding: utf-8 -*-
    
def warning(text, title = 'Zattoo Live TV', time = 4500, exit = False):
    import xbmc
    import xbmcaddon
    import os.path
    icon = os.path.join(xbmc.translatePath(xbmcaddon.Addon('plugin.video.zattoo_com').getAddonInfo('path')).decode('utf-8'), 'icon.png')
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (title, text, time, icon))
    if exit:
        import sys
        sys.exit(0)

