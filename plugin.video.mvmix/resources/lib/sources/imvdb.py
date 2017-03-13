# -*- coding: utf-8 -*-

from resources.lib import simple_requests as requests
import json,urllib

site = 'imvdb'
headers = {'IMVDB-APP-KEY': 'hjyG4SOzr73y6Prb95G1jeeIG1z5HwkYQTFULuud'}

def get_videos(artist):
    videos = []
    artist_id = get_artist_id(artist)
    if artist_id:
        try:
            url = 'https://imvdb.com/api/v1/entity/%s' % str(artist_id)
            params = {'per_page':'50', 'page':'1', 'include':'artist_videos', }
            json_data = requests.get(url, headers=headers, params=params).json()
        except:
            return False
        try:
            for v in json_data['artist_videos']['videos']:
                try:
                    id = v['id']
                    title = str(v['song_title'])
                    image = v['image']['o']
                    duration = ''
                    videos.append({'site':site, 'artist':[artist], 'title':title, 'duration':duration, 'id':id, 'image':image})
                except:
                    pass
        except:
            pass
    elif artist_id == False:
        return False
    return videos
    
def get_video_url(id):
    video_url = None
    try:
        url = 'http://imvdb.com/api/v1/video/%s' % str(id)
        params = {'include':'sources'}
        json_data = requests.get(url, headers=headers, params=params).json()
        for q in json_data['sources']:
            if q['source'] == 'vimeo':
                import vimeo
                video_url = vimeo.get_video_url(q['source_data'])
                break
            if q['source'] == 'youtube':
                import youtube
                video_url = youtube.get_video_url(q['source_data'])
                break
    except:
        pass
    return video_url

def get_artist_id(artist):
    artist_id = None
    try:
        url = 'https://imvdb.com/api/v1/search/entities'
        params = {'q':urllib.quote_plus(artist)}
        json_data = requests.get(url, headers=headers, params=params).json()
        artists = json_data['results']
        for a in artists:
            # name not present
            if a['slug'].replace('-',' ').encode('utf-8').lower() == artist.replace('-',' ').lower():
                artist_id = a['id']
                break
    except:
        return False
    return artist_id