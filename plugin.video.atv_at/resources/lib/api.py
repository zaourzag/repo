# -*- coding: utf-8 -*-
import re
import requests
import gui
from HTMLParser import HTMLParser

__URL_MAIN_PAGE = 'http://atv.at'
__HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Accept-Encoding': 'gzip'
}


def list_clusters():
    url = __URL_MAIN_PAGE + '/mediathek/'
    response = requests.get(url, headers=__HEADERS)
    html = response.read()
    pattern = '<li class="program">.*?href="(.*?)".*?<img src="(.*?)".*?title="(.*?)".*?</li>'
    clusters = re.findall(pattern, html, re.DOTALL)
    parser = HTMLParser()
    for url, thumb, title in clusters:
        title = parser.unescape(title)
        gui.add_folder(title, thumb, {'f': 'cluster', 'url': url})
    gui.end_listing()


def list_cluster(url):
    response = requests.get(url, headers=__HEADERS)
    html = response.read()
    pattern_video = '<li class="teaser">(.*?)</li>'
    pattern_video_data = 'href="(.*?)".*?<img src="(.*?)".*?"title">(.*?)<'
    videos = re.findall(pattern_video, html, re.DOTALL)
    parser = HTMLParser()
    for video in videos:
        if '<div class="video_indicator">' in video:
            video_data = re.findall(pattern_video_data, video, re.DOTALL)[0]
            url, thumb, title = video_data
            title = parser.unescape(title)
            thumb = parser.unescape(thumb)
            gui.add_video(title, thumb, {'f': 'play', 'url': url})
    gui.end_listing()


def get_playlist(url):
    response = requests.get(url, headers=__HEADERS)
    html = response.read()
    match = re.search('FlashPlayer" data-jsb="(.*?)"', html)
    playlist = []  # [(title,image_url,stream_url),(title,image_url,stream_url),...]
    if match:
        parser = HTMLParser()
        response.text = parser.unescape(match.group(1))
        json_data = response.json()
        parts = json_data['config']['initial_video']['parts']
        for part in parts:
            if part['is_geo_ip_blocked']:
                gui.warning('Video nicht abspielbar', 'Dieses Video ist nur in Österreich verfügbar!')
                return playlist
            streams = part['sources']
            if not streams:
                continue
            stream_part = part['title'], part['preview_image_url'], streams[0]['src']
            for stream in streams:
                if stream['protocol'] == 'http':
                    stream_part = part['title'], part['preview_image_url'], stream['src']
                    break
            playlist.append(stream_part)
    return playlist
