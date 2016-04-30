# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import json
import os.path
import xbmcplugin
import xbmcaddon
import xbmcgui

path = os.path.dirname(os.path.realpath(__file__))
icon = os.path.join(path, "icon.png")
addonID = 'plugin.video.kicker_tv'
addon = xbmcaddon.Addon(id=addonID)
quality = ['low', 'medium', 'high', 'hd'][int(addon.getSetting("videoQuality"))]

def index():
    add_category('Neueste Videos', 'list-videos')
    add_category(title = 'Deutscher Fussball', mode = 'list-videos', current_page = 0, keyword = 'dt%2E%20fussball', thumb = '')
    add_category(title = 'Internationaler Fussball', mode = 'list-videos', current_page = 0, keyword = 'int%2E%20fussball', thumb = '')
    add_category(title = 'WM', mode = 'list-videos', current_page = 0, keyword = 'wm', thumb = '')
    add_category(title = 'Regionalliga Bayern', mode = 'list-videos', current_page = 0, keyword = 'rl%20bayern', thumb = '')
    add_category(title = 'Frauenfussball', mode = 'list-videos', current_page = 0, keyword = 'frauen-fussball', thumb = '')
    add_category(title = 'Formel 1', mode = 'list-videos', current_page = 0, keyword = 'formel%201', thumb = '')
    add_category(title = 'Mehr Sport', mode = 'list-videos', current_page = 0, keyword = 'mehr%20sport', thumb = '')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def list_videos(category = '', current_page = 0):
    try:
        factor = 16
        url = 'http://www.kicker.de/news/video/ajax.ashx?ajaxtype=videoitems&vidcat=%s&sid=-1&vid=0&index=%i' % (category, current_page * factor)
        json_data = urllib2.urlopen(url).read()
        video_items = json.loads(json_data, encoding="cp1252")
        counter = 0
        max = factor
        if not video_items: return -1
        if len(video_items) < max:
            max = len(video_items)
        item_added = False
        for item in video_items:
            try:
                counter += 1
                if counter > max: break
                thumb = item['img']
                title = item['title'].replace("\\'", "'")
                video_id = item['id']
                if add_video(title, str(video_id), thumb, 'play-video'): item_added = True
            except:
                counter += 1
                continue
        if len(video_items) % 16 == 0:
            add_category('Nächste Seite (%i)' % (current_page + 2), 'list-videos', current_page + 1, category)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        return item_added
    except: return False
    
def add_video(title, id, thumb, mode):
    link = sys.argv[0] + "?id=" + id + "&mode=" + mode
    liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    liz.setInfo(type="Video", infoLabels={"Title": title})
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=liz, isFolder=True)
    
def add_category(title, mode, current_page = 0, keyword = '', thumb = ''):
    link = sys.argv[0] + "?mode=" + mode + "&page=%i" % current_page + "&keyword=" + urllib.quote_plus(keyword)
    liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    liz.setInfo(type="Video", infoLabels={"Title": title})
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=liz, isFolder=True)
    
def warning(text, title = 'Kicker.tv', time = 4500):
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (title, text, time, icon))
    
def play_video(video_id):
    try:
        url = 'http://www.kicker.de/player/v2/video.xml?id=' + video_id
        html = urllib2.urlopen(url).read()
        regex_video_info = '<headline>(.+?)</headline>.*?<teaser>(.+?)</teaser>.*?<date>(.+?)</date>.*?<thumb>(.+?)</thumb>.*?<videoUrl.*?>(.+?)</'
        video_info = re.findall(regex_video_info, html, re.DOTALL)[0]
        title = video_info[0]
        desc = video_info[1].replace('<![CDATA[', '').replace(']]>', '')
        date = video_info[2]
        thumb = video_info[3]
        stream_url = video_info[4].replace('_low.', '_%s.' % quality)
        liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
        liz.setInfo(type="Video", infoLabels={"Title": title, "Plot" : date + '\n' + desc})
        xbmc.Player().play(stream_url, liz)
        return True
    except: return False
 
def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict
 
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
vid = urllib.unquote_plus(params.get('id', ''))
page = urllib.unquote_plus(params.get('page', ''))
keyword = urllib.unquote_plus(params.get('keyword', ''))

if mode == 'play-video':
    if not play_video(vid): warning('Das Video konnte nicht abgespielt werden!')
elif mode == 'list-videos':
    ret = list_videos(keyword, int(page))
    if ret == -1: warning('Letzte Seite!')
    elif not ret: warning('Es konnten keine Videos aufgelistet werden!')
else: index()
