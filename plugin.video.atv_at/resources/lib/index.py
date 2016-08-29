# -*- coding: utf-8 -*-
import api
import sys
import urllib


def play(**kwargs):
    import gui
    playlist = api.get_playlist(urllib.unquote(kwargs['url']))
    gui.play_playlist(playlist)


def cluster(**kwargs):
    api.list_cluster(urllib.unquote(kwargs['url']))


def index():
    api.list_clusters()


d = dict(p.split('=') for p in sys.argv[2][1:].split('&') if len(p.split('=')) == 2)
f = d.pop('f', 'index')
exec '%s(**d)' % f
