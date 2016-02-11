# -*- coding: utf-8 -*-
import urllib2
import json
import sys
import xbmcplugin
import xbmcgui

def list_all_clusters(language = 'de', icon = ''):
    api_url = 'http://www.arte.tv/papi/tvguide/epg/clusters/%s/0/ALL.json' % language[0].upper()
    json_data = urllib2.urlopen(api_url).read()
    clusters = json.loads(json_data)['configClusterList']
    lang = language.upper()
    for cluster in clusters:
        try:
            if cluster['hidden']: continue
            cluster_id = cluster['clusterId']
            title = cluster['title' + lang]
            subtitle = cluster['subtitle' + lang]
            desc = cluster['text1' + lang]
            thumb = cluster['img' + lang]['IUR']
            # fanart = cluster['img' + lang]['imageOrigin']
            link = '%s?mode=list-videos&cluster=%s' % (sys.argv[0], cluster_id)
            item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
            item.setInfo(type='Video', infoLabels={
                'Title'             : title, 
                'Plot'              : desc,
                }
            )
            item.setProperty('fanart_image', thumb)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=True)
        except: continue
    xbmcplugin.endOfDirectory(int(sys.argv[1]))