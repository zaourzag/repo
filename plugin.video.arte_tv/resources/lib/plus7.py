# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import sys
import xbmcplugin
import xbmcgui
from resources.lib.functions import translate


def add_folder(title, thumb, mode, site='', desc='', fanart='', icon=''):
    link = '%s?%s' % (sys.argv[0], mode)
    item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    item.setProperty('fanart_image', fanart or thumb)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=True)


def list_index():
    import xbmc
    import xbmcaddon
    import os.path
    addon_path = xbmc.translatePath(xbmcaddon.Addon('plugin.video.arte_tv').getAddonInfo('path')).decode('utf-8')
    add_folder(translate(30006), os.path.join(addon_path, 'resources', 'media', 'plus7.png'),
               'mode=list-videos&recommended=1')
    add_folder(translate(30007), os.path.join(addon_path, 'resources', 'media', 'plus7.png'),
               'mode=list-videos&sort=VIEWS')
    add_folder(translate(30008), os.path.join(addon_path, 'resources', 'media', 'plus7.png'), 'mode=list-videos')
    add_folder(translate(30009), os.path.join(addon_path, 'resources', 'media', 'plus7.png'),
               'mode=list-videos&sort=LAST_CHANCE')
    add_folder(translate(30010), os.path.join(addon_path, 'resources', 'media', 'plus7.png'), 'mode=list-clusters')
    add_folder(translate(30011), os.path.join(addon_path, 'resources', 'media', 'plus7.png'), 'mode=list-channels')
    add_folder(translate(30005), os.path.join(addon_path, 'resources', 'media', 'plus7.png'),
               'mode=plus7-search&scope=plus7')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


# http://www.arte.tv/papi/tvguide/videos/plus7/program/F/L2/ALL/ALL/-1/AIRDATE_DESC/0/0/DE_FR.json
def list_videos(
        language='de',
        category='ALL',
        cluster='ALL',
        detail_level='L3',
        sort='AIRDATE_DESC',
        limit=0,
        offset=0,
        recommended=-1,
        current_page=0,
        thumb_as_fanart=True
):
    language_code = language[0].upper()
    url = 'http://www.arte.tv/papi/tvguide/videos/plus7/program/%s/%s/%s/%s/%i/%s/%i/%i/DE_FR.json' % (
    language_code, detail_level, category, cluster, recommended, sort, limit, offset)
    try:
        json_data = urllib2.urlopen(url).read()
        videos = json.loads(json_data)['program%sList' % language.upper()]
    except:
        return -1  # no network
    item_added = False
    for video in videos:
        try:
            rating = video['mediaRating' + language_code]
            duration_in_seconds = video['VDO']['videoDurationSeconds']
            json_stream_url = video['VDO']['videoStreamUrl']
            thumb = video['VDO']['VTU']['IUR']
            if thumb_as_fanart:
                fanart = thumb
            else:
                fanart = video['VDO']['VTU']['original']
            title = video['TIT']
            try:
                subtitle = video['STL']
                sep = ' - '
            except:
                subtitle = sep = ''
            try:
                genre = video['GEN']
            except:
                genre = ''
            year = video['VDO']['productionYear']
            try:
                desc = video['DLO'].replace(' ' * 6, '')
            except:
                desc = video['DTE']
            try:
                director = video['VDO']['director']
            except:
                director = ''
            cast_and_role = []
            try:
                cast = video['CCW']
                for entry in cast:
                    try:
                        cast_and_role.append((entry['CNA'], entry['CRO']))
                    except:
                        try:
                            cast_and_role.append((entry['CNA'], entry['CTY']))
                        except:
                            pass
            except:
                pass
            try:
                short_desc = video['VDO']['V7T']
            except:
                short_desc = ''
            try:
                studio = video['POR']
            except:
                studio = ''
            try:
                country = video['PCT']
            except:
                country = ''
            link = sys.argv[0] + '?stream=' + urllib.quote_plus(json_stream_url) + '&mode=play-video'
            item = xbmcgui.ListItem('[B]%s[/B]%s%s' % (title, sep, subtitle), iconImage='', thumbnailImage=thumb)
            item.setInfo(type='Video', infoLabels={
                'Title': '%s%s%s' % (title, sep, subtitle),
                'Plot': desc,
                'PlotOutline': short_desc,
                'Mpaa': rating,
                'Genre': genre,
                'Year': year,
                'Director': director,
                'CastAndRole': cast_and_role,
                'Studio': studio,
                'Country': country,
            }
                         )
            item.addStreamInfo('video', {'duration': duration_in_seconds})
            item.addStreamInfo('audio', {'language': language})
            item.setProperty('IsPlayable', 'true')
            item.setProperty('fanart_image', fanart)
            if xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item): item_added = True
        except:
            continue
    if len(videos) == limit:  # most likely this page isn't the limit...
        link = '%s?mode=list-videos&page=%i&category=%s&cluster=%s&sort=%s&recommended=%i' % (
        sys.argv[0], current_page + 1, category, cluster, sort, recommended)
        item = xbmcgui.ListItem('[B][COLOR fffa481c]%s (%i)[/COLOR][/B]' % (translate(30012), current_page + 2),
                                iconImage='')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return item_added
