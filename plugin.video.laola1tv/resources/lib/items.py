# -*- coding: utf-8 -*-

from common import *
from menu import Menu
from videos import Videos
from live_videos import Live_Videos
from live import Live

class Items:

    def __init__(self):
        self.cache = True
        self.video = False
    
    def list(self):
        if self.video:
            xbmcplugin.setContent(addon_handle, content)
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=self.cache)
        
        if force_view:
            xbmc.executebuiltin('Container.SetViewMode(%s)' % view_id)

    def add(self, item):    
        data = {
                'mode'   : item['mode'],
                'title'  : item['title'],
                'id'     : item.get('id', ''),
                'params' : item.get('params', '')
                }
                    
        art = {
                'thumb'  : item.get('thumb', icon),
                'poster' : item.get('thumb', icon),
                'fanart' : fanart
                }

        labels = {
                    'title'     : item['title'],
                    'plot'      : item.get('plot', ''),
                    'premiered' : item.get('date', ''),
                    'episode'   : item.get('episode', 0)
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
            
        xbmcplugin.addDirectoryItem(addon_handle, build_url(data), listitem, folder)
        
    def play(self, path):
        listitem = xbmcgui.ListItem(path=path)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
        
items = Items()

def menu(data):
    items.add({'mode':'live', 'title':getString(30101)})
    sports = data[0]['children']
    for i in sports:
        items.add(Menu(i, 'sports').item)
    items.list()
    
def sports(data, channel):
    channels = data[0]['children']
    for c in channels:
        if channel == utfenc(c['title']):
            for i in c['children']:
                items.add(Menu(i, 'sub_menu').item)
            break
    items.list()
    
def sub_menu(data):
    container = data['container']
    for c in container:
        if c['content']:
            if c.get('page', None):
                items.add(Menu(c, 'videos').item)
            else:
                for i in c['content']:
                    items.add(Videos(i).item)
        elif c['schedule']:
            for s in c['schedule']:
                items.add(Live_Videos(s).item)
    items.list()
    
def live(data):
    videos = data.get('video', [])
    for i in videos:
        items.add(Live(i).item)
    items.list()

def video(data):
    content = data['container'][0]['content']
    for i in content:
        items.add(Videos(i).item)
    items.list()
    
def play(path):
    items.play(path)