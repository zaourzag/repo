# -*- coding: utf-8 -*-
import urllib2
import json
import sys
#import xbmcplugin
#import xbmcgui
#import xbmc
#import xbmcaddon
import os.path
    
language = ('de', 'fr', 'en', 'es')[-2]

"""
WIP
"""

def list_all_channels(language = 'de'):
    api_url = 'http://arte.tv/guide/%s/programs' % language
    #try:
    json_data = urllib2.urlopen(api_url).read()
    video_channels = json.loads(json_data)['facets']['categories']
    #except: return False
    #addon_path = xbmc.translatePath(xbmcaddon.Addon('plugin.video.arte_tv').getAddonInfo('path')).decode('utf-8')
    for channel in video_channels:
        #try:
        print(channel['value'])
        #channel_id = channel['channelID']
        #title = channel['germanLabel'] if language == 'de' else channel['frenchLabel']
        #link = '%s?mode=list-videos&category=%s' % (sys.argv[0], channel_id)
        #item = xbmcgui.ListItem(title, thumbnailImage = os.path.join(addon_path, 'resources', 'media', 'plus7.png'))
        #xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=True)
        #except: continue
    #xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
def list_all_videos(language):
    """http://www.arte.tv/guide/en/plus7/videos?category=ACT&page=1&limit=24&sort=newest"""
    api_url = 'http://arte.tv/guide/%s/programs?page=1&limit=20' % language
    json_data = urllib2.urlopen(api_url).read()
    videos = json.loads(json_data)['programs']
    print(len(videos))
    for video in videos:
        title = video['title']
        subtitle = video['subtitle']
        print(title, subtitle)