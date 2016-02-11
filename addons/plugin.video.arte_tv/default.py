# -*- coding: utf-8 -*-
import urllib
import xbmcaddon
import xbmc
from resources.lib.functions import translate, parameters_string_to_dict

addon = xbmcaddon.Addon(id = 'plugin.video.arte_tv')
language = ('de', 'fr', 'en', 'es')[int(addon.getSetting('language'))]
details = ('L2', 'L3')[1 if addon.getSetting('loadExtraDetails') == 'true' else 0]
items_per_page = (10, 15, 20, 25, 50)[int(addon.getSetting('videosPerPage'))]
thumb_as_fanart = addon.getSetting('useThumbAsFanart') == 'true'
bitrate = (300, 800, 1500, 2200)[int(addon.getSetting('prefVideoQuality'))]

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))

if mode == 'highlights':
    site = urllib.unquote_plus(params.get('site', ''))
    if site == 'index':
        from resources.lib.highlights import list_index
        list_index()
    elif site == 'recommended':
        from resources.lib.plus7 import list_videos
        list_videos(language, recommended = 1, limit = items_per_page, detail_level = details)
    elif site == 'tv':
        pass # epg at -1|20.15|+1 -> trailers
    else:
        from resources.lib.highlights import list_highlight_videos
        if site == 'ctouch':
            list_highlight_videos('http://culture-touch-api.arte.tv/videofeeds/%s.json', language, 'ARTETV', bitrate)
        elif site == 'concert':
            list_highlight_videos('http://www.arte.tv/videofeed/ALW/%s/most_recent.json', language, 'ALW', bitrate)
        elif site == 'info':
            list_highlight_videos('http://www.arte.tv/videofeed/INFO/%s/most_recent.json', language, 'INFO', bitrate)
        elif site == 'cinema':
            list_highlight_videos('http://www.arte.tv/videofeed/CINEMA/%s/most_recent.json', language, 'CINEMA', bitrate)
        elif site == 'creative':
            list_highlight_videos('http://www.arte.tv/videofeed/CREATIVE/%s/most_recent.json', language, 'CREATIVE', bitrate)
        else:
            list_highlight_videos('http://www.arte.tv/videofeed/FUTURE/%s/most_recent.json', language, 'FUTURE', bitrate)
elif mode == 'concert':
    from resources.lib.concert import list_collections, list_concert_index
    site = urllib.unquote_plus(params.get('site', ''))
    if site:
        list_collections(language, type = site)
    else:
        list_concert_index(language)
elif mode == 'concert-search':
    import xbmc
    from resources.lib.concert import *
    keyboard = xbmc.Keyboard('', translate(30005))
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_string = keyboard.getText()
        concert_search(language, search_string, page = 0)
elif mode == 'list-concert-videos':
    from resources.lib.concert import *
    site = urllib.unquote_plus(params.get('site', ''))
    sort = urllib.unquote_plus(params.get('sort', '')) or 'latest'
    page = int(urllib.unquote_plus(params.get('page', '')) or 0)
    list_concert_videos(language, site, page, sort=sort)
elif mode == 'plus7':
    from resources.lib.plus7 import list_index
    list_index()
elif mode == 'plus7-search':
    import xbmc
    from resources.lib.plus7search import list_search_results
    scope = urllib.unquote_plus(params.get('scope', ''))
    keyboard = xbmc.Keyboard('', translate(30005))
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_string = keyboard.getText()
        list_search_results(search_string, language, scope)
elif mode == 'epg':
    from resources.lib.epg import list_tv_dates
    list_tv_dates()
elif mode == 'list-tv-guide':
    from resources.lib.epg import list_tv_guide
    date = urllib.unquote_plus(params.get('date', ''))
    list_tv_guide(language, details, date)
elif mode == 'live-tv':
    from resources.lib.livetv import play_livestream
    play_livestream(language)
elif mode == 'play-video':
    from resources.lib.player import *
    page = urllib.unquote_plus(params.get('page', ''))
    if page:
        vp_api_url = get_vp_api_url(page)
        stream = get_vp_stream_url(vp_api_url, bitrate)
        play_video(stream)
    else:
        player_url = urllib.unquote_plus(params.get('stream', ''))
        if player_url:
            stream_url = get_stream_url(player_url, language, bitrate)
        else:
            id = urllib.unquote_plus(params.get('id', ''))
            vector = urllib.unquote_plus(params.get('vector', '')) or 'ARTEPLUS7'
            stream_url = get_stream_url_by_id(id, language, bitrate, vector)
        title = urllib.unquote_plus(params.get('title', ''))
        if title:
            import xbmcgui
            thumb = urllib.unquote_plus(params.get('thumb', ''))
            item = xbmcgui.ListItem(title, thumbnailImage=thumb)
            xbmc.Player().play(stream_url, item)
        else:
            play_video(stream_url)
elif mode == 'list-videos':
    from resources.lib.plus7 import list_videos
    lmt = int( urllib.unquote_plus(params.get('limit', '')) or items_per_page )
    page_number = int( urllib.unquote_plus(params.get('page', '')) or 0 )
    ofst = 0 if page_number == 0 else page_number*lmt + 2
    list_videos(
        language = language,
        category = urllib.unquote_plus(params.get('category', '')) or 'ALL', 
        cluster = urllib.unquote_plus(params.get('cluster', '')) or 'ALL', 
        detail_level = details, 
        sort = urllib.unquote_plus(params.get('sort', '')) or 'AIRDATE_DESC', 
        limit = lmt,
        offset = ofst,
        recommended = int( urllib.unquote_plus(params.get('recommended', '')) or -1 ), 
        current_page = page_number,
        thumb_as_fanart = thumb_as_fanart
    )
elif mode == 'list-clusters':
    from resources.lib.clusters import list_all_clusters
    list_all_clusters(language)
elif mode == 'list-channels':
    from resources.lib.channels import list_all_channels
    list_all_channels(language)
else:
    from resources.lib.index import list_index
    list_index()
    