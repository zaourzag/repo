# -*- coding: utf-8 -*-
import api
import gui
import urllib
import sys


def play(**kwargs):
    import xbmcaddon
    addon = xbmcaddon.Addon(id='plugin.video.ran_de')
    height = (234, 270, 396, 480, 540, 720)[int(addon.getSetting('video.quality'))]
    resource = urllib.unquote_plus(kwargs['resource'])
    video=api.get_video_url(resource, height)
    if not video=="":
     gui.play(video)


def videos(**kwargs):
    resource = urllib.unquote_plus(kwargs['resource'])
    reliveOnly = kwargs['reliveOnly']
    api.list_videos(resource, reliveOnly)


def index():
    import thumbnails
    live_caption = api.get_number_livestreams()
    if live_caption:
        live_caption = '[B]Live (%s)[/B]' % live_caption
    else:
        live_caption = 'Live (%s)' % live_caption
    gui.add_folder(live_caption, thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/livestreams.json', 'reliveOnly': False}, 'aktuelle Live Streams')
    gui.add_folder('Neueste Videos', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos.json', 'reliveOnly': False}, 'Liste der neuesten Videos - über alle Kategorien')
    gui.add_folder('Neueste Videos - [COLOR blue] Re-Live only [/COLOR]', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos.json', 'reliveOnly': True}, 'Liste der neuesten Re-Lives - über alle Kategorien')
    gui.add_folder('Fussball', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/fussball.json', 'reliveOnly': False}, 'Liste der neuesten Fussball-Videos')
    gui.add_folder('Tennis', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/tennis.json', 'reliveOnly': False}, 'Liste der neuesten Tennis-Videos')
    gui.add_folder('US-Sports', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/us-sport.json', 'reliveOnly': False}, 'Liste der neuesten US-Sport-Videos (NBA, NFL, NHL)')
    gui.add_folder('US-Sports: [COLOR blue] Re-Live only [/COLOR]', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/us-sport.json', 'reliveOnly': True}, 'Liste der neuesten Re-Live-Videos des US-Sports auf ran.de (NBA, NFL, NHL)')
    gui.add_folder('Boxen', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/boxen.json', 'reliveOnly': False}, 'Liste der neuesten Box-Videos')
    gui.add_folder('Golf', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/golf.json', 'reliveOnly': False}, 'Liste der neuesten Golf-Videos')
    gui.end_listing()


d = dict(p.split('=') for p in sys.argv[2][1:].split('&') if len(p.split('=')) == 2)
f = d.pop('f', 'index')
exec '%s(**d)' % f
