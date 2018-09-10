# -*- coding: utf-8 -*-

from common import *

def get_video_category_items(data, id):
    items = []
    if id:
        children = find_children(data['children'][0]['children'], id)
    else:
        children = data['children'][0]['children']
        items.append({'type': 'dir', 'mode': 'videos', 'name': 'Neue Videos', 'id': www_base + '/api/playlist/neue-videos'})
        items.append({'type': 'dir', 'mode': 'videos', 'name': 'Top Videos', 'id': www_base + '/api/playlist/top-videos'})
    for child in children:
        sub_children = child['children']
        resource = child['resource']
        if sub_children:
            items.append({'type': 'dir', 'mode': 'video_category', 'name': utfenc(child['title']), 'id': child['slug']})
        elif resource:
            items.append({'type': 'dir', 'mode': 'videos', 'name': utfenc(child['title']), 'id': resource.replace('http://video.sport1.de', www_base)})
    return items

def get_children(children, search_slug):
    for i in children:
        if search_slug == i['slug']:
            return i['children']

def find_children(data, id):
    search_slug = ''
    spl = id.split('/')
    for i in spl:
        if i:
            search_slug += '/'+i
            data = get_children(data, search_slug)
    return data

def get_playlist_url(data):
    url = None
    elements = data['elements']
    for i in elements:
        sub_elements = i.get('elements', '')
        if sub_elements:
            for s in sub_elements:
                if 'video_detailed' in s.get('type', ''):
                    url = s['elements'][0]['url']
                    break
    return url

def get_video_items(data):
    items = []
    videos = data['videos']
    for i in videos:
        title = i['title']
        image = i['image']
        duration = int(i['durationSeconds'])
        date = i['date']
        dt = datetime.datetime.fromtimestamp(int(date))
        dt = str(dt)[:16]
        description = '%s\n%s' % (utfenc(i['description']), dt)
        url = i['url']
        if url:
            for u in url:
                mp4 = url[u]
                if 'high_quality' == u:
                    break
        else:
            mp4 = i['media']
        items.append({'type':'video', 'mode':'play_video', 'name':utfenc(title), 'id':mp4, 'description':utfenc(description), 'image':image, 'duration':duration})
    return items

def get_tv_items(data):
    items = []
    stations = data.get('stations', [])
    for s in stations:
        channel = s['title']
        current_programs = s['current_programs'][0]
        title = current_programs['title']
        subtitle = current_programs['subtitle']
        description = current_programs['long_description']
        start = current_programs['from'].split('T')[-1][:-3]
        end = current_programs['to'].split('T')[-1][:-3]
        link = s['link']
        name = '%s %s %s %s %s' % (channel,start,title,subtitle,end)
        items.append({'type':'video', 'mode':'play_tv', 'name':utfenc(name.replace('Live', '[COLOR red]Live[/COLOR]')), 'id':link, 'description':utfenc(description), 'duration':'0'})
    items.append({'type':'dir', 'mode':'livestream', 'name':'Weitere Livestreams', 'id':'', 'description':''})
    items.append({'type':'dir', 'mode':'replay', 'name':'Sendung verpasst?', 'id':'', 'description':''})
    items.append({'type':'dir', 'mode':'video_category', 'name':'Mediathek'})
    return items

def get_live_video_items(data):
    items = []
    live = re.search('id="stream_tile_livestream"(.*?)</div>\s*\n*</div>\s*\n*</div>', data, re.S)
    if live:
        a = live.group(1)
        items = get_event_items(items,a,live=True)
    ondemand = re.search('id="stream_tile_ondemandstream"(.*?)</div>\s*\n*</div>\s*\n*</div>', data, re.S)
    if ondemand:
        a = ondemand.group(1)
        items = get_event_items(items,a,live=False)
    return items
    
def get_event_items(items,a,live):
    b = re.findall('<div style=(.*?)</a>', a, re.S)
    for c in b:
        d = re.search('href="(.+?)"', c, re.S).group(1)
        e = re.search('data-background="(.+?)"', c, re.S).group(1)
        f = re.search('<span class="dateInfo">(.+?)</span>', c, re.S)
        g = re.search('<span class="event">(.+?)</span>', c, re.S)
        if f and g:
            if not d.startswith('http'):
                d = tv_base+d
            if not e.startswith('http'):
                e = tv_base+e
            if live:
                h = utfenc('%s %s' % (f.group(1)[:18],g.group(1)))
            else:
                h = utfenc('ARCHIV: %s %s' % (f.group(1)[:18],g.group(1)))
            items.append({'type':'video', 'mode':'play_tv', 'name':h, 'id':d, 'image':e, 'description':'', 'duration':'0'})
    return items

def get_replay_items(data):
    items = []
    tiles = re.search('<div class="stream_tiles(.*?)<div class="arrow right"></div>', data, re.S)
    if tiles:
        items = replay_items(tiles.group(1))
    return items

def replay_items(a):
    items = []
    b = re.findall('<div style=(.*?)</ul>', a, re.S)
    for c in b:
        d = re.search('href="(.+?)"', c, re.S).group(1)
        e = re.search('background: url\(\'(.+?)\'', c, re.S).group(1)
        f = re.search('<b>(.+?)</b>', c, re.S).group(1)
        g = re.search('<span class="event">(.+?)</span>', c, re.S).group(1)
        p = re.search('<p class="text">(.+?)</p>', c, re.S).group(1)
        p = re.sub('.+?<br>', '', p)
        if not d.startswith('http'):
            d = tv_base+d
        if not e.startswith('http'):
            e = tv_base+e
        h = '%s %s' % (f[:16],g)
        items.insert(0, {'type':'video', 'mode':'play_tv', 'name':utfenc(h), 'id':d, 'image':e, 'description':utfenc(p), 'duration':'0'})
    return items

def get_hls(data):
    result = ''
    pattern2 = '<div class="player".*?src="(.*?)"'
    pattern1 = 'file\s*:\s*"(.*?)"'
    a = re.search(pattern1, data)
    if a:
        s = a
    else:
        s = re.search(pattern2, data)
    if s:
        return s.group(1)
    else:
        pattern = '<div class="player">(?:<p class="error">|<p>)(.*?)</p>'
        s = re.search(pattern, data, re.S)
        if s:
            msg = s.group(1).strip()
            return re.sub('(<.+?>)', '', msg)
        pattern = '<div class="article streams">(.+?)(?:<a class|</p>)'
        s = re.search(pattern, data, re.S)
        if s:
            msg = s.group(1).strip()
            return re.sub('(<.+?>)', '', msg)
        pattern = '<p class="text">(.+?)</p>'
        s = re.search(pattern, data, re.S)
        if s:
            msg = s.group(1).strip()
            return re.sub('(<.+?>)', '', msg)
    return result