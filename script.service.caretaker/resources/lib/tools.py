import xbmc
import xbmcaddon
import xbmcgui
import json
import re
import os
import time
import urllib2

__LS__ = xbmcaddon.Addon().getLocalizedString
__profile__ = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))

# Constants

STRING = 0
BOOL = 1
NUM = 2

def writeLog(message, level=xbmc.LOGDEBUG, extra=None):
    xbmc.log('[%s %s] %s' % (xbmcaddon.Addon().getAddonInfo('id'),
                             xbmcaddon.Addon().getAddonInfo('version'),
                             message.encode('utf-8')), level)
    if extra is not None:
        with open(extra, 'a') as handle: handle.writelines('%s\n' % (message.encode('utf-8')))

def jsonrpc(query):
    querystring = {"jsonrpc": "2.0", "id": 1}
    querystring.update(query)
    try:
        response = json.loads(xbmc.executeJSONRPC(json.dumps(querystring, encoding='utf-8')))
        if 'result' in response: return response['result']
    except TypeError, e:
        writeLog('Error executing JSON RPC: %s' % (e.message), xbmc.LOGFATAL)
    return False

def notify(heading, message, icon=xbmcgui.NOTIFICATION_INFO, time=5000):
    xbmcgui.Dialog().notification(heading, message, icon=icon, time=time)

def dialogOk(heading, message):
    xbmcgui.Dialog().ok(heading, message)

def getAddonSetting(setting, sType=STRING, multiplicator=1):
    if sType == BOOL:
        return  True if xbmcaddon.Addon().getSetting(setting).upper() == 'TRUE' else False
    elif sType == NUM:
        try:
            return int(re.match('\d+', xbmcaddon.Addon().getSetting(setting)).group()) * multiplicator
        except AttributeError:
            return 0
    else:
        return xbmcaddon.Addon().getSetting(setting)

def updateBlacklist(cache, remote_source, fallback):
    limit_definition = [86400, 604800, 2419200] # update daily, weekly or monthly (secs)
    limit = limit_definition[getAddonSetting('update', NUM)]

    if not os.path.isfile(cache) or (int(time.time()) - os.path.getmtime(cache) > limit):
        try:
            writeLog('Getting blacklist from gist provider')
            _src = urllib2.urlopen(remote_source, timeout=5).read()
        except urllib2.URLError, e:
            writeLog('Could not read from gist provider', xbmc.LOGFATAL)
            writeLog('%s' % (e.reason), xbmc.LOGFATAL)
            writeLog('Use blacklist provided with addon source instead')
            with open(fallback, 'r') as src: _src = src.read()
        if not os.path.exists(__profile__):
            os.makedirs(__profile__)
        with open(cache, 'w') as _dst: _dst.write(_src)
    else:
        writeLog('Blacklist is up to date')