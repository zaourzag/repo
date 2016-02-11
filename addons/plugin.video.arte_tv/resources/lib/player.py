import urllib2
import json
import sys
import xbmcplugin
import xbmcgui


# CULTURE-TOUCH:        vector=ARTETV
# CONCERT:              vector=ALW
# INFO:                 vector=INFO
# CINEMA:               vector=CINEMA
# CREATIVE:             vector=CREATIVE
# FUTURE:               vector=FUTURE 

# Similiar videos: https://api.arte.tv/api/player/v1/recommendedPostroll/de/000000-000-A

def get_stream_url(api_url, language = 'de', bitrate = 2200):
    try: 
        json_data = urllib2.urlopen(api_url).read()
    except: return -1 # no network
    if bitrate <= 300:
        quality_code = 'MQ'
    elif bitrate <= 800:
        quality_code = 'HQ'
    elif bitrate <= 1500:
        quality_code = 'EQ'
    else: 
        quality_code = 'SQ'
    stream_url = ''
    try:
        video = json.loads(json_data)['videoJsonPlayer']
        video_qualities = video['VSR']
        for quality in video_qualities:
            if video['VSR'][quality]['videoFormat'] != 'HBBTV': continue
            if int(video['VSR'][quality]['versionProg']) != 1: continue
            stream_url = video['VSR'][quality]['url']
            if video['VSR'][quality]['VQU'] == quality_code: break
    except KeyError:
        video = json.loads(json_data)['video']
        if quality_code == 'MQ':
            quality_code = 'HQ' # not available here
        video_qualities = video['VSR']
        for quality in video_qualities:
            if quality['VFO'] != 'HBBTV': continue
            if int(quality['versionProg']) != 1: continue
            stream_url = quality['VUR']
            if quality['VQU'] == quality_code: break
    return stream_url
    
def get_vp_stream_url(api_url, bitrate = 2200):
    try: 
        json_data = urllib2.urlopen(api_url).read()
    except: return -1 # no network
    if bitrate <= 300:
        quality_code = 'MQ'
    elif bitrate <= 800:
        quality_code = 'HQ'
    elif bitrate <= 1500:
        quality_code = 'EQ'
    else: 
        quality_code = 'SQ'
    stream_url = ''
    try:
        video = json.loads(json_data)['videoJsonPlayer']
        video_qualities = video['VSR']
        for quality in video_qualities:
            if video['VSR'][quality]['mediaType'].lower() != 'mp4': continue
            if int(video['VSR'][quality]['versionProg']) != 1: continue
            stream_url = video['VSR'][quality]['url']
            if video['VSR'][quality]['quality'] == quality_code: break
    except: pass
    return stream_url

# vector in {ARTEPLUS7|TVGUIDE|CREATIVE|CINEMA|FUTURE|ALW|INFO|TRACKS|EXTERNAL|PRESSE_D|PRESSE_F|ARTETV|HABILLAGE|OPERA|PRG_ANG|PRG_ESP}
def get_stream_url_by_id(id = '060793-000-A', language = 'de', bitrate = 2200, vector = 'ARTEPLUS7'):
    """
    Requires working ssl module
    """
    api_url = 'https://api.arte.tv/api/player/v1/config/%s/%s?vector=%s' % (language, id, vector)
    return get_vp_stream_url(api_url, bitrate)
    
def get_vp_api_url(url):
    from re import findall
    try:
        html = urllib2.urlopen(url).read()
        regex_api_url = 'arte_vp_url="(.+?)"'
        return findall(regex_api_url, html)[0]
    except:
        return ''
    
def play_video(url):
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=url))