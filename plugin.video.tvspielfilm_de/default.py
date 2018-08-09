#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    This Plugin is compatible between Python 2.X and Python 3+
    without using any extra extern Plugins from XBMC (KODI)
    Copyright (C) 2018 by realvito
    Released under GPL(v3)
"""

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
	from urllib import quote, unquote, quote_plus, unquote_plus, urlencode, urlopen  # Python 2.X
	from urllib2 import build_opener, HTTPCookieProcessor  # Python 2.X
	from cookielib import LWPCookieJar  # Python 2.X
	from urlparse import urljoin, urlparse, urlunparse  # Python 2.X
elif PY3:
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse  # Python 3+
	from urllib.request import build_opener, HTTPCookieProcessor, urlopen  # Python 3+
	from http.cookiejar import LWPCookieJar  # Python 3+
import json
import xbmcvfs
import shutil
import socket
import time
from datetime import date,datetime,timedelta
import io
import gzip

#token = 'ffc9a283b511b7e11b326fdc3d76c5559b50544e reraeB'
#getheader = {'Api-Auth': 'reraeB '+token[::-1]} = Gespiegelt
#getheader = {'Api-Auth': 'Bearer '+token} = Original

pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
temp        = xbmc.translatePath(os.path.join(dataPath, 'temp', '')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg').encode('utf-8').decode('utf-8')
icon = os.path.join(addonPath, 'icon.png').encode('utf-8').decode('utf-8')
pic = os.path.join(addonPath, 'resources/media/')
preferredStreamType = addon.getSetting("streamSelection")
showDATE = addon.getSetting("enableDatetitle") == 'true'
showTVchannel = addon.getSetting("enableChannelID") == 'true'
showNOW = addon.getSetting("enableTVnow")
enableDebug = addon.getSetting("enableDebug") == 'true'
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == 'true'
forceViewMode = addon.getSetting("forceView") == 'true'
viewMode = str(addon.getSetting("viewID"))
baseURL = "https://www.tvspielfilm.de"
dateURL = "/mediathek/nach-datum/"
ZDFapiUrl = "https://api.zdf.de"

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

def py3_dec(d, encoding='utf-8'):
	if PY3 and isinstance(d, bytes):
		d = d.decode(encoding)
	return d

def translation(id):
	LANGUAGE = addon.getLocalizedString(id)
	LANGUAGE = py2_enc(LANGUAGE)
	return LANGUAGE

def debug_MS(content):
	if enableDebug:
		log_MS(content, xbmc.LOGNOTICE)

def log_MS(msg, level=xbmc.LOGNOTICE):
	msg = py2_enc(msg)
	xbmc.log('[TV-Spielfilm]'+msg, level)

def getUrl(url, header=None, referer=None):
	global cj
	for cook in cj:
		debug_MS("(getUrl) Cookie : {0}".format(str(cook)))
	pos = 0
	opener = build_opener(HTTPCookieProcessor(cj))
	try:
		if header:
			opener.addheaders = header
		else:
			opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')]
			opener.addheaders = [('Accept-Encoding', 'gzip, deflate')]
		if referer:
			opener.addheaders = [('Referer', referer)]
		response = opener.open(url, timeout=30)
		if response.info().get('Content-Encoding') == 'gzip':
			content = py3_dec(gzip.GzipFile(fileobj=io.BytesIO(response.read())).read())
		else:
			content = py3_dec(response.read())
	except Exception as e:
		failure = str(e)
		if pos < 1 and 'SSL23_GET_SERVER_HELLO' in failure:
			pos += 1
			try:
				Python_Version = str(sys.version).split(')')[0].strip()+")"
			except:
				Python_Version = translation(30501)
			xbmcgui.Dialog().ok(addon.getAddonInfo('id'), (translation(30502).format(Python_Version)))
			log_MS("(getUrl) ERROR - ERROR - ERROR : ########## Die installierte PYTHONVERSION : *** {0} *** ist zu alt !!! ##########\n########## Bitte zu KODI-Krypton (Version 17 oder hoeher) oder -FTMC updaten !!! ##########".format(Python_Version))
		elif pos < 1 and 'getaddrinfo failed' in failure:
			pos += 1
			xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30503))
			log_MS("(getUrl) ERROR - ERROR - ERROR : ########## Es besteht ein Problem mit dem Netzwerk === {0} === ##########\n########## Entweder ist die angeforderte - WebSeite - zurzeit nicht erreichbar oder überprüfen Sie, ob Ihre Internetverbindung funktioniert ?! ##########".format(failure))
		else:
			if hasattr(e, 'code'):
				log_MS("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
			elif hasattr(e, 'reason'):
				log_MS("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
		content = ""
		return sys.exit(0)
	opener.close()
	cj.save(cookie, ignore_discard=True, ignore_expires=True)               
	return content

def index():
	s1 = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
	s2 = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
	s3 = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
	s4 = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')
	s5 = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
	m1 = (datetime.now() - timedelta(days=1)).strftime('%d.%m.%Y')
	m2 = (datetime.now() - timedelta(days=2)).strftime('%d.%m.%Y')
	m3 = (datetime.now() - timedelta(days=3)).strftime('%d.%m.%Y')
	m4 = (datetime.now() - timedelta(days=4)).strftime('%d.%m.%Y')
	m5 = (datetime.now() - timedelta(days=5)).strftime('%d.%m.%Y')
	d = m1.split('.'); w1 = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")[date(int(d[2]), int(d[1]), int(d[0])).weekday()]
	d = m2.split('.'); w2 = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")[date(int(d[2]), int(d[1]), int(d[0])).weekday()]
	d = m3.split('.'); w3 = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")[date(int(d[2]), int(d[1]), int(d[0])).weekday()]
	d = m4.split('.'); w4 = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")[date(int(d[2]), int(d[1]), int(d[0])).weekday()]
	d = m5.split('.'); w5 = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")[date(int(d[2]), int(d[1]), int(d[0])).weekday()]
	addDir("Auswahl vom "+w1+", den "+m1, baseURL+dateURL+"?date="+s1, 'listVideos_Day_Channel_Highlights', icon)
	addDir("Auswahl vom "+w2+", den "+m2, baseURL+dateURL+"?date="+s2, 'listVideos_Day_Channel_Highlights', icon)
	addDir("Auswahl vom "+w3+", den "+m3, baseURL+dateURL+"?date="+s3, 'listVideos_Day_Channel_Highlights', icon)
	addDir("Auswahl vom "+w4+", den "+m4, baseURL+dateURL+"?date="+s4, 'listVideos_Day_Channel_Highlights', icon)
	addDir("Auswahl vom "+w5+", den "+m5, baseURL+dateURL+"?date="+s5, 'listVideos_Day_Channel_Highlights', icon)
	addDir("[COLOR deepskyblue]• • • SENDER sortiert • • •[/COLOR]", baseURL+"/mediathek/nach-sender/", 'listChannel', icon)
	addDir("[COLOR deepskyblue]• • • TV-HIGHLIGHTS • • •[/COLOR]", baseURL+"/mediathek/", 'listVideos_Day_Channel_Highlights', icon)
	addDir("* Spielfilme *", "Spielfilm", 'listVideosGenre', icon)
	addDir("* Serien *", "Serie", 'listVideosGenre', icon)
	addDir("* Reportagen *", "Report", 'listVideosGenre', icon)
	addDir("* Unterhaltung *", "Unterhaltung", 'listVideosGenre', icon)
	addDir("* Kinder *", "Kinder", 'listVideosGenre', icon)
	addDir("* Sport *", "Sport", 'listVideosGenre', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def listChannel(url):
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
	html = getUrl(url)
	debug_MS("(listChannel) SENDER-SORTIERUNG : Alle Sender in TV-Spielfilm")
	if showNOW == 'true':
		debug_MS("(listChannel) --- NowTV - Sender EINGEBLENDET ---")
	else:
		debug_MS("(listChannel) --- NowTV - Sender AUSGEBLENDET ---")
	content = html[html.find('<section class="mediathek-channels">'):]
	content = content[:content.find('</section>')]
	spl = content.split('title=')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		try:
			url = re.compile(r'href=["\'](https?://.*?)["\']>', re.DOTALL).findall(entry)[0]
			channelID = url.split('channel=')[1].strip()
			channelID = cleanStation(channelID.strip())
			title = channelID.replace('(', '').replace(')', '').replace('  ', '')
			if showNOW == 'false':
				if ("RTL" in channelID or "VOX" in channelID or "SUPER" in channelID):
					continue
			debug_MS("(listChannel) Link : {0}{1}".format(url, channelID))
			addDir('[COLOR lime]'+title+'[/COLOR]', url, 'listVideos_Day_Channel_Highlights', pic+title.lower().replace(' ', '')+'.png', studio=title)
		except:
			log_MS("(listChannel) Fehler-Eintrag : {0}".format(str(entry)))
	xbmcplugin.endOfDirectory(pluginhandle)

def listVideos_Day_Channel_Highlights(url):
	html = getUrl(url)
	debug_MS("(listVideos_Day_Channel_Highlights) MEDIATHEK : {0}".format(url))
	if showNOW == 'true':
		debug_MS("(listVideos_Day_Channel_Highlights) --- NowTV - Sender EINGEBLENDET ---")
	else:
		debug_MS("(listVideos_Day_Channel_Highlights) --- NowTV - Sender AUSGEBLENDET ---")
	if "?date=" in url or "?channel=" in url:
		content = html[html.find('<section class="teaser-section">')+1:]
		content = content[:content.find('</section>')]
		spl = content.split('<div class="content-teaser')
	else:
		content = html[html.find('<div class="swiper-container"')+1:]
		content = content[:content.find('<div class="swiper-button-prev"></div>')]
		spl = content.split('<div class="swiper-slide">')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		try:
			match1 = re.compile(r'<span class=["\']headline["\']>(.*?)</span>', re.DOTALL).findall(entry)
			match2= re.compile(r'<span class=["\']subline.+?>(.*?)</span>', re.DOTALL).findall(entry)
			match3 = re.compile(r'target=["\']_self["\'] title=["\'](.*?)["\']>', re.DOTALL).findall(entry)
			if (match1[0] and not match2[0] and match3[0]):
				first = match1[0].replace('…', '').replace('...', '').strip()
				third = match3[0].replace('…', '').replace('...', '').strip()
				if first == third:
					title = cleanTitle(first)
				else:
					title = cleanTitle(first.strip())+" - "+cleanTitle(third.replace(first, "").strip())
				added = ""
				channelID = cleanTitle(url.split('/')[-1].replace('?channel=', '').strip())
				channelID = cleanStation(channelID)
				studio = channelID.replace('(', '').replace(')', '').replace('  ', '')
			elif (match1[0] and match2[0] and not match3[0]):
				title = cleanTitle(match1[0].strip())+" - "+cleanTitle(match2[0].split('|')[-1].strip())
				added = match2[0].split('|')[0].strip()
				channelID = cleanTitle(match2[0].split('|')[1].strip())
				channelID = cleanStation(channelID)
				studio = channelID.replace('(', '').replace(')', '').replace('  ', '')
			elif (match1[0] and match2[0] and match3[0]):
				first = match1[0].replace('…', '').replace('...', '').strip()
				third = match3[0].replace('…', '').replace('...', '').strip()
				if first == third:
					title = cleanTitle(first)
				else:
					testing3 = cleanTitle(third.replace(first, "").strip())
					if testing3 == "":
						title = cleanTitle(first)
					else:
						title = cleanTitle(first)+" - "+testing3
				added = match2[0].split('|')[0].strip()
				channelID = cleanTitle(match2[0].split('|')[1].strip())
				channelID = cleanStation(channelID)
				studio = channelID.replace('(', '').replace(')', '').replace('  ', '')
			if showDATE and added != "":
				title = added.strip()+"  "+title
			urlFW = re.compile(r'<a href=["\'](https?://.*?mediathek/.*?)["\']', re.DOTALL).findall(entry)[0]
			photo = re.compile(r'<img src=["\'](https?://.*?.jpg)["\']', re.DOTALL).findall(entry)[0]
			if ',' in photo:
				photo = photo.split(',')[0].rstrip()+'.jpg'
			if showTVchannel and channelID != "":
				title += channelID
			if showNOW == 'false' and channelID != "":
				if ("RTL" in channelID or "VOX" in channelID or "SUPER" in channelID):
					continue
			debug_MS("(listVideos_Day_Channel_Highlights) Name : {0}".format(title))
			debug_MS("(listVideos_Day_Channel_Highlights) Link : {0}".format(urlFW))
			debug_MS("(listVideos_Day_Channel_Highlights) Icon : {0}".format(photo))
			addLink(title, urlFW, 'playVideo', photo, studio=studio)
		except:
			log_MS("(listVideos_Day_Channel_Highlights) Fehler-Eintrag : {0}".format(str(entry)))
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listVideosGenre(category):
	html = getUrl(baseURL+"/mediathek/")
	debug_MS("(listVideosGenre) MEDIATHEK : {0}/mediathek/ - Genre = *{1}*".format(baseURL, category.upper()))
	if showNOW == 'true':
		debug_MS("(listVideosGenre) --- NowTV - Sender EINGEBLENDET ---")
	else:
		debug_MS("(listVideosGenre) --- NowTV - Sender AUSGEBLENDET ---")
	content = html[html.find('<span>'+category+'</span>')+1:]
	content = content[:content.find('<div class="scroll-box">')]
	spl = content.split('<li>')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		try:
			match1 = re.compile(r'class=["\']aholder["\'] title=["\'](.*?)["\']>', re.DOTALL).findall(entry)
			match2= re.compile('<strong>(.*?)</strong>\s+<span>(.*?)</span>', re.DOTALL).findall(entry)
			first = match1[0].strip()
			secondONE = match2[0][0].strip()
			secondTWO = match2[0][1].strip()
			if first == secondONE:
				title = cleanTitle(first)
			elif ('...' in secondONE and not '...' in secondTWO):
				title = cleanTitle(first.replace(secondTWO, "").strip())+" - "+cleanTitle(secondTWO.strip())
			elif ('...' in secondONE and '...' in secondTWO):
				title = cleanTitle(first)
			else:
				title = cleanTitle(secondONE.strip())+" - "+cleanTitle(first.replace(secondONE, "").strip())
			added = re.compile(r'<div class=["\']col["\']>(.*?)</div>', re.DOTALL).findall(entry)[0]
			if showDATE and added != "":
				title = added.strip()+"  "+title
			match3 = re.compile(r'target=["\']_self["\'] title=["\'].+?["\']>(.*?)</a>', re.DOTALL).findall(entry)
			channelID = cleanTitle(match3[0])
			channelID = cleanStation(channelID)
			studio = channelID.replace('(', '').replace(')', '').replace('  ', '')
			urlFW = re.compile(r'<a href=["\'](https?://.*?mediathek/.*?)["\']', re.DOTALL).findall(entry)[0]
			photo = re.compile(r'<img src=["\'](https?://.*?.jpg)["\']', re.DOTALL).findall(entry)[0]
			if ',' in photo:
				photo = photo.split(',')[0].rstrip()+'.jpg'
			if showTVchannel and channelID != "":
				title += channelID
			if showNOW == 'false' and channelID != "":
				if ("RTL" in channelID or "VOX" in channelID or "SUPER" in channelID):
					continue
			debug_MS("(listVideosGenre) Name : {0}".format(title))
			debug_MS("(listVideosGenre) Link : {0}".format(urlFW))
			debug_MS("(listVideosGenre) Icon : {0}".format(photo))
			addLink(title, urlFW, 'playVideo', photo, studio=studio)
		except:
			log_MS("(listVideosGenre) Fehler-Eintrag : {0}".format(str(entry)))
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playVideo(url):
	finalURL = False
	ARD_SCHEMES = ('http://www.ardmediathek.de', 'https://www.ardmediathek.de', 'http://mediathek.daserste.de', 'https://mediathek.daserste.de')
	RTL_SCHEMES = ('http://www.nowtv.de', 'https://www.nowtv.de', 'http://www.tvnow.de', 'https://www.tvnow.de')
	log_MS("(playVideo) --- START WIEDERGABE ANFORDERUNG ---")
	log_MS("(playVideo) frei")
	try:
		content = getUrl(url)
		LINK = re.compile('<header class="broadcast-detail__header">.+?<a href="([^"]+)" class="mediathek-open col-hover-thek"', re.DOTALL).findall(content)[0]
		log_MS("(playVideo) AbspielLink (Original) : {0}".format(LINK))
	except:
		log_MS("(playVideo) MediathekLink-00 : MediathekLink der Sendung in TV-Spielfilm NICHT gefunden !!!")
		xbmcgui.Dialog().notification(translation(30521), translation(30522), icon, 8000)
		LINK = ""
	log_MS("(playVideo) frei")
	if LINK.startswith("https://www.arte.tv"):
		videoID = re.compile("arte.tv/de/videos/([^/]+?)/", re.DOTALL).findall(LINK)[0]
		try:
			plugin2 = xbmcaddon.Addon(id='plugin.video.L0RE.arte')
			finalURL = 'plugin://'+plugin2.getAddonInfo('id')+'/?mode=playvideo&url='+videoID
			log_MS("(playVideo) AbspielLink-1 (ARTE-TV) : {0}".format(finalURL))
		except:
			try:
				plugin3 = xbmcaddon.Addon(id='plugin.video.arteplussept')
				finalURL = 'plugin://'+plugin3.getAddonInfo('id')+'/play/'+quote_plus(videoID)
				log_MS("(playVideo) AbspielLink-2 (ARTE-plussept) : {0}".format(finalURL))
			except:
				if finalURL:
					log_MS("(playVideo) AbspielLink-00 (ARTE) : *ARTE-Plugin* Der angeforderte -VideoLink- existiert NICHT !!!")
					xbmcgui.Dialog().notification((translation(30523).format('ARTE - Plugin')), translation(30525), icon, 8000)
				else:
					log_MS("(playVideo) AbspielLink-00 (ARTE) : KEIN *ARTE-Addon* zur Wiedergabe vorhanden !!!")
					xbmcgui.Dialog().notification((translation(30523).format('ARTE - Addon')), (translation(30524).format('ARTE-Addon')), icon, 8000)
				pass
	elif LINK.startswith(ARD_SCHEMES):
		videoID = LINK.split('documentId=')[1]
		if '&' in videoID:
			videoID = videoID.split('&')[0]
		return ArdGetVideo(videoID)
	elif LINK.startswith("https://www.zdf.de"):
		cleanURL = LINK[:LINK.find('.html')]
		videoURL = unquote_plus(cleanURL)+".html"
		return ZdfGetVideo(videoURL)
	elif LINK.startswith(RTL_SCHEMES):
		LINK = LINK.replace('http://', 'https://').replace('www.nowtv.de/', 'www.tvnow.de/').replace('list/aktuell/', '').replace('/player', '')
		videoSE = LINK.split('/')[4].strip()
		videoEP = LINK.split('/')[-1].strip()
		log_MS("(playVideo) --- RTL-Daten : ### Serie [{0}] ### Episode [{1}] ### ---".format(videoSE, videoEP))
		return RtlGetVideo(videoSE, videoEP, LINK)
	if finalURL:
		listitem = xbmcgui.ListItem(name, path=finalURL)
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	log_MS("(playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---")

def ArdGetVideo(videoID):
	finalURL = False
	ARD_Url = ""
	try:
		content = getUrl('http://www.ardmediathek.de/play/media/'+videoID)
		result = json.loads(content)
		m3u8Links_1 = result["_mediaArray"][0]["_mediaStreamArray"]
		m3u8Links_2 = result["_mediaArray"][1]["_mediaStreamArray"]
		mp4Links = result["_mediaArray"][1]["_mediaStreamArray"]
		linkQuality = 3 # Beste verfügbare mp4-Qualität in der ARD-Mediathek = 3 (alle anderen sind schlechter)
		# Beste Qualität ?
		if preferredStreamType == "0" and (m3u8Links_1 or m3u8Links_2):
			for item in m3u8Links_1:
				stream = item["_stream"]
				if item["_quality"] == 'auto' and 'mil/master.m3u8' in stream:
					finalURL = stream
					log_MS("(ArdGetVideo) Wir haben 2 *m3u8-Streams* (ARD+3) - wähle den Ersten : {0}".format(finalURL))
			if not finalURL:
				for item in m3u8Links_2:
					stream = item["_stream"]
					if item["_quality"] == 'auto' and 'mil/master.m3u8' in stream:
						finalURL = stream
						log_MS("(ArdGetVideo) Wir haben 1 *m3u8-Stream*  (ARD+3) - wähle Diesen : {0}".format(finalURL))
			if finalURL and finalURL[:4] != "http":
				finalURL = "http:"+finalURL
		if mp4Links and not finalURL:
			if linkQuality == -1:
				linkQuality = 0
				for element in mp4Links:
					if element["_quality"] != 'auto' and element["_quality"] > linkQuality and '_stream' in element:
						linkQuality = element["_quality"]
			log_MS("(ArdGetVideo) ##### LINK-Qualität (ARD+3) = {0} ##### [3=beste|2=mittlere|1=schlechteste]".format(str(linkQuality)))
			for element in mp4Links:
				if linkQuality != element["_quality"]:
					continue
				stream = element["_stream"]
				# Überprüfen, ob die ausgewählte Qualität zwei Streams enthält
				if type(stream) is list or type(stream) is tuple:
					if len(stream) > 1:
						ARD_Url = stream[0]
						log_MS("(ArdGetVideo) Wir haben 2 *mp4-Streams* (ARD+3) - wähle den Ersten : {0}".format(ARD_Url))
					else:
						ARD_Url = stream[0]
						log_MS("(ArdGetVideo) Wir haben 1 *mp4-Stream* (ARD+3) in der Liste : {0}".format(ARD_Url))
				else:
					ARD_Url = stream
					log_MS("(ArdGetVideo) Wir haben 1 *mp4-Stream* (ARD+3) - wähle Diesen : {0}".format(ARD_Url))
			if ARD_Url != "" and ARD_Url[:4] != "http":
				ARD_Url = "http:"+ARD_Url
			finalURL = VideoBEST(ARD_Url, improve='ard-YES') # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
		if not finalURL:
			finalURL = ndrPodcastHack(finalURL)
			finalURL = dwHack(finalURL)
			log_MS("(ArdGetVideo) finalURL (ARD+3) NICHT gefunden - nutze Hack !")
		else:
			listitem = xbmcgui.ListItem(name, path=finalURL)
			xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
			log_MS("(ArdGetVideo) END-Qualität (ARD+3) : {0}".format(finalURL))
	except:
		log_MS("(ArdGetVideo) AbspielLink-00 (ARD+3) : *ARD-Intern* Der angeforderte -VideoLink- existiert NICHT !!!")
		xbmcgui.Dialog().notification((translation(30523).format('ARD - Intern')), translation(30525), icon, 8000)
	log_MS("(playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---")

def ndrPodcastHack(url):
	try:
		if url.startswith('http://media.ndr.de/download/podcasts/'):
			uri = url.split('/')[-1]
			YYYYMMDD = uri.split('-')[1]
			YYYY = YYYYMMDD[:4]
			MMDD = YYYYMMDD[4:]
			return 'http://hls.ndr.de/i/ndr/'+ YYYY +'/'+ MMDD +'/'+ uri
	except: pass
	return url

def dwHack(url):
	try:
		if url.startswith('http://tv-download.dw.de'):
			return url.replace('_sd.mp4','_hd_dwdownload.mp4')
	except: pass
	return url

def RtlGetVideo(SERIES, EPISODE, REFERER):
	j_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.GetAddonDetails", "params": {"addonid":"plugin.video.rtlnow", "properties": ["enabled"]}, "id":1}')
	if '"enabled":false' in j_query:
		try:
			xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": {"addonid":"plugin.video.rtlnow", "enabled":true}, "id":1}')
		except: pass
	if xbmc.getCondVisibility('System.HasAddon(plugin.video.rtlnow)'):
		#http://api.tvnow.de/v3/movies/shopping-queen/2361-lisa-marie-nuernberg-flower-power-praesentiere-dich-in-deinem-neuen-bluetenkleid?fields=manifest,isDrm,free
		streamURL = False
		try:
			content = getUrl('http://api.tvnow.de/v3/movies/{0}/{1}?fields=manifest,isDrm,free'.format(SERIES, EPISODE))
			response = json.loads(content)
			drm = response["isDrm"]
			free = response["free"]
			log_MS("(RtlGetVideo) --- RTL-Optionen : ### DRM = {0} ### FREE = {1} ### ---".format(drm, free))
			videoFREE = response["manifest"]["dashclear"].strip()
			if drm == True:
				debug_MS("(RtlGetVideo) ~~~ Video ist DRM - geschützt ~~~")
				try:
					videoDRM = response["manifest"]["dash"].strip()
				except:
					videoDRM = "0"
				log_MS("(RtlGetVideo) videoDRM : {0}".format(videoDRM))
			else:
				videoDRM = "0"
				log_MS("(RtlGetVideo) videoFREE : {0}".format(videoFREE))
			if videoDRM != "0":
				streamURL = videoDRM.replace('vodnowusodash.secure.footprint.net', 'vodnowusodash-a.akamaihd.net').split('.mpd')[0]+'.mpd'
				protected = "1"
			else:
				streamURL = videoFREE.replace('vodnowusodash.secure.footprint.net', 'vodnowusodash-a.akamaihd.net').split('.mpd')[0]+'.mpd'
				protected = "0"
			if streamURL:
				log_MS("(RtlGetVideo) END-Qualität (TV-Now) : {0}".format(streamURL))
				listitem = xbmcgui.ListItem(path='plugin://plugin.video.rtlnow/?mode=playdash&xstream='+str(streamURL)+'&xlink='+REFERER+'&xdrm='+protected)
				xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
		except:
			log_MS("(RtlGetVideo) AbspielLink-00 (TV-Now) : *TVNow-Plugin* Der angeforderte -VideoLink- existiert NICHT !!!")
			xbmcgui.Dialog().notification((translation(30523).format('TVNow - Plugin')), translation(30525), icon, 8000)
	else:
		log_MS("(RtlGetVideo) AbspielLink-00 (TV-Now) : KEIN *TVNow-Addon* zur Wiedergabe vorhanden !!!")
		xbmcgui.Dialog().notification((translation(30523).format('TVNow - Addon')), (translation(30524).format('TVNow-Addon')), icon, 8000)
		pass
	log_MS("(playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---")

def ZdfGetVideo(url):
	try: 
		content = getUrl(url)
		response = re.compile("data-zdfplayer-jsb='(\{.*?\})'", re.DOTALL).findall(content)[0]
		firstURL = json.loads(response)
		if firstURL:
			teaser = firstURL['content']
			secret = firstURL['apiToken']
			header = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'), ('Api-Auth', 'Bearer '+secret)]
			log_MS("(ZdfGetVideo) SECRET gefunden (ZDF+3) : xxxxx {0} xxxxx".format(str(secret)))
			if teaser[:4] != "http":
				teaser = ZDFapiUrl+teaser
			secondURL = getUrl(teaser, header=header)
			element = json.loads(secondURL)
			if element['profile'] == "http://zdf.de/rels/not-found":
				return False
			if element['contentType'] == "clip":
				component = element['mainVideoContent']['http://zdf.de/rels/target']
				#videoFOUND2 = ZDFapiUrl+element['mainVideoContent']['http://zdf.de/rels/target']['http://zdf.de/rels/streams/ptmd-template'].replace('{playerId}', 'ngplayer_2_3')
			elif element['contentType'] == "episode":
				if "mainVideoContent" in element:
					component = element['mainVideoContent']['http://zdf.de/rels/target']
				elif "mainContent" in element:
					component = element['mainContent'][0]['videoContent'][0]['http://zdf.de/rels/target']
			videoFOUND = ZDFapiUrl+component['http://zdf.de/rels/streams/ptmd']
			if videoFOUND:
				thirdURL = getUrl(videoFOUND, header=header)
				jsonObject = json.loads(thirdURL)
				return ZdfExtractQuality(jsonObject)
	except:
		log_MS("(ZdfGetVideo) AbspielLink-00 (ZDF+3) : *ZDF-Intern* Der angeforderte -VideoLink- existiert NICHT !!!")
		log_MS("(playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---")
		xbmcgui.Dialog().notification((translation(30523).format('ZDF - Intern')), translation(30525), icon, 8000)

def ZdfExtractQuality(jsonObject):
	DATA = {}
	DATA['media'] = []
	QUALITIES = ['auto', 'hd', 'veryhigh', 'high', 'med']
	finalURL = False
	try:
		for each in jsonObject['priorityList']:
			if preferredStreamType == "0" and each['formitaeten'][0]['type'] == "h264_aac_ts_http_m3u8_http":
				for found in QUALITIES:
					for quality in each['formitaeten'][0]['qualities']:
						if quality['quality'] == found:
							DATA['media'].append({'url': quality['audio']['tracks'][0]['uri'], 'type': 'video', 'mimeType': 'application/x-mpegURL'})
				finalURL = DATA['media'][0]['url']
				log_MS("(ZdfExtractQuality) m3u8-Stream (ZDF+3) : {0}".format(finalURL))
			if each['formitaeten'][0]['type'] == "h264_aac_mp4_http_na_na" and not finalURL:
				for found in QUALITIES:
					for quality in each['formitaeten'][0]['qualities']:
						if quality['quality'] == found:
							DATA['media'].append({'url': quality['audio']['tracks'][0]['uri'], 'type': 'video', 'mimeType': 'video/mp4'})
				log_MS("(ZdfExtractQuality) ZDF-STANDARDurl : {0}".format(DATA['media'][0]['url']))
				finalURL = VideoBEST(DATA['media'][0]['url'], improve='zdf-YES') # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
		if not finalURL:
			log_MS("(ZdfExtractQuality) AbspielLink-00 (ZDF+3) : *ZDF-Intern* VIDEO konnte NICHT abgespielt werden !!!")
		else:
			listitem = xbmcgui.ListItem(name, path=finalURL)
			xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
			log_MS("(ZdfExtractQuality) END-Qualität (ZDF+3) : {0}".format(finalURL))
	except:
		log_MS("(ZdfExtractQuality) AbspielLink-00 (ZDF+3) : *ZDF-Intern* Fehler bei Anforderung des AbspielLinks !!!")
	log_MS("(playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---")

def VideoBEST(best_url, improve=False):
	# *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
	standards = [best_url,"",""]
	if improve == "ard-YES":
		standards[1] = standards[0].replace('/960', '/1280').replace('.hq.mp4', '.hd.mp4').replace('.l.mp4', '.xl.mp4').replace('_C.mp4', '_X.mp4')
	elif improve == "zdf-YES":
		standards[1] = standards[0].replace('1456k_p13v11', '2328k_p35v11').replace('1456k_p13v12', '2328k_p35v12').replace('1496k_p13v13', '2328k_p35v13').replace('1496k_p13v14', '2328k_p35v14').replace('2256k_p14v11', '2328k_p35v11').replace('2256k_p14v12', '2328k_p35v12').replace('2296k_p14v13', '2328k_p35v13').replace('2296k_p14v14', '2328k_p35v14')
		standards[2] = standards[1].replace('2328k_p35v12', '3328k_p36v12').replace('2328k_p35v13', '3328k_p36v13').replace('2328k_p35v14', '3328k_p36v14')
	for element in reversed(standards):
		if len(element) > 0:
			code = urlopen(element).getcode()
			if str(code) == "200":
				return element
	return best_url

def cleanTitle(title):
	title = py2_enc(title)
	title = title.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('amp;', '').replace('&#39;', '\'').replace('&#039;', '\'').replace('&quot;', '"').replace('&szlig;', 'ß').replace('&ndash;', '-').replace('#', '')
	title = title.replace('&#x00c4', 'Ä').replace('&#x00e4', 'ä').replace('&#x00d6', 'Ö').replace('&#x00f6', 'ö').replace('&#x00dc', 'Ü').replace('&#x00fc', 'ü').replace('&#x00df', 'ß')
	title = title.replace('&Auml;', 'Ä').replace('&Ouml;', 'Ö').replace('&Uuml;', 'Ü').replace('&auml;', 'ä').replace('&ouml;', 'ö').replace('&uuml;', 'ü')
	title = title.replace('&agrave;', 'à').replace('&aacute;', 'á').replace('&acirc;', 'â').replace('&egrave;', 'è').replace('&eacute;', 'é').replace('&ecirc;', 'ê').replace('&igrave;', 'ì').replace('&iacute;', 'í').replace('&icirc;', 'î')
	title = title.replace('&ograve;', 'ò').replace('&oacute;', 'ó').replace('&ocirc;', 'ô').replace('&ugrave;', 'ù').replace('&uacute;', 'ú').replace('&ucirc;', 'û')
	title = title.replace("\\'", "'").replace('<wbr/>', '').replace('<br />', ' -').replace(" ", ".").replace('Ã¶', 'ö')
	title = title.strip()
	return title

def cleanStation(channelID):
	ChannelCode = ('ARD','Das Erste','ONE','ZDF','2NEO','ZNEO','2INFO','ZINFO','3SAT','Arte','ARTE','BR','HR','KIKA','MDR','NDR','N3','ORF','PHOEN','RBB','SR','SWR','SWR/SR','WDR','RTL','RTL2','VOX','SRTL','SUPER')
	if channelID in ChannelCode and channelID != "":
		try:
			channelID = channelID.replace(' ', '')
			if 'ARD' in channelID or 'DasErste' in channelID:
				channelID = '  (Das Erste)'
			elif 'ONE' in channelID:
				channelID = '  (ONE)'
			elif 'Arte' in channelID or 'ARTE' in channelID:
				channelID = '  (ARTE)'
			elif '2INFO' in channelID or 'ZINFO' in channelID:
				channelID = '  (ZDFinfo)'
			elif '2NEO' in channelID or 'ZNEO' in channelID:
				channelID = '  (ZDFneo)'
			elif '3SAT' in channelID:
				channelID = '  (3sat)'
			elif 'NDR' in channelID or 'N3' in channelID:
				channelID = '  (NDR)'
			elif 'PHOEN' in channelID:
				channelID = '  (PHOENIX)'
			elif ('SR' in channelID or 'SWR' in channelID) and not 'SRTL' in channelID:
				channelID = '  (SWR)'
			elif 'SRTL' in channelID or 'SUPER' in channelID:
				channelID = '  (SRTL)'
			else:
				channelID = '  ('+channelID+')'
		except: pass
	elif not channelID in ChannelCode and channelID != "":
		channelID = '  ('+channelID+')'
	else:
		channelID = ""
	return channelID

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def addVideoList(url, name, image, studio):
	PL = xbmc.PlayList(1)
	listitem = xbmcgui.ListItem(name, thumbnailImage=image)
	listitem.setInfo(type="Video", infoLabels={"Title": name, "Studio": studio, "mediatype": "video"})
	if useThumbAsFanart and image != icon:
		listitem.setArt({'fanart': image})
	else:
		listitem.setArt({'fanart': defaultFanart})
	listitem.setProperty('IsPlayable', 'true')
	listitem.setContentLookup(False)
	PL.add(url, listitem)

def addDir(name, url, mode, image, plot=None, studio=None, genre=None):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Studio": studio, "Genre": genre})
	if useThumbAsFanart and image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

def addLink(name, url, mode, image, plot=None, studio=None, genre=None, duration=None, director=None, rating=None):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Studio": studio, "Genre": genre, "Duration": duration, "Director": director, "Rating": rating, "mediatype": "video"})
	if useThumbAsFanart and image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	if duration is not None:
		liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	liz.addContextMenuItems([(translation(30601), 'RunPlugin(plugin://{0}?mode=addVideoList&url={1}&name={2}&image={3}&studio={4})'.format(addon.getAddonInfo('id'), quote_plus(u), quote_plus(name), quote_plus(image), quote_plus(studio)))])
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
image = unquote_plus(params.get('image', ''))
studio = unquote_plus(params.get('studio', ''))
referer = unquote_plus(params.get('referer', ''))

if mode == 'listChannel':
	listChannel(url)
elif mode == 'listVideos_Day_Channel_Highlights':
	listVideos_Day_Channel_Highlights(url)
elif mode == 'listVideosGenre':
	listVideosGenre(url)
elif mode == 'playVideo':
	playVideo(url)
elif mode == 'addVideoList':
	addVideoList(url, name, image, studio)
else:
	index()