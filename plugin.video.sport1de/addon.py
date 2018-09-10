# -*- coding: utf-8 -*-

from resources.lib.common import *
from resources.lib.client import Client
from resources.lib import sport1
from resources.lib import cache

client = Client()

def tv_category():
    if addon.getSetting('startup') == 'true':
        video_root = client.get_video_root()
        if video_root:
            cache.cache_data(video_root)
            addon.setSetting('startup', 'false')
    data = client.get_tv_epg()
    list_items(sport1.get_tv_items(data))
    xbmcplugin.endOfDirectory(addon_handle)

def video_category():
    data = cache.get_cache_data()
    if data:
        list_items(sport1.get_video_category_items(data, id))
    xbmcplugin.endOfDirectory(addon_handle)

def videos():
    if 'api/playlist' in id:
        url = id
    else:
        url = sport1.get_playlist_url(client.get_resource(id))
    if url:
        data = client.get_playlist(url)
        if data:
            list_items(sport1.get_video_items(data))
    xbmcplugin.endOfDirectory(addon_handle)

def livestream():
    data = client.get_tv()
    if data:
        list_items(sport1.get_live_video_items(data))
    xbmcplugin.endOfDirectory(addon_handle)

def replay():
    data = client.get_replay()
    if data:
        list_items(sport1.get_replay_items(data))
    xbmcplugin.endOfDirectory(addon_handle)
    
def play_video():
    if id:
        play(id)

def play_tv():
    result = sport1.get_hls(client.get_tv(id))
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
    _id = item['id']
    image = item.get('image', icon)
    plot = item['description']
    u = build_url({'mode': item['mode'], 'name':name, 'id':_id})
    item=xbmcgui.ListItem(item['name'], iconImage="DefaultVideo.png", thumbnailImage=image)
    item.setInfo(type='Video', infoLabels={'Title':name, 'Plot':plot})
    item.addStreamInfo('video', {'duration':duration})
    item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(addon_handle,url=u,listitem=item)

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)
id = args.get('id', [''])[0]
log('[%s] Arguments: %s' % (addon_id, str(args)))

if mode==None:
    tv_category()
else:
    exec '%s()' % mode[0]