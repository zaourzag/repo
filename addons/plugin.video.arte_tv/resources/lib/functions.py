import xbmcaddon

def translate(tid):
    return xbmcaddon.Addon(id = 'plugin.video.arte_tv').getLocalizedString(tid).encode('utf-8')