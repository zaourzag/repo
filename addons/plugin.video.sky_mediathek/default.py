# -*- coding: utf-8 -*-
import urllib
import urllib2
import os.path
import re
import xbmcplugin
import xbmcaddon
import xbmcgui

path = os.path.dirname(os.path.realpath(__file__))
icon = os.path.join(path, 'icon.png') 
addon = xbmcaddon.Addon(id='plugin.video.sky_mediathek')
quality = ['360', '720'][int(addon.getSetting('maxVideoQuality'))]

base_url = 'http://www.sky.de'
video_player = '3424888239001'

def clean_text(text):
    return text.replace('&#34;', '"').replace('&amp;', '&').replace('&#39;', "'")
    
def play_video(stream_url):
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=stream_url))
    
def add_video(title, resource, thumb = '', mode = 'play-video', duration_in_seconds = 0, desc = ''):
    link = sys.argv[0] + '?resource=' + urllib.quote_plus(resource) + '&mode=' + mode
    liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    liz.setInfo(type='Video', infoLabels={'Title': title, 'Plot': desc})
    liz.addStreamInfo('video', {'duration': duration_in_seconds})
    liz.setProperty('IsPlayable', 'true')
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=liz)
    
def add_category(title, mode, resource, current_page = 1):
    link = sys.argv[0] + '?mode=' + mode + '&current_page=' + str(current_page) + '&resource=' + resource
    liz = xbmcgui.ListItem(title, iconImage=icon)
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
    
def warning(text, title = 'Sky Mediathek', time = 4500):
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (title, text, time, icon))
    
def get_stream_url(page_url):
    video_id = page_url.split('/')[-1]
    rescue_url = 'http://c.brightcove.com/services/mobile/streaming/index/master.m3u8?videoId=' + video_id
    url = 'http://c.brightcove.com/services/viewer/htmlFederated?playerID=%s&%%40videoPlayer=%s' % (video_player, video_id)
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
        'Referer' : page_url,
        'Connection' : 'keep-alive'
    }
    try:
        req = urllib2.Request(url, None, headers)
        data = urllib2.urlopen(req).read()
        regex_all_video_urls = '"renditions".*?:.*?\[(.+?)\]'
        all_videos = re.findall(regex_all_video_urls, data, re.DOTALL)[0].split('},{')
    except: return rescue_url
    if not all_videos: return rescue_url
    regex_find_stream = '"defaultURL".*?:.*?"(.+?)"'
    try:
        for json_data in all_videos:
            if '"frameHeight":' + quality in json_data:
                return re.findall(regex_find_stream, json_data)[0].replace('https:', 'http:').replace('\\', '')
        stream_url = re.findall(regex_find_stream, all_videos[0])[0].replace('https:', 'http:').replace('\\', '')
        if stream_url.startswith('http') and len(stream_url) > 20: return stream_url
        return rescue_url
    except: return rescue_url

def list_all_videos(page_number = 1, category_id = ''):
    pagination_url = base_url + '/me03pagination.sr?QUERY_TYPE=PLAYLIST_ID&QUERY_VALUE=%s&ANC_LINK=&show_date=true&show_category=false&FIRST_ELEMENT_NUMBER=-1&page=%i' % (category_id, page_number)
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0'}
    try:
        req = urllib2.Request(pagination_url, None, headers)
        html = urllib2.urlopen(req).read()
    except: return False
    regex_all_videos = '<div class="videoPlayer__poster">.*?<img src="(.+?)".*?</span>(.*?)</div>.*?class="airingDate__date">(.+?)<.*?href="(.+?)".*?>(.+?)<'
    all_videos = re.findall(regex_all_videos, html, re.DOTALL)
    for video in all_videos:
        if not 'videoPlayer__lockedCaption' in video[1]:
            thumb = video[0].split('.jpg')[0].replace('https:', 'http:') + '.jpg'
            date = video[2].split(', ')[-1].split('. ')[0] + '.'
            try:
                duration_in_seconds = video[2].split('| ')[-1]
                duration_in_seconds = duration_in_seconds[:duration_in_seconds.find(' ')]
                splitted = duration_in_seconds.split(':')
                duration_in_seconds = int(splitted[0]) * 60 + int(splitted[1])
            except: duration_in_seconds = 0
            url = base_url + video[3]
            if not video[3][-8:-1].isdigit(): continue
            title = clean_text(video[4])
            add_video('%s - %s' % (date, title), url, thumb, 'play-video', duration_in_seconds)
    if ('var lastPage = false;' not in html) or len(all_videos) != 4: return -1 # than is last page
    return True # else not last page

def add_videos(page_number = 1, category = ''):
    for page in range((page_number-1)*3 + 1,page_number*3 + 1):
        return_code = list_all_videos(page, category)
        if not return_code: return warning('Keine Netzwerkverbindung?')
        if return_code == -1:
            # last page reached
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            return True
    add_category(title = '%s (%i)' % ('Nächste Seite', page_number+1), mode = 'list-videos', resource = category, current_page = page_number+1)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return True

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
category = urllib.unquote_plus(params.get('resource', ''))
c_page = urllib.unquote_plus(params.get('current_page', ''))

if mode == 'play-video':
    stream_url = get_stream_url(category)
    play_video(stream_url)
elif mode == 'list-videos':
    add_videos(int(c_page or 1), category)
else:
    add_category('Neue Videos',         'list-videos', '27610441001')
    add_category('1. Bundesliga',       'list-videos', '32548888001')
    add_category('2. Bundesliga',       'list-videos', '32548889001')
    add_category('DFB Pokal',           'list-videos', '30700836001')
    add_category('Premier League',      'list-videos', '33728263001')
    add_category('Champions League',    'list-videos', '33569461001')
    add_category('Europa League',       'list-videos', '37988504001')
    add_category('1. Liga AT',          'list-videos', '29734631001')
    add_category('2. Liga AT',          'list-videos', '29713021001')
    add_category('Formel 1',            'list-videos', '27583543001')
    add_category('Formel E',            'list-videos', '3764627965001')
    add_category('Handball',            'list-videos', '3784218159001')
    add_category('Golf',                'list-videos', '27610440001')
    add_category('Wintersport',         'list-videos', '3261159912001')
    add_category('Beachvolleyball',     'list-videos', '2359637262001')
    add_category('Sport-Dokumentationen', 'list-videos', '3852736962001')
    add_category('Sonstige Videos',     'list-videos', '1711753593001')
    add_category('Kinotrailer',         'list-videos', '1772804035001')
    add_category('DVD Trailer',         'list-videos', '1772804034001')
    add_category('Serien-Highlights',   'list-videos', '1574504486001')
    add_category('Kinopolis',           'list-videos', '1219349353001')
    add_category('Sky Magazin',         'list-videos', '1219349354001')
    add_category('Neu auf Sky',         'list-videos', '1772804032001')
    add_category('Sky90',               'list-videos', '44551452001')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))