import urllib
import urllib2
import json
import sys
import xbmcgui
import xbmcplugin

def list_recommended_videos(id = 'XXXXXX-000-A', language = 'de'):
    try:
        api_url = 'https://api.arte.tv/api/player/v1/recommendedPostroll/%s/%s' % (language, id)
        try: 
            json_data = urllib2.urlopen(api_url).read()
            video_list = json.loads(json_data)['videoList']
        except: return -1 # no network
        for video in video_list:
            video_player_url = video['videoPlayerUrl']
            title = video['VTI']
            thumb = video['VTU']['IUR'].replace('https:', 'http:')
            link = sys.argv[0] + '?stream=' + urllib.quote_plus(video_player_url) + '&mode=play-video'
            item = xbmcgui.ListItem('[B]%s[/B]' % title, thumbnailImage=thumb)
            item.setInfo(type='Video', infoLabels={
                'Title'             : title
                }
            )
            item.addStreamInfo('audio', {'language' : language})
            item.setProperty('IsPlayable', 'true')
            item.setProperty('fanart_image', thumb)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    except: return False