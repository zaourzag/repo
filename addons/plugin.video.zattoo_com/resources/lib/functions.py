# -*- coding: utf-8 -*-

def get_parameter_dict(parameters):
    param_dict = {}
    if parameters:
        param_pairs = parameters[1:].split('&')
        for pair in param_pairs:
            splitted = pair.split('=')
            if (len(splitted)) == 2:
                param_dict[splitted[0]] = splitted[1]
    return param_dict
    
def warning(text, title = 'Zattoo Live TV', time = 4500, exit = False):
    import xbmc
    import xbmcaddon
    import os.path
    icon = os.path.join(xbmc.translatePath(xbmcaddon.Addon('plugin.video.zattoo_com').getAddonInfo('path')).decode('utf-8'), 'icon.png')
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (title, text, time, icon))
    if exit:
        import sys
        sys.exit(0)

