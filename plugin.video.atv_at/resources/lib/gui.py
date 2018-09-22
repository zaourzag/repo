# -*- coding: utf-8 -*-

import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import socket
import time
import requests
try:
	from requests.packages.urllib3.exceptions import InsecureRequestWarning
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except: pass
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
	from urllib import urlencode # Python 2.X
	from HTMLParser import HTMLParser  # Python 2.X
	try:
		import StorageServer
	except ImportError:
		from . import storageserverdummy as StorageServer
elif PY3:
	from urllib.parse import urlencode  # Python 3+
	from html.parser import HTMLParser  # Python 3+


HOST_AND_PATH = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])
addon = xbmcaddon.Addon()
socket.setdefaulttimeout(30)
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg')
icon = os.path.join(addonPath, 'icon.png')
if PY2:
	cachePERIOD = int(addon.getSetting("cacheTime"))*24
	cache = StorageServer.StorageServer(addon.getAddonInfo('id'), cachePERIOD) # (Your plugin name, Cache time in hours)


__HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Encoding': 'gzip, deflate','Connection': 'keep-alive','Upgrade-Insecure-Requests': '1'}
headerFIELDS = "User-Agent=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F67.0.3396.62%20Safari%2F537.36"


xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')


def py2_encode(s, encoding='utf-8'):
	if PY2 and isinstance(s, unicode):
		s = s.encode(encoding)
	return s


def cleanupTEXT(input):
	input = input.replace("  ", " ").encode('utf-8').decode('utf-8')
	return HTMLParser().unescape(input)


def translation(id):
	LANGUAGE = addon.getLocalizedString(id)
	LANGUAGE = py2_encode(LANGUAGE)
	return LANGUAGE


def debug(content):
	if addon.getSetting("enableDebug") == 'true':
		log(content, xbmc.LOGNOTICE)


def log(msg, level=xbmc.LOGNOTICE):
	msg = py2_encode(msg)
	xbmc.log("["+addon.getAddonInfo('id')+"-"+addon.getAddonInfo('version')+"]"+msg, level)


def makeREQUEST(url):
	if PY2:
		INQUIRE = cache.cacheFunction(getUrl, url, "GET", False, False, __HEADERS)
	elif PY3:
		INQUIRE = getUrl(url, "GET", False, False, __HEADERS)
	return INQUIRE


def getUrl(url, method, allow_redirects=False, verify=False, headers="", data="", timeout=30):
	response = requests.Session()
	if method=="GET":
		content = response.get(url, allow_redirects=allow_redirects, verify=verify, headers=headers, data=data, timeout=timeout).text
	elif method=="POST":
		content = response.post(url, data=data, allow_redirects=allow_redirects, verify=verify).text
	return content


def end_listing():
	xbmcplugin.endOfDirectory(ADDON_HANDLE)


def add_folder(title, thumb, url_params, context_menu_items=None):
	url = '%s?%s' % (HOST_AND_PATH, urlencode(url_params))
	liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
	if thumb != icon:
		liz.setArt({'fanart': thumb})
	else:
		liz.setArt({'fanart': defaultFanart})
	if context_menu_items is not None:
		liz.addContextMenuItems(context_menu_items)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=liz, isFolder=True)


def add_video(title, tvshowtitle=None, season=None, episode=None, plot=None, thumb=None, url_params=None, duration=None, context_menu_items=None, subtitle_list=None):
	"""
	Callback function to pass directory contents back to XBMC as a list.
	:param title: primary title of video
	:param thumb: path to thumbnail
	:param url_params: dictionary of url parameters
	:param video_info_labels: {
			genre: string (Comedy)
			year: integer (2009)
			episode: integer (4) ...
		}
	:param fanart: path to fanart image
	:param video_url: direct url to video
	:param icon: path to icon
	:param is_playable: boolean
	:param context_menu_items: [('title', 'xbmc.function')]
	:param subtitle_list: ['url to srt']
	:return: boolean for successful completion
	"""
	vidURL = '%s?%s' % (HOST_AND_PATH, urlencode(url_params))
	liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
	liz.setInfo(type="Video", infoLabels={'TVShowTitle': tvshowtitle, 'Title': title, 'Season': season, 'Episode': episode, 'Plot': plot, 'Studio': 'ATV.at', 'Genre': 'Unterhaltung', 'mediatype': 'episode'})
	liz.setProperty('IsPlayable','true')
	#liz.setContentLookup(False)
	if thumb != icon:
		liz.setArt({'fanart': thumb})
	else:
		liz.setArt({'fanart': defaultFanart})
	if duration is not None:
		liz.addStreamInfo('Video', {'Duration': duration})
	if context_menu_items is not None:
		liz.addContextMenuItems(context_menu_items)
	if subtitle_list is not None:
		try:
			liz.setSubtitles(subtitle_list)
		except AttributeError:
			pass
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=vidURL, listitem=liz)


def play_standard(ASSEMBLY):
	combined_videoURL = ""
	pos = 0
	if ASSEMBLY:
		for single_videoURL, title, NRS_title, tvshowtitle, season, episode, plot, photo, thumb, duration in ASSEMBLY:
			pos += 1
			combined_videoURL += single_videoURL+" , "
			stacked_videoURL = 'stack://'+combined_videoURL[:-3]
			liz = xbmcgui.ListItem(path=stacked_videoURL)
			liz.setInfo(type="Video", infoLabels={'TVShowTitle': tvshowtitle, 'Title': title, 'Season': season, 'Episode': episode, 'Plot': plot, 'Duration': duration, 'Studio': 'ATV.at', 'Genre': 'Unterhaltung', 'mediatype': 'episode'})
			liz.setArt({'thumb': photo, 'fanart': photo})
			if addon.getSetting('play_technique') == "0":
				liz.setMimeType("mime/x-type")
				liz.setProperty('IsPlayable','true')
				liz.setContentLookup(False)
				xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, listitem=liz)
			elif addon.getSetting('play_technique') == "1":
				liz.setMimeType("mime/x-type")
				liz.setProperty('IsPlayable','true')
				liz.setContentLookup(False)
				xbmc.Player().play(stacked_videoURL, listitem=liz)
		log("(play_standard) combined_videoURL : {0}".format(combined_videoURL))
		log("(play_standard) -------------------- Meldung: *Standard-Abspielen* in den Settings eingestellt --------------------")


def play_playlist(ASSEMBLY):
	PL = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	pos = 0
	if ASSEMBLY:
		log("(play_playlist) -------------------- Meldung: Nur *Playliste-Abspielen* in den Settings eingestellt --------------------")
		for single_videoURL, title, NRS_title, tvshowtitle, season, episode, plot, photo, thumb, duration in ASSEMBLY:
			pos += 1
			NRS_title = '[COLOR chartreuse]'+NRS_title+'[/COLOR]' # Die Hofwochen - Folge 5 1/7
			liz = xbmcgui.ListItem(title)
			liz.setInfo(type="Video", infoLabels={'TVShowTitle': tvshowtitle, 'Title': NRS_title, 'Season': season, 'Episode': episode, 'Plot': plot, 'Duration': duration, 'Studio': 'ATV.at', 'Genre': 'Unterhaltung', 'mediatype': 'episode'})
			liz.setArt({'thumb': thumb, 'fanart': thumb}) # Episode-Bild = wechselnd für jeden Videopart
			xbmc.sleep(50)
			PL.add(url=single_videoURL, listitem=liz, index=pos)
		return PL


def get_search_input(heading, default_text=''):
	keyboard = xbmc.Keyboard(default_text, heading)
	keyboard.doModal()
	if keyboard.isConfirmed():
		return keyboard.getText()
