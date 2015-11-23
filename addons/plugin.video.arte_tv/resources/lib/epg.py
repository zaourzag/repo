# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import sys
import xbmcplugin
import xbmcgui
from resources.lib.functions import translate

def add_folder(title, thumb, mode, site = '', desc = '', fanart = '', icon = ''):
    link = '%s?%s' % (sys.argv[0], mode)
    item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    item.setProperty('fanart_image', fanart or thumb)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=True)

def list_tv_dates(language = 'de'):
    import xbmc
    import xbmcaddon
    import os.path
    import datetime
    
    addon_path = xbmc.translatePath(xbmcaddon.Addon('plugin.video.arte_tv').getAddonInfo('path')).decode('utf-8')
    weekdays = (translate(30020), translate(30021), translate(30022), translate(30023), translate(30024), translate(30025), translate(30026))
    
    date = datetime.datetime.now()
    today = date 
    yesterday = date + datetime.timedelta(days=-1)
    tomorrow = date + datetime.timedelta(days=1)
    add_folder(translate(30027), os.path.join(addon_path, 'resources', 'media', 'plus7.png'), 'mode=list-tv-guide&date=' + yesterday.strftime('%Y-%m-%d'))
    add_folder(translate(30028), os.path.join(addon_path, 'resources', 'media', 'plus7.png'), 'mode=list-tv-guide&date=' + today.strftime('%Y-%m-%d'))
    add_folder(translate(30029), os.path.join(addon_path, 'resources', 'media', 'plus7.png'), 'mode=list-tv-guide&date=' + tomorrow.strftime('%Y-%m-%d'))
    date += datetime.timedelta(days=1)
    for day in range(20):
        date += datetime.timedelta(days=1)
        weekday = weekdays[date.weekday()]
        add_folder('%s, %s' % (weekday, date.strftime('%d.%m.')), os.path.join(addon_path, 'resources', 'media', 'plus7.png'), 'mode=list-tv-guide&date=' + date.strftime('%Y-%m-%d'))
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

# list_tv_guide('de', 'L2', '2015-12-03')
# http://www.arte.tv/papi/tvguide/epg/schedule/D/L2/2015-11-12/2015-11-12/0.json
# http://www.arte.tv/papi/tvguide/epg/schedule/D/L2/2015-11-12/2015-11-12/1.json
# http://www.arte.tv/papi/tvguide/epg/programs/D/L2.json?endDate=2015-11-12&startDate=2015-11-12
# (end_date - start_date) in {0,1,2,...,7}
def list_tv_guide(
        language        = 'de',
        detail_level    = 'L3',
        start_date      = '2015-07-30',
        end_date        = ''
    ):
    url = 'http://www.arte.tv/papi/tvguide/epg/schedule/%s/%s/%s/%s/0.json' % (language[0].upper(), detail_level, start_date, end_date or start_date)
    try: 
        json_data = urllib2.urlopen(url).read()
        videos = json.loads(json_data)['abstractBroadcastList']
    except: return -1 # no network
    lang = language[0].upper()
    item_added = False
    for video in videos:
        try:
            title = video['TIT']
            try: thumb = video['IMG']['IUR']
            except: thumb = ''
            try: rating = video['mediaRating' + lang]
            except: rating = 0
            start_time = video['BAT']
            try:
                video_player_url = video['VDO']['videoPlayerUrl']
                duration_in_seconds = video['VDO']['videoDurationSeconds']
                playable = 'true'
            except:
                video_player_url = ''
                duration_in_seconds = 0
                playable = 'false'
            try: 
                subtitle = video['STL']
                sep = ' - '
            except: 
                subtitle = sep = ''
            try: genre = video['GEN']
            except: genre = ''
            try: year = video['VDO']['productionYear']
            except: year = 0
            try: desc = video['DLO'].replace(' '*6, '')
            except: 
                try: desc = video['DTE']
                except: desc = ''
            try: director = video['VDO']['director']
            except: director = ''
            cast_and_role = []
            try:
                cast = video['CCW']
                for entry in cast:
                    try:
                        cast_and_role.append((entry['CNA'], entry['CRO']))
                    except:
                        try:
                            cast_and_role.append((entry['CNA'], entry['CTY']))
                        except: pass
            except: pass
            try: short_desc = video['VDO']['V7T']
            except: short_desc = ''
            try: studio = video['POR']
            except: studio = ''
            try: country = video['PCT']
            except: country = ''
            try:
                if video['CGE'] == 'FIL':
                    featured_color = 'fffa805a'
                else:
                    try:
                        if video['FEA']:
                            featured_color = 'fffa805a'
                        else: featured_color = ''
                    except: featured_color = ''
            except: featured = ''
            link = sys.argv[0] + '?stream=' + urllib.quote_plus(video_player_url) + '&mode=play-video'
            item = xbmcgui.ListItem('[B][COLOR fffa481c]%s [/COLOR][COLOR %s]%s[/B]%s%s[/COLOR]' % (start_time, featured_color, title, sep, subtitle), iconImage='', thumbnailImage=thumb)
            item.setInfo(type='Video', infoLabels={
                'Title'             : '%s%s%s' % (title, sep, subtitle), 
                'Plot'              : desc,
                'PlotOutline'       : short_desc,
                'Mpaa'              : rating, 
                'Genre'             : genre, 
                'Year'              : year, 
                'Director'          : director, 
                'CastAndRole'       : cast_and_role,
                'Studio'            : studio, 
                'Country'           : country,
                }
            )
            item.addStreamInfo('video', {'duration' : duration_in_seconds})
            item.addStreamInfo('audio', {'language' : language})
            item.setProperty('IsPlayable', playable)
            item.setProperty('fanart_image', thumb)
            if xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item): item_added = True
        except: continue
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return item_added