# -*- coding: utf-8 -*-
import sys
import urllib
import urllib2
import json
import re
import xbmcplugin
import xbmcgui
import os.path

URI = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])
PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THUMBNAIL_PATH = os.path.join(PATH, 'media')

def list_matchdays(league='1'):
    json_url = 'http://sportdaten.bild.de/sportdaten/widgets/rpc_competition-info/%sbl/' % (league if league == '2' else '')
    try:
        json_data = urllib2.urlopen(json_url).read()
        info = json.loads(json_data)
    except: return
    season_id = info['season_id']
    round_id = info['round_id']
    matchdays_until_today = info['matchday']
    from resources.lib.index import add_dir, ADDON_HANDLE
    for matchday in range(matchdays_until_today, 0, -1):
        add_dir('%i. Spieltag' % matchday, 'bundesliga.jpg', {'lib':'bundesliga','function':'list_matchday','arg':'%i-%i-%i'%(matchday,season_id,round_id)})
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    
def list_matchday(arg):
    try:
        matchday, season_id, round_id = arg.split('-')
        ajax_url = 'http://sportdaten.bild.de/sportdaten/widgets/rpc_dmm_widget-gameplan-bibuli/sp1/se%s/ro%s/md%s/' % (season_id, round_id, matchday)
        matchday_data = urllib2.urlopen(ajax_url).read()
    except: return
    import xbmcaddon
    addon = xbmcaddon.Addon(id='plugin.video.bild_bundesliga')
    SHOW_RESULT = addon.getSetting('showMatchResult') == 'true'
    regex_all_matches = '<tr class="event (?:odd|even) finished".*?title="(.*?)".*?title="(.*?)".*?match_result_ats.*?href="(.+?)".*?<span class="finished">(.*?)<'
    matches = re.findall(regex_all_matches, matchday_data)
    thumb = os.path.join(THUMBNAIL_PATH, 'bundesliga.jpg')
    if not matches:
        regex_all_matches = '<tr class="event (?:odd|even)".*?title="(.*?)".*?title="(.*?)".*?match_result_ats">(.+?)<'
        matches = re.findall(regex_all_matches, matchday_data)
        for match in matches:
            team_home = match[0]
            team_away = match[1]
            date = match[2].replace('  ', ' ').replace(' Uhr', '')
            title = '%s %s - %s' % (date, team_home, team_away)
            liz = xbmcgui.ListItem(title, thumbnailImage=thumb)
            liz.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url='', listitem=liz)
    else:
        for match in matches:
            team_home = match[0]
            team_away = match[1]
            url = match[2]
            if SHOW_RESULT:
                result = match[3]
                title = '%s - %s %s' % (team_home, team_away, result)
            else:
                title = '%s - %s' % (team_home, team_away)
            link = URI + '?lib=bundesliga&function=play&arg=' + urllib.quote(url)
            liz = xbmcgui.ListItem(title, thumbnailImage=thumb)
            liz.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=link, listitem=liz)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def get_stream_url(url):
    url = urllib.unquote(url)
    html = urllib2.urlopen(url).read()
    regex_json_url = 'data-video\s*?=\s*?"(.+?)"'
    try: 
        json_url = re.search(regex_json_url, html, re.DOTALL).group(1)
        if 'bild-plus' in json_url: return
        json_url = 'http://bild.de%s,view=json,width=400.bild.html' % json_url.split(',')[0]
        json_data = urllib2.urlopen(json_url).read()
        video = json.loads(json_data)
        streams = video['clipList']
        for stream in streams:
            for src in stream['srces']:
                if src.get('src').endswith('.m3u8'):
                    return src.get('src')
    except: return ''

def play(arg):
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, xbmcgui.ListItem(path=get_stream_url(arg)))