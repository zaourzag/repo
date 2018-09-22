# -*- coding: utf-8 -*-

import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
	from urllib import unquote, unquote_plus  # Python 2.X
elif PY3:
	from urllib.parse import unquote, unquote_plus   # Python 3+
from . import api
from . import gui


def index():
	api.list_series()


def cluster(url):
	api.list_cluster(url)


def episodes(url):
	api.list_episodes(url)


def following_page(url):
	url = unquote(url)
	cluster(url)


def collect_video_parts(url, photo):
	import xbmcaddon
	addon = xbmcaddon.Addon()
	if addon.getSetting('play_technique') == "2":
		ASSEMBLY = api.get_video_url(url, photo)
		gui.play_playlist(ASSEMBLY)
	else:
		ASSEMBLY = api.get_video_url(url, photo)
		gui.play_standard(ASSEMBLY)


def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict


params = parameters_string_to_dict(sys.argv[2])
mode = unquote_plus(params.get('mode', ''))
url = unquote_plus(params.get('url', ''))
photo = unquote_plus(params.get('photo', ''))


if mode == 'cluster':
	cluster(url)
elif mode == 'episodes':
	episodes(url)
elif mode == 'following_page':
	following_page(url)
elif mode == 'collect_video_parts':
	collect_video_parts(url, photo)
else:
	index()
