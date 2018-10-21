#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
	from urllib import quote, unquote, quote_plus, unquote_plus, urlencode  # Python 2.X
	from urllib2 import build_opener, HTTPCookieProcessor, Request, urlopen  # Python 2.X
	from cookielib import LWPCookieJar  # Python 2.X
	from urlparse import urljoin, urlparse, urlunparse  # Python 2.X
	try:
		import StorageServer
	except:
		from resources.lib import storageserverdummy as StorageServer
elif PY3:
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse  # Python 3+
	from urllib.request import build_opener, HTTPCookieProcessor, Request, urlopen  # Python 3+
	from http.cookiejar import LWPCookieJar  # Python 3+
import json
import xbmcvfs
import shutil
import socket
import time
from datetime import date,datetime,timedelta
from bs4 import BeautifulSoup
import io
import gzip

# Setting Variablen Des Plugins
global debuging
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
temp        = xbmc.translatePath(os.path.join(dataPath, 'temp', '')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg')
icon = os.path.join(addonPath, 'icon.png')
pic = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
enableInputstream = addon.getSetting("inputstream") == "true"
prefSTREAM = addon.getSetting("streamSelection")
prefQUALITY = {0: 'hd720', 1: 'mediumlarge', 2: 'medium', 3: 'small'}[int(addon.getSetting('prefVideoQuality'))]
if PY2:
	cachePERIOD = int(addon.getSetting("cacheTime"))*24
	cache = StorageServer.StorageServer(addon.getAddonInfo('id'), cachePERIOD) # (Your plugin name, Cache time in hours)
baseURL = "http://3plus.tv"

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

if xbmcvfs.exists(temp) and os.path.isdir(temp):
	shutil.rmtree(temp, ignore_errors=True)
xbmcvfs.mkdirs(temp)
cookie = os.path.join(temp, 'cookie.lwp')
cj = LWPCookieJar()

if xbmcvfs.exists(cookie):
	cj.load(cookie, ignore_discard=True, ignore_expires=True)

def py2_enc(s, encoding='utf-8'):
	if PY2 and isinstance(s, unicode):
		s = s.encode(encoding)
	return s

def py2_uni(s, encoding='utf-8'):
	if PY2 and isinstance(s, str):
		s = unicode(s, encoding)
	return s

def py3_dec(d, encoding='utf-8'):
	if PY3 and isinstance(d, bytes):
		d = d.decode(encoding)
	return d

def translation(id):
	LANGUAGE = addon.getLocalizedString(id)
	LANGUAGE = py2_enc(LANGUAGE)
	return LANGUAGE

def failing(content):
	log(content, xbmc.LOGERROR)

def debug(content):
	log(content, xbmc.LOGDEBUG)

def log(msg, level=xbmc.LOGNOTICE):
	msg = py2_enc(msg)
	xbmc.log("["+addon.getAddonInfo('id')+"-"+addon.getAddonInfo('version')+"]"+msg, level)

def makeREQUEST(url):
	if PY2:
		INQUIRE = cache.cacheFunction(getUrl, url)
	elif PY3:
		INQUIRE = getUrl(url)
	return INQUIRE

def getUrl(url, header=None, referer=None):
	global cj
	for cook in cj:
		debug("(getUrl) COOKIE : {0}".format(str(cook)))
	pos = 0
	opener = build_opener(HTTPCookieProcessor(cj))
	try:
		if header:
			opener.addheaders = header
		else:
			opener.addheaders =[('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0')]
			opener.addheaders = [('Accept-Encoding', 'gzip, deflate')]
		if referer:
			opener.addheaders = [('Referer', referer)]
		response = opener.open(url, timeout=40)
		if response.info().get('Content-Encoding') == 'gzip':
			content = py3_dec(gzip.GzipFile(fileobj=io.BytesIO(response.read())).read())
		else:
			content = py3_dec(response.read())
	except Exception as e:
		failure = str(e)
		if hasattr(e, 'code'):
			failing("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
			xbmcgui.Dialog().notification((translation(30521).format('URL')), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 15000)
		elif hasattr(e, 'reason'):
			failing("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
			xbmcgui.Dialog().notification((translation(30521).format('URL')), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 15000)
		content = ""
		return sys.exit(0)
	opener.close()
	cj.save(cookie, ignore_discard=True, ignore_expires=True)
	return content

def clearCache():
	if PY2:
		debug("Clear Cache")
		cache.delete("%")
		xbmc.sleep(2000)
		xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30501))
	elif PY3:
		Python_Version = str(sys.version).split(')')[0].strip()+")"
		xbmcgui.Dialog().ok(addon.getAddonInfo('id'), (translation(30502).format(Python_Version)))
		pass

def ADDON_operate(INPUT_STREAM):
	js_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.GetAddonDetails", "params": {"addonid":"'+INPUT_STREAM+'", "properties": ["enabled"]}, "id":1}')
	if '"enabled":false' in js_query:
		try:
			xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": {"addonid":"'+INPUT_STREAM+'", "enabled":true}, "id":1}')
			failing("(ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *inputstream.adaptive* ist NICHT aktiviert !!! #####\n##### Es wird jetzt versucht die Aktivierung durchzuführen !!! #####")
		except: pass
	if '"error":' in js_query:
		xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30503))
		failing("(ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *inputstream.adaptive* ist NICHT installiert !!! #####\n##### Bitte KODI-Krypton (Version 17 oder höher) installieren, Diese enthalten das erforderliche Addon im Setup !!! #####")
		return False
	if '"enabled":true' in js_query:
		return True

def index():
	addDir(translation(30601), baseURL+"/videos", "listSeries", icon)
	addDir(translation(30602), "", "aSettings", icon)
	if enableInputstream:
		if ADDON_operate('inputstream.adaptive'):
			addDir(translation(30603), "", "iSettings", icon)
		else:
			addon.setSetting("inputstream", "false")
	xbmcplugin.endOfDirectory(pluginhandle)

def listSeries(url):
	xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
	un_WANTED = ['free-tv', 'jubiläumsfilm', 'trailer', 'weihnachtsüber']
	html = makeREQUEST(url) 
	content = html[html.find('class="view view-videos view-id-videos view-display-id-block_8 view-dom-id-4"')+1:]
	content = content[:content.find('</div>')]
	series = re.findall('<a href="(.*?)">(.*?)</a>', content, re.DOTALL)
	for link, name in series:
		debug("------")
		url = baseURL+link
		debug("(listSeries) ##### SeriesURL : "+url+" #####")
		name = py2_enc(name).replace('&amp;', '&')
		photo = pic+link.lower().split('videos/')[1]+'.jpg'
		if not any(x in name.lower() for x in un_WANTED):
			addDir(name, url, "listSeasons", photo)
	xbmcplugin.endOfDirectory(pluginhandle)

def listSeasons(url):
	xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
	un_WANTED = ['aufruf', 'talk', 'trailer']
	content = makeREQUEST(url)
	htmlPage = BeautifulSoup(content, "html.parser")
	seasons = htmlPage.find_all("div", {"class": "views-field-title-1"})
	for item in seasons:
		debug("------")
		linkhtml = item.find("a")
		link = baseURL+linkhtml["href"]
		debug("(listSeasons) ##### Seasons_1-Url : "+link+" #####")
		photo = pic+linkhtml["href"].lower().split('/')[2]+'.jpg'
		name = linkhtml.get_text().strip()
		if not any(x in name.lower() for x in un_WANTED):
			addDir(name, link, "listEpisodes", photo)
	xbmcplugin.endOfDirectory(pluginhandle)

def listEpisodes(name, url):
	pos = 0
	videoIsolated = set()
	myList = []
	imgCODE = ['aufruf', 'artboard', '_rz_', '_sn_', 'snippets', 'standphoto', 'web']
	wanted = ['big pictures', 'episode', 'folge', 'vorstellung', 'zur alten', ' (']
	un_WANTED = ['anmelden', 'aufruf', 'highlights', 'talk', 'teaser', 'trailer']
	content2 = makeREQUEST(url)
	htmlPage2 = BeautifulSoup(content2, "html.parser")
	seasons2 = htmlPage2.find_all("div", {"class": "views-field-title-1"})
	if seasons2:
		for item in seasons2:
			debug("------")
			linkhtml2 = item.find("a")
			link2 = baseURL+linkhtml2["href"]
			debug("(listEpisodes) ##### Seasons_2-Url : "+link2+" #####")
			title2 = linkhtml2.get_text().strip()
			myList.append([title2, link2])
	else:
		link2 = url
		title2 = name
		myList.append([title2, link2])
	for title2, link2 in myList:
		result = makeREQUEST(link2)
		webPage = BeautifulSoup(result, "html.parser")
		subhtml = webPage.find("div", {"id": "video_list_placeholder"})
		episodes = subhtml.find_all("li", {"class": "views-row"})
		for element in episodes:
			debug("(listEpisodes) ##### ELEMENT : "+str(element)+" #####")
			token_zone = element.find("div", {"class": "views-field-field-threeq-value"})
			debug("(listEpisodes) ##### TOKEN_ZONE : "+str(token_zone)+" #####")
			token = token_zone.find("div", {"class": "field-content"}).get_text().strip()
			debug("(listEpisodes) ##### TOKEN : "+token+" #####")
			if token == "":
				continue
			name_zone = element.find("div", {"class": "views-field-title"})
			name = name_zone.find("div", {"class": "field-content"}).get_text().strip()
			name = py2_enc(name).replace("3+ ", "").strip()
			if not any(x in name.lower() for x in un_WANTED):
				pos += 1
			photo = element.find("img")["src"]
			photo = photo.replace("/imagecache/playlist_video", "").replace("/imagecache/playlist_big", "")
			#photo = photo.replace("/playlist_", "/frontpage_")
			if any(p in photo.lower() for p in imgCODE) and not any(q in photo.lower() for q in wanted) and not any(y in name.lower() for y in wanted):
				debug("(listEpisodes) ##### PHOTO (not wanted)  : "+photo+" #####")
				continue
			if name in videoIsolated:
				debug("(listEpisodes) ##### NAME (double deleted) : "+name+" #####")
				continue
			videoIsolated.add(name)
			if (pos > 0 and not any(x in name.lower() for x in un_WANTED) and any(y in name.lower() for y in wanted)):
				addLink(name, token, "playVideo", photo)
			elif (pos > 0 and not any(x in name.lower() for x in un_WANTED) and not any(y in name.lower() for y in wanted)):
				addLink(name, token, "playVideo", photo)
			elif pos == 0:
				addLink(name, token, "playVideo", photo)
	xbmcplugin.endOfDirectory(pluginhandle)

def playVideo(token1):
	headerfields = "User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
	QUALITIES = ['hd720', 'mediumlarge', 'medium', 'small']
	DATA = {}
	DATA['media'] = []
	RESERVE = {}
	RESERVE['media'] = []
	finalURL = False
	streamTYPE = False
	# firstUrl = http://playout.3qsdn.com/7b26f470-e224-11e6-a78b-0cc47a188158?timestamp=0&autoplay=false&key=0&js=true&container=sdnPlayer&width=100%&height=100%&protocol=http&vastid=0&playlistbar=false
	firstUrl = "http://playout.3qsdn.com/"+token1+"?timestamp=0&key=0&js=true&container=sdnPlayer&width=100%&height=100%&protocol=http&vastid=0&wmode=direct&preload=true&amp=false"
	ref1 = "http://playout.3qsdn.com/"+token1
	content1 = getUrl(firstUrl, referer=ref1)
	debug("(playVideo) ##### firstURL : "+firstUrl+" #####")
	content1 = cleanSymbols(content1)
	videos1 = re.compile("{src:'(.+?)', type: '(.+?)', quality: '(.+?)'", re.DOTALL).findall(content1) 
	for found in QUALITIES:
		for vid, type, quality in videos1:
			if (type == "application/vnd.apple.mpegURL" or type == "application/x-mpegurl" or type== "video/mp4") and quality == found:
				DATA['media'].append({'url': vid, 'mimeType': type, 'standard': quality})
				debug("(playVideo) listing1_DATA[media] ### standard : "+quality+" ### url : "+vid+" ### mimeType : "+type+" ###")
	if DATA['media']:
		for found in QUALITIES:
			for item in DATA['media']:
				if enableInputstream:
					if ADDON_operate('inputstream.adaptive'):
						if item['mimeType'].lower() == 'application/vnd.apple.mpegurl' and item['standard'].lower() == found:
							finalURL = item['url']
							streamTYPE = 'HLS'
							debug("(playVideo) listing1_HLS ### standard : "+item['standard']+" ### finalURL : "+finalURL+" ### mimeType : "+item['mimeType']+" ### streamTYPE : "+streamTYPE+" ###")
					else:
						addon.setSetting("inputstream", "false")
				if not enableInputstream and prefSTREAM == "0" and item['mimeType'].lower() == 'application/x-mpegurl' and item['standard'].lower() == found:
					finalURL = item['url']
					streamTYPE = 'M3U8'
					debug("(playVideo) listing1_M3U8 ### standard : "+item['standard']+" ### finalURL : "+finalURL+" ### mimeType : "+item['mimeType']+" ### streamTYPE : "+streamTYPE+" ###")
				if not enableInputstream and prefSTREAM == "1" and item['mimeType'].lower() == 'video/mp4' and item['standard'].lower() == prefQUALITY:
					finalURL = item['url']
					streamTYPE = 'MP4'
					debug("(playVideo) listing1_MP4 ### standard : "+item['standard']+" ### finalURL : "+finalURL+" ### mimeType : "+item['mimeType']+" ### streamTYPE : "+streamTYPE+" ###")
	if not finalURL and DATA['media']:
		for found in QUALITIES:
			for item in DATA['media']:
				if item['mimeType'].lower() == 'video/mp4' and item['standard'].lower() == found:
					RESERVE['media'].append({'url': item['url'], 'mimeType': item['mimeType'], 'standard': item['standard']})
		finalURL = RESERVE['media'][0]['url']
		streamTYPE = 'MP4'
		debug("(playVideo) listing1_Reserve_MP4 ### standard : "+RESERVE['media'][0]['standard']+" ### finalURL : "+finalURL+" ### mimeType : "+RESERVE['media'][0]['mimeType']+" ### streamTYPE : "+streamTYPE+" ###")
	if not finalURL and not streamTYPE:
		token2 = re.compile("sdnPlayoutId:'(.+?)'", re.DOTALL).findall(content1)[0]
		# secondUrl =  http://playout.3qsdn.com/0702727c-0d5d-11e7-a78b-0cc47a188158?timestamp=0&key=0&js=true&autoplay=false&container=sdnPlayer_player&width=100%25&height=100%25&protocol=http&token=0&vastid=0&jscallback=sdnPlaylistBridge
		secondUrl = "http://playout.3qsdn.com/"+token2+"?timestamp=0&key=0&js=true&autoplay=false&container=sdnPlayer_player&width=100%25&height=100%25&protocol=http&token=0&vastid=0&jscallback=sdnPlaylistBridge"
		ref2 = "http://playout.3qsdn.com/"+token2
		content2 = getUrl(secondUrl, referer=ref2)
		debug("(playVideo) ##### secondURL : "+secondUrl+" #####")
		content2 = cleanSymbols(content2)
		videos2 = re.compile("{src:'(.+?)', type: '(.+?)', quality: '(.+?)'", re.DOTALL).findall(content2)
		for found in QUALITIES:
			for vid, type, quality in videos2:
				if (type == "application/vnd.apple.mpegURL" or type == "application/x-mpegurl" or type== "video/mp4") and quality == found:
					DATA['media'].append({'url': vid, 'mimeType': type, 'standard': quality})
					debug("(playVideo) listing2_DATA[media] ### standard : "+quality+" ### url : "+vid+" ### mimeType : "+type+" ###")
		if DATA['media']:
			for found in QUALITIES:
				for item in DATA['media']:
					if enableInputstream:
						if ADDON_operate('inputstream.adaptive'):
							if item['mimeType'].lower() == 'application/vnd.apple.mpegurl' and item['standard'].lower() == found:
								finalURL = item['url']
								streamTYPE = 'HLS'
								debug("(playVideo) listing2_HLS ### standard : "+item['standard']+" ### finalURL : "+finalURL+" ### mimeType : "+item['mimeType']+" ### streamTYPE : "+streamTYPE+" ###")
						else:
							addon.setSetting("inputstream", "false")
					if not enableInputstream and prefSTREAM == "0" and item['mimeType'].lower() == 'application/x-mpegurl' and item['standard'].lower() == found:
						finalURL = item['url']
						streamTYPE = 'M3U8'
						debug("(playVideo) listing2_M3U8 ### standard : "+item['standard']+" ### finalURL : "+finalURL+" ### mimeType : "+item['mimeType']+" ### streamTYPE : "+streamTYPE+" ###")
					if not enableInputstream and prefSTREAM == "1" and item['mimeType'].lower() == 'video/mp4' and item['standard'].lower() == prefQUALITY:
						finalURL = item['url']
						streamTYPE = 'MP4'
						debug("(playVideo) listing2_MP4 ### standard : "+item['standard']+" ### finalURL : "+finalURL+" ### mimeType : "+item['mimeType']+" ### streamTYPE : "+streamTYPE+" ###")
	if not finalURL and DATA['media']:
		for found in QUALITIES:
			for item in DATA['media']:
				if item['mimeType'].lower() == 'video/mp4' and item['standard'].lower() == found:
					RESERVE['media'].append({'url': item['url'], 'mimeType': item['mimeType'], 'standard': item['standard']})
		finalURL = RESERVE['media'][0]['url']
		streamTYPE = 'MP4'
		debug("(playVideo) listing2_Reserve_MP4 ### standard : "+RESERVE['media'][0]['standard']+" ### finalURL : "+finalURL+" ### mimeType : "+RESERVE['media'][0]['mimeType']+" ### streamTYPE : "+streamTYPE+" ###")
	if finalURL and streamTYPE:
		if streamTYPE == 'M3U8':
			log("(playVideo) M3U8_stream : {0}".format(finalURL))
			finalURL = finalURL.split(".m3u8")[0]+".m3u8"
		if streamTYPE == 'MP4':
			log("(playVideo) MP4_stream : {0}".format(finalURL))
			finalURL = finalURL.split(".mp4")[0]+".mp4"
		listitem = xbmcgui.ListItem(path=finalURL)
		if streamTYPE == 'HLS':
			log("(playVideo) HLS_stream : {0}".format(finalURL))
			listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
			listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
			listitem.setMimeType('application/vnd.apple.mpegurl')
		listitem.setContentLookup(False)
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	else: 
		failing("(playVideo) ##### Abspielen des Videos NICHT möglich - URL : {0} - #####\n    ########## KEINEN Stream-Eintrag auf der Webseite von *3plus.tv* gefunden !!! ##########".format(url))
		xbmcgui.Dialog().notification((translation(30521).format('PLAY')), translation(30523), icon, 8000)

def cleanSymbols(s):
	s = s.replace('\\x2A', '*').replace('\\x2B', '+').replace('\\x2D', '-').replace('\\x2E', '.').replace('\\x2F', '/').replace('\\x5F', '_')
	s = s.replace('\\u002A', '*').replace('\\u002B', '+').replace('\\u002D', '-').replace('\\u002E', '.').replace('\\u002F', '/').replace('\\u005F', '_')
	s = s.replace('\/', '/')
	return s

def addVideoList(url, name, image):
	PL = xbmc.PlayList(1)
	listitem = xbmcgui.ListItem(name, thumbnailImage=image)
	listitem.setInfo(type="Video", infoLabels={"Title": name, "Studio": "3plus.TV", "mediatype": "video"})
	listitem.setProperty('IsPlayable', 'true')
	listitem.setContentLookup(False)
	PL.add(url, listitem)

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split("=")
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def addDir(name, url, mode, image, plot=None, page=1, nosub=0):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&nosub="+str(nosub)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
	liz.setArt({'fanart': image})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  
def addLink(name, url, mode, image, plot=None, duration=None, genre=None, director=None, studio=None, date=None):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Duration": duration, "Genre": "Unterhaltung", "Director": director, "Studio": "3plus.TV"})
	liz.setArt({'fanart': defaultFanart})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
	liz.addContextMenuItems([(translation(30654), 'RunPlugin(plugin://{0}?mode=addVideoList&url={1}&name={2}&image={3}'.format(addon.getAddonInfo('id'), quote_plus(u), quote_plus(name), quote_plus(image)))])
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
image = unquote_plus(params.get('image', ''))
referer = unquote_plus(params.get('referer', ''))
page= unquote_plus(params.get('page', ''))
nosub= unquote_plus(params.get('nosub', ''))

if mode == 'aSettings':
	addon.openSettings()
elif mode == 'iSettings':
	xbmcaddon.Addon('inputstream.adaptive').openSettings()
elif mode == 'clearCache':
	clearCache()
elif mode == 'listSeries':
	listSeries(url)
elif mode == 'listSeasons':
	listSeasons(url)
elif mode == 'listEpisodes':
	listEpisodes(name, url)
elif mode == 'playVideo':
	playVideo(url)
elif mode == 'addVideoList':
	addVideoList(url, name, image)
else:
	index()