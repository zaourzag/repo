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
        try:
            title = parser.unescape(title)
        except:
            pass
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
            try:
                video_data = re.findall(pattern_video_data, video, re.DOTALL)[0]
            except:
                continue
            url, thumb, title = video_data
            try:
                title = parser.unescape(title)
            except:
                pass
            try:
                thumb = parser.unescape(thumb)
            except:
                pass
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
            streams = part['sources']
            if not streams:
                continue
            stream_part = part['title'], part['preview_image_url'], streams[-1]['src']
            for stream in streams:
                if stream['protocol'] == 'http':
                    stream_part = part['title'], part['preview_image_url'], stream['src']
                    break
            playlist.append(stream_part)
    return playlist
