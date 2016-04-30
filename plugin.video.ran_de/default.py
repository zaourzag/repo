# -*- coding: utf-8 -*-
import urllib
import urllib2
import os.path
import re
import json
import datetime
import time
import xbmcplugin
import xbmcaddon
import xbmcgui

path = os.path.dirname(os.path.realpath(__file__))
icon = os.path.join(path, 'icon.png')
addon = xbmcaddon.Addon(id='plugin.video.ran_de')
try:
    height = [270, 396, 480, 540, 720][int(addon.getSetting('maxVideoQuality'))]
except:
    height = 540

# http://www.ran.de/static/ran-app/configuration.json
ran_api_base = 'http://contentapi.sim-technik.de'

def play_video(resource = '/ran-app/v1/*.json', height = 720):
    try:
        json_url = ran_api_base + resource
        html = urllib2.urlopen(json_url).read()
        video_info = json.loads(html)
        if video_info['type'] == 'livestream':
            url = video_info['stream_url']
            url = get_playlist_url(url, height)
        elif video_info['type'] == 'video':
            id = str(video_info['video_id'])
            url = get_stream_url(id, height)
        else: return False
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=url))
        return True
    except: return False
    
def get_playlist_url(m3u8_url, height = 720):
    try:
        resolutions = urllib2.urlopen(m3u8_url).read().split('#')
        stream_url_prefix = m3u8_url[:m3u8_url.rfind('/')+1]
        stream_url_suffix = ''
        max_height = 0
        pattern = 'RESOLUTION=\d+x(\d+),.*?\n(.+?)\n'
        for resolution in resolutions:
            try:
                if not resolution.endswith('\n'):
                    resolution += '\n'
                if 'RESOLUTION' in resolution:
                    result = re.findall(pattern, resolution)[0]
                    available_height = int(result[0])
                    if max_height < available_height <= height:
                        max_height = available_height
                        stream_url_suffix = result[1]
            except: continue
        stream_url = stream_url_prefix + stream_url_suffix
        stream_url = stream_url.replace('\r', '').replace(' ', '')
        if stream_url.startswith('http') and stream_url.endswith('m3u8'): return stream_url
        return m3u8_url           
    except: return m3u8_url

def list_videos(resource = '/ran-app/v1/videos.json'):
    try:
        json_url = ran_api_base + resource
        html = urllib2.urlopen(json_url).read()
        videos = json.loads(html)['contents']
        item_added = False
        for video in videos:
            try:
                playable = 'false'
                if video['type'] == 'video':
                    duration_in_seconds = video['duration_in_seconds']
                    date = datetime.datetime.fromtimestamp(video['published']).strftime('%d.%m.%Y')
                    playable = 'true'
                elif video['type'] == 'livestream':
                    stream_date_start = video['streamdate_start']
                    stream_date_ende = video['streamdate_end']
                    duration_in_seconds = stream_date_ende - stream_date_start
                    date = datetime.datetime.fromtimestamp(stream_date_start).strftime('%d.%m.%Y, %H:%M')
                    timestamp_now = time.time()
                    if stream_date_ende >= timestamp_now:
                        if stream_date_start <= timestamp_now: 
                            date = '[COLOR red]%s[/COLOR]' % translation(30104).upper()
                            duration_in_seconds = stream_date_ende - timestamp_now
                            playable = 'true'
                    else: continue
                resource = video['resource']
                title = video['teaser']['title']
                thumb = video['teaser']['image'].replace('ran_app_1280x720', 'ran_app_512x288')
                desc = video['teaser']['image_alt']
                link = sys.argv[0] + '?resource=' + urllib.quote_plus(resource) + '&mode=play-video'
                item = xbmcgui.ListItem('%s - %s' % (date, title), iconImage=icon, thumbnailImage=thumb)
                item.setInfo(type='Video', infoLabels={'Title' : title, 'Plot' : desc})
                item.addStreamInfo('video', {'duration': duration_in_seconds})
                item.setProperty('IsPlayable', playable)
                if xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item): item_added = True
            except: continue
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        return item_added
    except: return False

def get_stream_url(clip_id = '', height = 720):
    """
    Returns streaming url of given clip id in requested or lower quality
    Height values: 270, 360, 480, 540, 720
    Stream id: (default: 06)
    12: 1280x720@2.7mbps, 11: 1280x720@2mbps, 10: 960x540@1.7mbps, 09: 960x540@1.4mbps; if 12 than 11 and 10 and 09 and not 08/07
    08: 768x432@1.8mbps,  07: 768x432@1.5mbps; if 08 than 07 and not 12/11/10/09
    06: 640x360@1.1mbps,  05: 640x360@0.6mbps, 04: 480x270@0.4mbps; 06,05,...,01 always available
    03: 416x258@0.2mbps,  02: Audio only, 01: Audio only
    """
    if height == 360: return 'http://ws.vtc.sim-technik.de/video/video.php?clipid=' + clip_id
    url = 'http://vas.sim-technik.de/video/video.jsonp?clipid=' + clip_id
    try: 
        json = urllib2.urlopen(url).read() 
        regex_parse_url = '"VideoURL":"(.+?)",'   
        stream_url = re.findall(regex_parse_url, json, re.DOTALL)[0]
    except: return False
    stream_url = stream_url.replace('\\', '').split('&ts')[0]
    if height <= 270: return stream_url.replace('06.mp4', '04.mp4')
    def is_video_quality_available(quality = '12'):
        try:
            stream_url_high = stream_url.replace('06.mp4', quality + '.mp4')
            req = urllib2.Request(stream_url_high)
            urllib2.urlopen(req)
            return stream_url_high
        except: return False
    if height <= 480:
        available = is_video_quality_available('08')
        if available: return available
        return stream_url
    if height >= 720:
        available = is_video_quality_available('12')
        if available: return available
        available = is_video_quality_available('08')
        if available: return available
        return stream_url
    available = is_video_quality_available('10')
    if available: return available
    available = is_video_quality_available('08')
    if available: return available
    return stream_url

def add_category(title, mode, resource, thumb = ''):
    link = sys.argv[0] + '?mode=' + mode + '&resource=' + urllib.quote_plus(resource)
    liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=liz, isFolder=True)
 
def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split('&')
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict
    
def warning(text, title = 'ran', time = 4500):
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (title, text, time, icon))

def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')
    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
resource = urllib.unquote_plus(params.get('resource', ''))

if mode == 'play-video':
    if not play_video(resource, height): warning(translation(30102))
elif mode == 'list-videos':
    if not list_videos(resource): warning(translation(30103))
else:
    add_category(translation(30105), 'list-videos', '/ran-app/v1/livestreams.json')
    add_category(translation(30106), 'list-videos', '/ran-app/v1/videos.json')
    add_category(translation(30107), 'list-videos', '/ran-app/v1/videos/fussball.json')
    add_category(translation(30108), 'list-videos', '/ran-app/v1/videos/tennis.json')
    add_category(translation(30109), 'list-videos', '/ran-app/v1/videos/us-sport.json')
    add_category(translation(30110), 'list-videos', '/ran-app/v1/videos/boxen.json')
    add_category(translation(30111), 'list-videos', '/ran-app/v1/videos/golf.json')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))