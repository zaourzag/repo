import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import urlparse
import urllib
import resources.lib.common as common
import base64
import struct

import maxdome as maxdome

addon_handle = int(sys.argv[1])
plugin_base_url = sys.argv[0]
params = dict(urlparse.parse_qsl(sys.argv[2][1:]))
addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()

base_url = "plugin://" + xbmcaddon.Addon().getAddonInfo('id')
cookie_path = xbmc.translatePath(addon.getAddonInfo('profile')) + 'COOKIES'
username = addon.getSetting('email')
password = addon.getSetting('password')

mas = maxdome.MaxdomeSession(username, password, cookie_path)
#xbmc.log("MAXDOME PREFERENCES: " + mas.getPreferences())

def rootDir():
	url = common.build_url({'action': 'list', 'page': 'movies'})
	li = xbmcgui.ListItem('Filme')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
								listitem=li, isFolder=True)	
	url = common.build_url({'action': 'list', 'page': 'series'})
	li = xbmcgui.ListItem('Serien')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
								listitem=li, isFolder=True)
	url = common.build_url({'action': 'list', 'page': 'kids'})
	li = xbmcgui.ListItem('Kids')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
								listitem=li, isFolder=True)
	url = common.build_url({'action': 'list', 'url': '/mein-account/merkzettel'})
	li = xbmcgui.ListItem('Merkzettel')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
								listitem=li, isFolder=True)
	url = common.build_url({'action': 'list', 'page': 'boughtAssets'})
	li = xbmcgui.ListItem('Gekaufte Videos')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
								listitem=li, isFolder=True)
	url = common.build_url({'action': 'list', 'page': 'rentAssets'})
	li = xbmcgui.ListItem('Geliehene Videos')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
								listitem=li, isFolder=True)
	url = common.build_url({'action': 'search'})
	li = xbmcgui.ListItem('Suche')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
								listitem=li, isFolder=True)

	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

def listDir(listitems):
	action = ''
	url = ''
	isfolder = True
	for item in listitems:
		li = xbmcgui.ListItem(item.keys()[0])
		if str(item.values()[0]).startswith('/'):
			url = common.build_url({'action': 'list', 'url': item.values()[0]})

		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
									listitem=li, isFolder=isfolder)

	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

def getInfoItem(assetid):
	asset_info = mas.Assets.getAssetInformation(assetid)
	if asset_info['@class'] == 'AssetVideoFilmTvSeries':
		info = { 'mediatype': 'episode', 'title': asset_info['episodeTitle'], 'tvshowtitle': asset_info['title'], 'episode': asset_info['episodeNumber'], 'season': asset_info['seasonNumber'], 'plot': asset_info['descriptionLong'] }
		return info
	elif asset_info['@class'] == 'AssetVideoFilm':
		info = { 'mediatype': 'movie', 'title': asset_info['title'], 'plot': asset_info['descriptionLong'] }
		return info

	return { 'mediatype': 'movie' }

def play(assetid):	
#	mas.play(assetid)
	mas.Assets.orderAsset(assetid)

	li = xbmcgui.ListItem(path=mas.video_url)
	info = getInfoItem(assetid)
	li.setInfo('video', info)
	li.setProperty('inputstream.mpd.license_type', 'com.widevine.alpha')
	li.setProperty('inputstream.mpd.license_key', mas.license_url)
	li.setProperty('inputstreamaddon', 'inputstream.mpd')

	xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)

def listAssets(assets):
	xbmcplugin.setContent(addon_handle, 'movies')
	for item in assets:
		url = ''
		playable = False
		li = xbmcgui.ListItem(item['title'])
		if 'poster' in item.keys():
			li.setArt({'poster': item['poster']})
		if (item['class'] == 'assetVideoFilm') or (item['class'] == 'assetVideoFilmTvSeries') or (item['class'] == 'MultiAssetTvSeriesSeason'):
			playable = True
			li.setProperty('IsPlayable', 'true')
			info = { 'mediatype': 'movie', 'title': item['title'] }
			li.setInfo('video', info)
			url = common.build_url({'action': 'play', 'assetid': item['id']})
		else:
			playable = False
			url = common.build_url({'action': 'list', 'assetid': item['id']})

		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
									listitem=li, isFolder=(not playable))

	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

# Router for all plugin actions
if params:
	print params
	if params['action'] == 'list':
		if 'page' in params:
			if params['page'] == 'movies':
				listDir(mas.Assets.getMoviesCategories())
			elif params['page'] == 'series':
				listDir(mas.Assets.getSeriesCategories())
			elif params['page'] == 'kids':
				listDir(mas.Assets.getKidsCategories())
			elif params['page'] == 'boughtAssets':
				listAssets(mas.Assets.getBoughtAssets())
			elif params['page'] == 'rentAssets':
				listAssets(mas.Assets.getRentAssets())
		elif 'url' in params:
			path = params['url']
			listAssets(mas.Assets.parseHtmlAssets(path))
		elif 'assetid' in params:
			assetid = params['assetid']
			listAssets(mas.Assets.parseAsset(assetid))
	elif params['action'] == 'search':
		dlg = xbmcgui.Dialog()
		term = dlg.input('Suchbegriff', type=xbmcgui.INPUT_ALPHANUM)
		listAssets(mas.Assets.searchAssets(term))
	elif params['action'] == 'play':
		if 'assetid' in params:
			assetid = params['assetid']
			play(assetid)
else:
	rootDir()


