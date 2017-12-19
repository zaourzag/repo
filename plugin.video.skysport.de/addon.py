#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import urlparse
import urllib
from HTMLParser import HTMLParser
import xbmc, xbmcplugin, xbmcaddon, xbmcgui
from bs4 import BeautifulSoup
import requests
import json

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

addon = xbmcaddon.Addon()
params = dict(urlparse.parse_qsl(sys.argv[2][1:]))
addon_handle = int(sys.argv[1])
cache = StorageServer.StorageServer(addon.getAddonInfo('name') + '.videoid', 24 * 30)

playmethod = addon.getSetting('playmethod')

HOST = 'http://sport.sky.de'
NAVIGATION_JSON_FILE = xbmc.translatePath(addon.getAddonInfo('path') +'/resources/navigation.json')

ADDON_BASE_URL = "plugin://" + addon.getAddonInfo('id')

VIDEO_URL_HSL = "http://player.ooyala.com/player/all/{video_id}.m3u8"
VIDEO_URL_DASH = "https://videossportskyde.akamaized.net/{video_id}/1/dash/1.mpd"

USER_AGENT = 'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'

def rootDir():
    nav = json.load(open(NAVIGATION_JSON_FILE))
    for item in nav:
        action = item.get('action', 'showVideos')
        if action == 'showVideos':
            url = build_url({'action': action, 'path': item.get('path'), 'show_videos': 'false'})
        else:
            url = build_url({'action': action, 'path': item.get('path'), 'hasitems': 'true' if item.get('children', None) is not None else 'false'})

        addDir(item.get('label'), url)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

def addDir(label, url, icon=None):
    addVideo(label, url, icon, True)

def addVideo(label, url, icon, isFolder=False):
    li = xbmcgui.ListItem(label, iconImage=icon, thumbnailImage=icon)
    li.setInfo('video', {})
    li.setProperty('IsPlayable', str(isFolder))

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=isFolder)

def build_url(query):
    return ADDON_BASE_URL + '?' + urllib.urlencode(query)

def listSubnavi(path, hasitems):
    if hasitems == 'false':
        url = urlparse.urljoin(HOST, path)
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        for item in soup('a', 'sdc-site-directory__content'):
            label = item.span.string
            url = build_url({'action': 'showVideos', 'path': item.get('href') + '-videos', 'show_videos': 'false'})
            addDir(label, url)
    else:
        items = None
        nav = json.load(open(NAVIGATION_JSON_FILE))
        for item in nav:
            if item.get('path') == path:
                items = item.get('children')

        if items is not None:
            for item in items:
                url = build_url({'action': 'showVideos', 'path': item.get('path'), 'show_videos': 'true'})
                addDir(item.get('label'), url)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

def showVideos(path, show_videos):
    url = urlparse.urljoin(HOST, path)
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    nav = soup.find('nav', {'aria-label': 'Videos:'})

    if show_videos == 'false' and nav is not None:
        for item in nav.findAll('a'):
            label = item.string
            url = build_url({'action': 'showVideos', 'path': item.get('href'), 'show_videos': 'true'})
            if label is not None and label != '':
                addDir(label, url)
    else:
        for item in soup('div', 'sdc-site-tiles__item sdc-site-tile sdc-site-tile--has-link'):
            link = item.find('a', {'class': 'sdc-site-tile__headline-link'})           
            label = link.span.string
            url = build_url({'action': 'playVideo', 'path': link.get('href')})
            icon = item.img.get('src')
            addVideo(label, url, icon)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

def getVideoIdFromCache(path):
    return cache.cacheFunction(getVideoId, path)

def getVideoId(path):
    video_id = None

    url = urlparse.urljoin(HOST, path)
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    div = soup.find('div', {'class': 'sdc-article-video'})
    if div is not None:
        video_id = div.get('data-sdc-video-id')

    if video_id is None:
        scripts = soup.findAll('script')
        for script in scripts:
            script = script.text
            match = re.search('data-sdc-video-id="([^"]*)"', script)
            if match is not None:
                video_id = match.group(1)

    return video_id

def playVideo(path):
    video_id = getVideoIdFromCache(path)
    if video_id is not None: 
        li = getVideoListItem(video_id)
        xbmcplugin.setResolvedUrl(addon_handle, True, li)

def getVideoListItem(video_id):
    li = xbmcgui.ListItem()

    adaptive_addon = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.adaptive", "properties": ["enabled", "version"]}}')
    adaptive_addon = json.loads(adaptive_addon)
    if playmethod == '0' and 'error' not in adaptive_addon.keys() and adaptive_addon['result']['addon']['enabled'] == True:
        li.setPath(VIDEO_URL_DASH.format(video_id=video_id) + "|" + USER_AGENT)
        li.setMimeType('application/dash+xml')
        li.setProperty("inputstream.adaptive.manifest_type", "mpd")
        li.setProperty('inputstreamaddon', 'inputstream.adaptive')
    else:
        url = VIDEO_URL_HSL.format(video_id=video_id)
        response = requests.get(url)

        if response.status_code == 200:
            maxbandwith = int(addon.getSetting('maxbandwith'))
            maxresolution = int(addon.getSetting('maxresolution').replace('p', ''))

            matches = re.findall("BANDWIDTH=(\d*).*RESOLUTION=\d*x(\d*)\s*(.*)", response.text)
            if matches:
                resolutions = [360, 480, 720, 1080, 0]
                for m_bandwidth, m_resolution, m_url in matches:
                    if (maxbandwith == 0 or int(m_bandwidth) <= maxbandwith) and (resolutions[maxresolution] == 0 or int(m_resolution) <= resolutions[maxresolution]):
                        url = m_url

            response.close()

        li.setPath(url + "|" + USER_AGENT)

    return li

if __name__ == '__main__':
    if 'action' in params:

        xbmc.log("params = " + str(params))

        if params.get('action') == 'listSubnavi':
            listSubnavi(params.get('path'), params.get('hasitems'))
        elif params.get('action') == 'showVideos':
            showVideos(params.get('path'), params.get('show_videos'))
        elif params.get('action') == 'playVideo':
            playVideo(params.get('path'))
    else:
        rootDir()
