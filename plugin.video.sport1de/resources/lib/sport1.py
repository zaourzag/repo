# -*- coding: utf-8 -*-

from common import *

def get_category_items():
    return [
                {'type':'dir', 'mode':'tv_category', 'name':'Live-TV'},
                #{'type':'dir', 'mode':'live_radio', 'name':'Radio'},
                {'type':'dir', 'mode':'video_category', 'name':'Mediathek'}
            ]

def get_video_category_items(data, id):
    items = []
    if id:
        children = find_children(data['children'][0]['children'], id)
    else:
        children = data['children'][0]['children']
    for child in children:
        sub_children = child['children']
        resource = child['resource']
        if sub_children:
            items.append({'type': 'dir', 'mode': 'video_category', 'name': utfenc(child['title']), 'id': child['slug']})
        elif resource:
            items.append({'type': 'dir', 'mode': 'videos', 'name': utfenc(child['title']), 'id': resource})
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
    stations = data['stations']
    for s in stations:
        title = s['title']
        current_programs = s['current_programs'][0]
        description = current_programs['description']
        start = current_programs['from'].split('T')[-1]
        end = current_programs['to'].split('T')[-1]
        link = s['link']
        name = utfenc('%s %s %s %s' % (title,start,description,end))
        items.append({'type':'video', 'mode':'play_tv', 'name':name, 'id':link, 'description':'', 'duration':'0'})
    items.append({'type':'dir', 'mode':'livestream', 'name':'LIVESTREAM', 'id':'', 'description':'', 'duration':'0'})
    return items

def get_live_video_items(data):
    items = []
    live = re.search('id="stream_tile_livestream"(.*?)<hr>', data, re.S)
    if live:
        a = live.group(1)
        items = get_event_items(items,a,live=True)
    ondemand = re.search('id="stream_tile_ondemandstream"(.*?)<hr>', data, re.S)
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
    
def get_live_radio_items(data):
    items = []
    content = data['content']
    for i in content:
        url = i['url']
        desc = i['description']
        if not url and desc.startswith('http'):
            url = desc
        description = '%s\n%s' % (i['startzeit'][:22], desc)
        item = {'type':'video', 'mode':'play_video', 'name':utfenc(i['titel']), 'id':url, 'description':utfenc(description), 'duration':i['duration']}
        items.append(item)
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
        pattern = '<div class="article streams">(.+?)</p>'
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