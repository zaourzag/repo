# -*- coding: utf-8 -*-

from resources.lib.common import *
from resources.lib.client import Client
from resources.lib import sport1

client = Client()

def categories():
    items = sport1.get_category_items()
    list_items(items)
    xbmcplugin.endOfDirectory(addon_handle)

def tv_category():
    data = client.get_tv_epg()
    if data:
        items = sport1.get_tv_items(data)
        list_items(items)
    xbmcplugin.endOfDirectory(addon_handle)

def video_category():
    items = sport1.get_video_category_items()
    list_items(items)
    xbmcplugin.endOfDirectory(addon_handle)

def radio_category():
    items = sport1.get_radio_category_items()
    list_items(items)
    xbmcplugin.endOfDirectory(addon_handle)

def playlist():
    id = args['id'][0]
    data = client.get_page(id)
    if data:
        url = sport1.get_playlist_url(data)
        if url:
            data = client.get_playlist(url)
            if data:
                items = sport1.get_video_items(data,quality)
                list_items(items)
    xbmcplugin.endOfDirectory(addon_handle)

def live_radio():
    data = client.get_radio()
    if data:
        items = sport1.get_live_radio_items(data)
        list_items(items)
    xbmcplugin.endOfDirectory(addon_handle)

def videos():
    id = args['id'][0]
    data = client.get_playlist(id)
    if data:
        items = sport1.get_video_items(data)
        list_items(items)
    xbmcplugin.endOfDirectory(addon_handle)

def livestream():
    data = client.get_tv()
    if data:
        items = sport1.get_live_video_items(data)
        list_items(items)
    xbmcplugin.endOfDirectory(addon_handle)
    
def play_video():
    path = args['id'][0]
    if path:
        play(path)

def play_tv():
    id = args['id'][0]
    data = client.get_tv(id)
    result = sport1.get_hls(data)
    if '.m3u8' in result:
        play(result)
    else:
        log('[%s] play error: %s' % (addon_id, utfenc(result)))
        dialog.ok(addon_name, utfenc(result))

def play(url):
    if not url.startswith('http'):
        url = 'https:' + url
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
    
def list_items(items):
    for i in items:
        if i['type'] == 'dir':
            add_dir(i)
        elif i['type'] == 'video':
            add_video(i)

def add_dir(item):
    u = build_url({'mode':item['mode'], 'name':item['name'], 'id':item.get('id', '')})
    item=xbmcgui.ListItem(item['name'], iconImage="DefaultFolder.png", thumbnailImage=item.get('image', icon))
    xbmcplugin.addDirectoryItem(addon_handle,url=u,listitem=item,isFolder=True)
    
def add_video(item):
    name = item['name']
    duration = item['duration']
    id = item['id']
    image = item.get('image', icon)
    plot = item['description']
    u = build_url({'mode': item['mode'], 'name':name, 'id':id})
    item=xbmcgui.ListItem(item['name'], iconImage="DefaultVideo.png", thumbnailImage=image)
    item.setInfo(type='Video', infoLabels={'Title':name, 'Plot':plot})
    item.addStreamInfo('video', {'duration':duration})
    item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(addon_handle,url=u,listitem=item)

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)
log('[%s] Arguments: %s' % (addon_id, str(args)))

if mode==None:
    categories()
else:
    exec '%s()' % mode[0]