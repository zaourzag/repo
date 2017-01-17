import urllib2
import json
import sys
import xbmcgui
import xbmcplugin
import xbmc
from resources.lib.functions import translate

def play_livestream(language = 'de'):
    try:
        api_url = 'http://www.arte.tv/papi/tvguide/videos/livestream/player/%s/' % language[0].upper()
        try: 
            json_data = urllib2.urlopen(api_url).read()
            stream_data = json.loads(json_data)['videoJsonPlayer']
        except: return -1 # no network
        title = stream_data['VTI']
        try:
            subtitle = stream_data['VSU']
        except:
            subtitle = ''
        if subtitle:
            sep = ' - '
        else:
            subtitle = sep = ''
        try:
            desc = stream_data['VDE']
        except:
            desc = ''
        thumb = stream_data['VTU']['IUR']
        try:
            duration_in_seconds = stream_data['BDS']
        except:
            duration_in_seconds = 0
        stream_url = stream_data['VSR']['M3U8_HQ']['url']
        try:
            player_url = stream_data['videoPlayerUrl'] # for playing video from beginning if wished
        except:
            player_url = ''
        bitrate = stream_data['VSR']['M3U8_HQ']['bitrate']
        height = stream_data['VSR']['M3U8_HQ']['height']
        width = stream_data['VSR']['M3U8_HQ']['width']
        item = xbmcgui.ListItem('[B][COLOR fffa481c]LIVE[/COLOR] %s[/B]%s%s' % (title, sep, subtitle), thumbnailImage=thumb)
        item.setInfo(type='Video', infoLabels={
            'Title'             : '%s%s%s' % (title, sep, subtitle), 
            'Plot'              : desc,
            }
        )
        item.addStreamInfo('video', {
            'duration'  : duration_in_seconds,
            'aspect'    : float(width) / height,
            'width'     : width,
            'height'    : height,
            }
        )
        item.addStreamInfo('audio', {'language' : language})
        item.setProperty('IsPlayable', 'true')
        item.setProperty('fanart_image', thumb)
        if player_url: # add option 'Play from beginning' to context menu
            import urllib
            item.addContextMenuItems(
                [(translate(30014), 'xbmc.RunPlugin(plugin://plugin.video.arte_tv/?mode=play-video&stream=%s&title=%s&thumb=%s)' 
                    % (player_url, urllib.quote_plus(title.encode('utf8')), urllib.quote_plus(thumb.encode('utf8'))))
                ]
            )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=stream_url, listitem=item)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        return True
    except: return False