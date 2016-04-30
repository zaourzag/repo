# -*- coding: utf-8 -*-
import urllib
import urllib2
import sys
import xbmcplugin
import xbmcgui

def list_concert_index(language):
    from resources.lib.index import add_folder
    import os.path, xbmc, xbmcaddon
    addon_path = xbmc.translatePath(xbmcaddon.Addon('plugin.video.arte_tv').getAddonInfo('path')).decode('utf-8')
    concert_image = os.path.join(addon_path, 'resources', 'media', 'concert.png')
    if language == 'fr':
        add_folder('Les plus récentes', concert_image, 'mode=list-concert-videos&site=/fr/videos/all')
        add_folder('Dernière chance', concert_image, 'mode=list-concert-videos&site=/fr/videos/all&sort=lastchance')
        add_folder('Rock/Pop', concert_image, 'mode=list-concert-videos&site=/fr/videos/rockpop')
        add_folder('Musique classique', concert_image, 'mode=list-concert-videos&site=/fr/videos/musique-classique')
        add_folder('Jazz', concert_image, 'mode=list-concert-videos&site=/fr/videos/jazz')
        add_folder('Musiques du monde', concert_image, 'mode=list-concert-videos&site=/fr/videos/musiques-du-monde')
        add_folder('Danse', concert_image, 'mode=list-concert-videos&site=/fr/videos/danse')
        add_folder('Collections', concert_image, 'mode=concert&site=events')
        add_folder('Partenaires', concert_image, 'mode=concert&site=partners')
        add_folder('Recherche', concert_image, 'mode=concert-search')
    else:
        add_folder('Neueste', concert_image, 'mode=list-concert-videos&site=/de/videos/all')
        add_folder('Letzte Chance', concert_image, 'mode=list-concert-videos&site=/de/videos/all&sort=lastchance')
        add_folder('Rock/Pop', concert_image, 'mode=list-concert-videos&site=/de/videos/rockpop')
        add_folder('Klassik', concert_image, 'mode=list-concert-videos&site=/de/videos/klassische-musik')
        add_folder('Jazz', concert_image, 'mode=list-concert-videos&site=/de/videos/jazz')
        add_folder('Weltmusik', concert_image, 'mode=list-concert-videos&site=/de/videos/weltmusik')
        add_folder('Tanz', concert_image, 'mode=list-concert-videos&site=/de/videos/tanz')
        add_folder('Events', concert_image, 'mode=concert&site=events')
        add_folder('Partnerseiten', concert_image, 'mode=concert&site=partners')
        add_folder('Suche', concert_image, 'mode=concert-search')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def concert_search(language, search_string='rone', page=0, sort='latest'):
    url = '/%s/search/site/%s' % (language, search_string)
    list_concert_videos(language, url, page, sort=sort)

def list_collections(language='de', type='events', page=0, sort='latest'):  # type in {events, partners}
    import re
    url = 'http://concert.arte.tv/%s/videos/all' % language
    try:
        html = urllib2.urlopen(url).read()
    except:
        return -1
    regex_collection = '<div class="liste-content content-down" id="%s">(.+?)</div>' % type
    try:
        collection = re.findall(regex_collection, html, re.DOTALL)[0]
    except:
        return -2
    regex_all_events = '<li>.*?<a href="(.+?)">.*?src="(.+?)".*?<span>(.+?)</span>.*?</li>'
    events = re.findall(regex_all_events, collection, re.DOTALL)
    item_added = False
    for event in events:
        url = event[0]
        thumb = event[1].replace('https:', 'http:')
        if type == 'events':
            fanart = thumb.replace('/styles/alw_square_30_full/public', '').replace('/styles/alw_square_30/public', '')
            thumb = thumb.replace('alw_square_30_full', 'alw_rectangle_456').replace('alw_square_30', 'alw_rectangle_456')
        else:
            thumb = thumb.replace('/styles/alw_square_30_full/public', '').replace('/styles/alw_square_30/public', '')
            fanart = ''
        title = event[2].replace('&amp;', '&').replace('&#039;', "'").replace('&quot;', '"')
        link = sys.argv[0] + '?site=' + urllib.quote_plus(url) + '&mode=list-concert-videos'
        item = xbmcgui.ListItem('%s' % title, iconImage='', thumbnailImage=thumb)
        item.setProperty('fanart_image', fanart)
        if xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=True): item_added = True
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def list_concert_videos(language, site='', page=0, last_page=0, sort='latest'):  # sort=lastchance
    from resources.lib.functions import translate
    url = 'http://concert.arte.tv%s?page=%i&sort=%s&type=videop' % (urllib.unquote_plus(site) or '/%s/videos/all' % language, page, sort)
    try:
        html = urllib2.urlopen(url).read()
    except:
        return -1
    items = html.split('<article')
    del items[0]
    item_added = False
    for item in items:
        try:
            current_index = 0
            search_string = 'about="'
            len_search_string = len(search_string)
            start_index = item.find(search_string, current_index)
            if start_index > -1:
                end_index = item.find('"', start_index + len_search_string)
                if end_index > -1:
                    url = 'http://concert.arte.tv' + item[start_index + len_search_string:end_index]
                    current_index = end_index
                else:
                    url = ''
                    current_index += len_search_string
            else:
                url = ''
            ###
            search_string = 'title="'
            len_search_string = len(search_string)
            start_index = item.find(search_string, current_index)
            if start_index > -1:
                end_index = item.find('"', start_index + len_search_string)
                if end_index > -1:
                    title = item[start_index + len_search_string:end_index].replace('&amp;', '&').replace('&#039;', "'").replace('&quot;', '"')
                    current_index = end_index
                else:
                    title = ''
                    current_index += len_search_string
            else:
                title = ''
            ###
            search_string = ' src="'
            len_search_string = len(search_string)
            start_index = item.find(search_string, current_index)
            if start_index > -1:
                end_index = item.find('"', start_index + len_search_string)
                if end_index > -1:
                    thumb = item[start_index + len_search_string:end_index]
                    current_index = end_index
                else:
                    thumb = ''
                    current_index += len_search_string
            else:
                thumb = ''
            fanart = thumb
            thumb = thumb.replace('https:', 'http:').replace('alw_rectangle_376', 'alw_rectangle_456')
            fanart = fanart.replace('https:', 'http:').replace('/styles/alw_rectangle_376/public', '')
            ###
            search_string = '<span class="date-container">'
            len_search_string = len(search_string)
            start_index = item.find(search_string, current_index)
            if start_index > -1:
                end_index = item.find('</span>', start_index + len_search_string)
                if end_index > -1:
                    date = item[start_index + len_search_string:end_index].replace('\n', '').replace(' ', '')
                    current_index = end_index
                else:
                    date = ''
                    current_index += len_search_string
            else:
                date = ''
            ###
            search_string = '<span class="time-container">'
            len_search_string = len(search_string)
            start_index = item.find(search_string, current_index)
            if start_index > -1:
                end_index = item.find('</span>', start_index + len_search_string)
                if end_index > -1:
                    duration = item[start_index + len_search_string:end_index].replace('\n', '').replace(' ', '').replace('"', '')
                    current_index = end_index
                else:
                    duration = ''
                    current_index += len_search_string
            else:
                duration = ''
            if len(duration) == 8 and duration.count(':') == 2:
                try:
                    hours = int(duration[:2])
                    minutes = int(duration[3:5])
                    seconds = int(duration[6:])
                    duration_in_seconds = hours * 3600 + minutes * 60 + seconds
                except:
                    duration_in_seconds = 0
            else:
                duration_in_seconds = 0
            ###
            search_string = 'property="content:encoded">'
            len_search_string = len(search_string)
            start_index = item.find(search_string, current_index)
            if start_index > -1:
                end_index = item.find('</', start_index + len_search_string)
                if end_index > -1:
                    desc = item[start_index + len_search_string:end_index].replace('\n    ', '').replace('&amp;', '&').replace('&#039;', "'").replace('&quot;', '"')
                    if date:
                        desc = '%s\n%s' % (date, desc)
                    current_index = end_index
                else:
                    desc = ''
                    current_index += len_search_string
            else:
                desc = ''
            ###
            search_string = '<span class="tag video-genre">'
            len_search_string = len(search_string)
            start_index = item.find(search_string, current_index)
            if start_index > -1:
                end_index = item.find('</span>', start_index + len_search_string)
                if end_index > -1:
                    genre = item[start_index + len_search_string:end_index]
                    current_index = end_index
                else:
                    genre = ''
                    current_index += len_search_string
            else:
                genre = ''
            ###
            link = sys.argv[0] + '?mode=play-video&page=' + urllib.quote_plus(url)
            item = xbmcgui.ListItem('%s' % title, iconImage='', thumbnailImage=thumb)
            item.setInfo(type='Video', infoLabels={
                'Title': title,
                'Plot': desc,
                'Genre': genre
            })
            item.addStreamInfo('video', {'duration': duration_in_seconds})
            item.addStreamInfo('audio', {'language': language})
            item.setProperty('IsPlayable', 'true')
            item.setProperty('fanart_image', fanart)
            if xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item): item_added = True
        except: continue
    if len(items) in (8, 12): # most likely next page available...
        link = '%s?mode=list-concert-videos&site=%s&page=%i&sort=%s' % (sys.argv[0], site, page + 1, sort)
        item = xbmcgui.ListItem('[B][COLOR fffd8bc8]%s (%i)[/COLOR][/B]' % (translate(30012), page + 2), iconImage='')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return item_added
