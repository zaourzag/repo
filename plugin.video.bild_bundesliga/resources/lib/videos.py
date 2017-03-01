# -*- coding: utf-8 -*-
import sys
import urllib
import urllib2
import json
import re
import xbmcgui
import xbmcplugin

URI = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])

def list_videos(arg):
    page_id, page_number, last_page = arg.split('--')
    ajax_url = 'http://www.bild.de/video/clip/%s,page=%s,view=ajax.bild.html' % (page_id, page_number)
    try: ajax_data = urllib2.urlopen(ajax_url).read()
    except: return
    regex_all_videos = '<div\s+?class\s*?=\s*?"hentry.*?<meta\s*?itemprop\s*?=\s*?"url"\s*?content\s*?=\s*?"(.+?)".*?<meta\s*?itemprop\s*?=\s*?"datePublished"\s*?content\s*?=\s*?"(.+?)".*?<meta\s*?itemprop\s*?=\s*?"name"\s*?content\s*?=\s*?"(.+?)".*?<meta\s*?itemprop\s*?=\s*?"description"\s*?content\s*?=\s*?"(.+?)".*?<meta\s*?itemprop\s*?=\s*?"duration"\s*?content\s*?=\s*?"(.+?)".*?<meta\s*?itemprop\s*?=\s*?"thumbnailUrl"\s*?content\s*?=\s*?"(.+?)".*?</div>'
    videos = re.findall(regex_all_videos, ajax_data, re.DOTALL)
    for video in videos:
        ajax_url = video[0]
        date = '%s.%s.%s' % (video[1][8:10], video[1][5:7], video[1][:4])
        title = video[2].replace('&#039;', "'").replace('&#034;', '"').replace('&amp;', '&')
        desc = video[3].replace('&#039;', "'").replace('&#034;', '"').replace('&amp;', '&')
        duration = video[4]
        duration_in_seconds = 0
        try:
            # Assuming video length < 60min <==> duration begins with 'T0H'
            if duration[4] == 'M':      # Minutes <= 9
                duration_in_seconds += 60 * int(duration[3])
                if duration[6] == 'S':  # Seconds <= 9
                    duration_in_seconds += int(duration[5])
                else:                   # Seconds >= 10, duration[7] = 'S'
                    duration_in_seconds += int(duration[5:7])
            else:                       # Minutes >= 10, duration[5] = 'M'
                duration_in_seconds += 60 * int(duration[3:5])
                if duration[7] == 'S':  # Seconds <= 9
                    duration_in_seconds += int(duration[6])
                else:                   # Seconds >= 10, duration[8] = 'S'
                    duration_in_seconds += int(duration[6:8])
        except: pass
        thumb = video[5]
        link = '%s?%s' % (URI, urllib.urlencode({'lib':'videos', 'function':'play', 'arg':ajax_url}))
        item = xbmcgui.ListItem('%s %s' % (date, title), thumbnailImage=thumb)
        item.setInfo(type='Video', infoLabels={'Title' : title, 'Plot' : desc})
        item.addStreamInfo('video', {'duration': duration_in_seconds})
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=link, listitem=item)
    if page_number < last_page:
        arg = '%s--%i--%s' % (page_id, int(page_number)+1, last_page)
        args = {'lib':'videos', 'function':'list_videos', 'arg':arg}
        link = '%s?%s' % (URI, urllib.urlencode(args))
        item = xbmcgui.ListItem('[B]Nächste Seite (%i)[/B]' % (int(page_number)+2))
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=link, listitem=item, isFolder=True)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def get_stream_url(ajax_url):
    try:
        ajax_url = urllib.unquote(ajax_url)
        json_url = ajax_url.rpartition('.bild.html')[0] + ',height=400,view=json.bild.html'
        json_data = urllib2.urlopen(json_url).read()
        video = json.loads(json_data)
        streams = video['clipList']
        for stream in streams:
            for src in stream['srces']:
                if src.get('src'):
                    return src.get('src')
    except: pass
    return ''
    
def play(arg):
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, xbmcgui.ListItem(path=get_stream_url(arg)))