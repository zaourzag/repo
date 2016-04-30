# -*- coding: utf-8 -*-
import urllib2
import json
import sys
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import os.path
    

def list_all_channels(language = 'de'):
    api_url = 'http://www.arte.tv/papi/tvguide/videos/channels/%s/0.json' % language[0].upper()
    try:
        json_data = urllib2.urlopen(api_url).read()
        video_channels = json.loads(json_data)['videoChannelList']
    except: return False
    addon_path = xbmc.translatePath(xbmcaddon.Addon('plugin.video.arte_tv').getAddonInfo('path')).decode('utf-8')
    for channel in video_channels:
        try:
            channel_id = channel['channelID']
            title = channel['germanLabel'] if language == 'de' else channel['frenchLabel']
            link = '%s?mode=list-videos&category=%s' % (sys.argv[0], channel_id)
            item = xbmcgui.ListItem(title, thumbnailImage = os.path.join(addon_path, 'resources', 'media', 'plus7.png'))
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=True)
        except: continue
    xbmcplugin.endOfDirectory(int(sys.argv[1]))