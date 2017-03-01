# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import sys
import xbmcplugin
import xbmcaddon
import xbmcgui

def list_search_results(search_string, language, scope = ''):
    search_url = 'http://www.arte.tv/guide/%s/programs?q=%s&scope=%s' % (language, search_string, scope) # scope='plus7'
    try:
        json_data = urllib2.urlopen(search_url).read()
    except: return False
    videos = json.loads(json_data)['programs']
    item_added = False
    for video in videos:
        try: # in rare cases articles appear in video results...
            # views = video['views']
            duration_in_seconds = video['duration']
            id = video['id']
            title = video['title']
            subtitle = video['subtitle']
            if subtitle:
                sep = ' - '
            else:
                sep = ''
                subtitle = ''
            thumb = video['thumbnail_url'].replace('https:', 'http:')
            desc = video['description']
            year = video['year']
            try:
                directors = video['person']['director']
                if len(directors) == 0: director = ''
                elif len(directors) == 1: director = directors[0]
                else:
                    director = ''
                    for drt in directors:
                        director += drt + ', '
                    director = director[:-2]
            except: director = ''
            try:
                countries = video['countries']
                if len(countries) == 0: country = ''
                elif len(countries) == 1: country = countries[0]
                else:
                    country = ''
                    for cnty in countries:
                        country += cnty + ', '
                    country = country[:-2]
            except: country = ''
            cast_and_role = []
            try:
                cast = video['person']['casting']
                for entry in cast:
                    cast_and_role.append((entry['name'], entry['character_name']))
            except: pass
            link = sys.argv[0] + '?id=' + urllib.quote_plus(id) + '&mode=play-video'
            item = xbmcgui.ListItem('[B]%s[/B]%s%s' % (title, sep, subtitle), iconImage='', thumbnailImage=thumb)
            item.setInfo(type='Video', infoLabels={
                'Title'             : '%s%s%s' % (title, sep, subtitle), 
                'Plot'              : desc,
                'Year'              : year, 
                'Director'          : director, 
                'CastAndRole'       : cast_and_role,
                'Country'           : country,
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