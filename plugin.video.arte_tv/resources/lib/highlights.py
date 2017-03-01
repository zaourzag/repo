import urllib
import urllib2
import re
import json
import sys
import xbmcplugin
import xbmcaddon
import xbmcgui
from resources.lib.functions import translate

def add_folder(title, thumb, mode, site = '', desc = '', fanart = '', icon = ''):
    link = '%s?mode=%s&site=%s' % (sys.argv[0], mode, site)
    item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    item.setProperty('fanart_image', fanart or thumb)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=True)

def list_index():
    import xbmc
    import os.path
    addon_path = xbmc.translatePath(xbmcaddon.Addon('plugin.video.arte_tv').getAddonInfo('path')).decode('utf-8')
    add_folder(translate(30006), os.path.join(addon_path, 'resources', 'media', 'plus7.png'), 'highlights', 'recommended')
    #add_folder(translate(30013), os.path.join(addon_path, 'resources', 'media', 'plus7.png') , 'highlights', 'tv')
    add_folder('ARTE INFO', os.path.join(addon_path, 'resources', 'media', 'info.png'), 'highlights', 'info')
    add_folder('ARTE FUTURE', os.path.join(addon_path, 'resources', 'media', 'future.png'), 'highlights', 'future')
    add_folder('ARTE CREATIVE', os.path.join(addon_path, 'resources', 'media', 'creative.png'), 'highlights', 'creative')
    add_folder('ARTE CONCERT', os.path.join(addon_path, 'resources', 'media', 'concert.png'), 'highlights', 'concert')
    add_folder('ARTE CINEMA', os.path.join(addon_path, 'resources', 'media', 'cinema.png'), 'highlights', 'cinema')
    #add_folder('CULTURE TOUCH', os.path.join(addon_path, 'resources', 'media', 'ctouch.jpg'), 'highlights', 'ctouch')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def list_highlight_videos(api_url, language, vector, max_height, icon = ''):
    api_url = api_url % language
    json_data = urllib2.urlopen(api_url).read()
    videos = json.loads(json_data)['videos']
    item_added = False
    for video in videos:
        try:
            thumb = video['VTU'].replace('https:', 'http:')
            title = video['VTI']
            try: desc = video['VDE']
            except: desc = ''
            #date = datetime.strptime(video['VDA'][:-6], '%d/%m/%Y %H:%M:%S').strftime('%d.%m.%Y')
            duration_in_seconds = video['VDU']
            try: category = video['category']
            except: category = ''
            if 216 < max_height <= 406:
                stream_urls = video['VSR']
                stream_url = ''
                for url in stream_urls:
                    try:
                        stream_url = video['VSR'][url]['url']
                        if video['VSR'][url]['versionShortLibelle'].lower() == language:
                            break # language found
                    except: continue
                link = stream_url
            else:
                id = video['VID']
                id = id if id.count('-') == 2 else id + '-A'
                link = '%s?mode=play-video&id=%s&vector=%s' % (sys.argv[0], urllib.quote_plus(id), urllib.quote_plus(vector))
            item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
            item.setInfo(type='Video', infoLabels={
                'Title'             : title, 
                'Plot'              : desc, 
                'Genre'             : category,
                }
            )
            item.addStreamInfo('video', {'duration' : duration_in_seconds})
            item.addStreamInfo('audio', {'language' : language})
            item.setProperty('IsPlayable', 'true')
            item.setProperty('fanart_image', thumb)
            if xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item): item_added = True
        except: continue
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return item_added