# -*- coding: utf-8 -*-
import api
import sys
import urllib


def play(**kwargs):
    import gui
    import xbmcaddon
    addon = xbmcaddon.Addon(id='plugin.video.atv_at')
    protocol = ('http', 'rtsp')[int(addon.getSetting('protocol'))]
    if addon.getSetting('video.as_playlist') == 'true':
        playlist = api.get_playlist(urllib.unquote(kwargs['url']), protocol)
        gui.play_playlist(playlist)
    else:
        gui.play(api.get_video_url(urllib.unquote(kwargs['url']), protocol))


def cluster(**kwargs):
    api.list_cluster(urllib.unquote(kwargs['url']))


def index():
    api.list_clusters()


def videos(**kwargs):
    api.list_videos(urllib.unquote(kwargs['url']))


def more(**kwargs):
    kwargs['url'] = urllib.unquote(kwargs['url'])
    cluster(**kwargs)


d = dict(p.split('=') for p in sys.argv[2][1:].split('&') if len(p.split('=')) == 2)
f = d.pop('f', 'index')
exec '%s(**d)' % f
