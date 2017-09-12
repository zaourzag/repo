# -*- coding: utf-8 -*-

from common import *

class Items:

    def __init__(self):
        self.cache = True
        self.video = False
    
    def list(self, sort=False, upd=False):
        if self.video:
            xbmcplugin.setContent(addon_handle, content)
        if sort:
            xbmcplugin.addSortMethod(addon_handle, 1)
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=self.cache, updateListing=upd)
        
        if force_view:
            xbmc.executebuiltin('Container.SetViewMode({0})'.format(view_id))

    def add(self, item):    
        data = {
            'mode': item['mode'],
            'title': item['title'],
            'id': item.get('id', ''),
            'params': item.get('params', '')
        }
                    
        art = {
            'thumb': item.get('thumb', fanart),
            'poster': item.get('thumb', fanart),
            'fanart': item.get('fanart', fanart)
        }
                
        labels = {
            'title': item['title'],
            'plot': item.get('plot', ''),
            'premiered': item.get('date', ''),
            'episode': item.get('episode', 0)
        }
        
        listitem = xbmcgui.ListItem(item['title'])
        listitem.setArt(art)
        listitem.setInfo(type='Video', infoLabels=labels)
        
        if 'play' in item['mode']:
            self.cache = False
            self.video = True
            folder = False
            listitem.addStreamInfo('video', {'duration':item.get('duration', 0)})
            listitem.setProperty('IsPlayable', 'true')
        else:
            folder = True
            
        if item.get('cm', None):
            listitem.addContextMenuItems( item['cm'] )

        xbmcplugin.addDirectoryItem(addon_handle, build_url(data), listitem, folder)
        
    def play(self, path, license_key):
        listitem = xbmcgui.ListItem()
        listitem.setContentLookup(False)
        listitem.setMimeType('application/x-mpegURL')
        listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
        listitem.setProperty('inputstream.adaptive.license_key', license_key)
        listitem.setPath(path)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
        
    def add_token(self, license_key):
        listitem = xbmcgui.ListItem()
        xbmcplugin.addDirectoryItem(addon_handle, license_key, listitem)
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)