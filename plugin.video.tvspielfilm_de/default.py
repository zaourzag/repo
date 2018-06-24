#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    This Plugin is compatible between Python 2.X and Python 3+
    without using any extra extern Plugins from XBMC (KODI)
    Copyright (C) 2018 by realvito
    Released under GPL(v3)
'''

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import os
import re
import sys
try:
	import urllib, urllib2  # Python 2.X
	import cookielib  # Python 2.X
	unquote_plus = urllib.unquote_plus
	quote_plus = urllib.quote_plus
	quote = urllib.quote
	urlopen = urllib.urlopen
	makeRequest = urllib2
	makeCooks = cookielib
except ImportError:
	import urllib.parse, urllib.request  # Python 3+
	import http.cookiejar  # Python 3+
	unquote_plus = urllib.parse.unquote_plus
	quote_plus = urllib.parse.quote_plus
	quote = urllib.parse.quote
	urlopen = urllib.request.urlopen
	makeRequest = urllib.request
	makeCooks = http.cookiejar
import json
import xbmcvfs
import shutil
import socket
import time
from datetime import date,datetime,timedelta
from io import BytesIO
import gzip

#token = 'ffc9a283b511b7e11b326fdc3d76c5559b50544e reraeB'
#getheader = {'Api-Auth': 'reraeB '+token[::-1]} = Gespiegelt
#getheader = {'Api-Auth': 'Bearer '+token} = Original

base_url = sys.argv[0]
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
translation = addon.getLocalizedString
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

try:
	if xbmcvfs.exists(temp):
		shutil.rmtree(temp)
except: pass
xbmcvfs.mkdirs(temp)
cookie=os.path.join(temp, 'cookie.lwp')
cj = makeCooks.LWPCookieJar();

if xbmcvfs.exists(cookie):
	cj.load(cookie, ignore_discard=True, ignore_expires=True)

def debug(msg, level=xbmc.LOGNOTICE):
	if enableDebug:
		xbmc.log('[TvSpielfilm]'+msg, level)

def getUrl(url, header=False, referer=False):
	global cj
	for cook in cj:
		debug("(getUrl) Cookie : %s" %str(cook))
	pos = 0
	opener = makeRequest.build_opener(makeRequest.HTTPCookieProcessor(cj))
	try:
		if header:
			opener.addheaders = header
		else:
			opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')]
			opener.addheaders = [('Accept-Encoding', 'gzip, deflate')]
		if referer:
			opener.addheaders = [('Referer', referer)]
		response = opener.open(url, timeout=30)
		content = response.read()
		if response.headers.get('Content-Encoding', '') == 'gzip':
			content = gzip.GzipFile(fileobj=BytesIO(content)).read().decode('utf-8')
	except Exception as e:
		if pos < 1 and 'SSL23_GET_SERVER_HELLO' in str(e):
			pos += 1
			try:
				python_version = str(sys.version).split(')')[0].strip()+")"
			except:
				python_version = "Unbekannte Version - NICHT ermittelbar"
			xbmcgui.Dialog().ok(addon.getAddonInfo('id'), "[COLOR orangered]ACHTUNG : ... die installierte PHYTONVERSION : *"+python_version+"* ist zu alt !!![/COLOR]", "Bitte zu KODI-Krypton (Version 17 oder höher) oder -FTMC updaten !!!")
			xbmc.log("[TvSpielfilm](getUrl) ERROR - ERROR - ERROR : ##### Die installierte PHYTONVERSION : *"+python_version+"* ist zu alt !!! ##### Bitte zu KODI-Krypton (Version 17 oder höher) oder -FTMC updaten !!! #####", xbmc.LOGFATAL)
		elif pos < 1 and 'getaddrinfo failed' in str(e):
			pos += 1
			xbmcgui.Dialog().ok(addon.getAddonInfo('id'), "[COLOR orangered]ACHTUNG : ... Es besteht ein Problem mit dem Netzwerk !!![/COLOR]", "Entweder ist die angeforderte - WebSeite - zurzeit nicht erreichbar oder ...", "... überprüfen Sie, ob Ihre Internetverbindung funktioniert ?!")
			xbmc.log("[TvSpielfilm](getUrl) ERROR - ERROR - ERROR : ########## %s ##########" %(str(e)), xbmc.LOGFATAL)
		else:
			err = str(e)
			if hasattr(e, 'code'):
				xbmc.log("[TvSpielfilm](getUrl) ERROR - ERROR - ERROR : ########## %s = %s ##########" %(url, err), xbmc.LOGFATAL)
			elif hasattr(e, 'reason'):
				xbmc.log("[TvSpielfilm](getUrl) ERROR - ERROR - ERROR : ########## %s = %s ##########" %(url, err), xbmc.LOGFATAL)
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
	debug("(listChannel) SENDER-SORTIERUNG : Alle Sender in TvSpielfilm")
	if showNOW == 'true':
		debug("(listChannel) --- NowTV - Sender EINGEBLENDET ---")
	else:
		debug("(listChannel) --- NowTV - Sender AUSGEBLENDET ---")
	content = html[html.find('<section class="mediathek-channels">'):]
	content = content[:content.find('</section>')]
	spl = content.split('title=')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		try:
			url = re.compile(r'href=["\'](https?://.*?)["\']>', re.DOTALL).findall(entry)[0]
			channelID = url.split('channel=')[1].strip()
			channelID = cleanStation(channelID.strip())
			title = channelID.replace('(', '').replace(')', '').replace(' ', '')
			if showNOW == 'false':
				if ("RTL" in channelID or "VOX" in channelID or "SUPER" in channelID):
					continue
			debug("(listChannel) Link : %s%s" %(url, channelID))
			addDir('[COLOR lime]'+title+'[/COLOR]', url, 'listVideos_Day_Channel_Highlights', pic+title+'.png')
		except: pass
	xbmcplugin.endOfDirectory(pluginhandle)

def listVideos_Day_Channel_Highlights(url):
	html = getUrl(url)
	debug("(listVideos_Day_Channel_Highlights) MEDIATHEK : %s" %url)
	if showNOW == 'true':
		debug("(listVideos_Day_Channel_Highlights) --- NowTV - Sender EINGEBLENDET ---")
	else:
		debug("(listVideos_Day_Channel_Highlights) --- NowTV - Sender AUSGEBLENDET ---")
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
					title = cleanTitle(first.strip())
				else:
					title = cleanTitle(first.strip())+" - "+cleanTitle(third.replace(first, "").strip())
				added = ""
				channelID = cleanTitle(url.split('/')[-1].replace('?channel=', '').strip())
				channelID = cleanStation(channelID.strip())
				studio = channelID.replace('(', '').replace(')', '').replace('  ', '')
			elif (match1[0] and match2[0] and not match3[0]):
				title = cleanTitle(match1[0].strip())+" - "+cleanTitle(match2[0].split('|')[-1].strip())
				added = match2[0].split('|')[0].strip()
				channelID = cleanTitle(match2[0].split('|')[1].strip())
				channelID = cleanStation(channelID.strip())
				studio = channelID.replace('(', '').replace(')', '').replace('  ', '')
			elif (match1[0] and match2[0] and match3[0]):
				first = match1[0].replace('…', '').replace('...', '').strip()
				third = match3[0].replace('…', '').replace('...', '').strip()
				if first == third:
					title = cleanTitle(first.strip())
				else:
					title = cleanTitle(first.strip())+" - "+cleanTitle(third.replace(first, "").strip())
				added = match2[0].split('|')[0].strip()
				channelID = cleanTitle(match2[0].split('|')[1].strip())
				channelID = cleanStation(channelID.strip())
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
			debug("(listVideos_Day_Channel_Highlights) Name : %s" %title)
			debug("(listVideos_Day_Channel_Highlights) Link : %s" %urlFW)
			debug("(listVideos_Day_Channel_Highlights) Icon : %s" %photo)
			addLink(title, urlFW, 'playVideo', photo, studio=studio)
		except: pass
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listVideosGenre(category):
	html = getUrl(baseURL+"/mediathek/")
	debug("(listVideosGenre) MEDIATHEK : %s/mediathek/ - Genre = *%s*" %(baseURL, category.upper()))
	if showNOW == 'true':
		debug("(listVideosGenre) --- NowTV - Sender EINGEBLENDET ---")
	else:
		debug("(listVideosGenre) --- NowTV - Sender AUSGEBLENDET ---")
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
				title = cleanTitle(first.strip())
			elif ('...' in secondONE and not '...' in secondTWO):
				title = cleanTitle(first.replace(secondTWO, "").strip())+" - "+cleanTitle(secondTWO.strip())
			elif ('...' in secondONE and '...' in secondTWO):
				title = cleanTitle(first.strip())
			else:
				title = cleanTitle(secondONE.strip())+" - "+cleanTitle(first.replace(secondONE, "").strip())
			added = re.compile(r'<div class=["\']col["\']>(.*?)</div>', re.DOTALL).findall(entry)[0]
			if showDATE and added != "":
				title = added.strip()+"  "+title
			match3 = re.compile(r'target=["\']_self["\'] title=["\'].+?["\']>(.*?)</a>', re.DOTALL).findall(entry)
			channelID = cleanTitle(match3[0].strip())
			channelID = cleanStation(channelID.strip())
			studio = channelID.replace('(', '').replace(')', '').replace('  ', '')
			urlFW = re.compile(r'<a href=["\'](https?://.*?mediathek/.*?)["\']', re.DOTALL).findall(entry)[0]
			photo = re.compile(r'<img src=["\'](https?://.*?.jpg)["\']', re.DOTALL).findall(entry)[0]
			if ',' in photo:
				photo = photo.split(',')[0].rstrip()+'.jpg'
			if showTVchannel:
				title += channelID
			if showNOW == 'false':
				if ("RTL" in channelID or "VOX" in channelID or "SUPER" in channelID):
					continue
			debug("(listVideosGenre) Name : %s" %title)
			debug("(listVideosGenre) Link : %s" %urlFW)
			debug("(listVideosGenre) Icon : %s" %photo)
			addLink(title, urlFW, 'playVideo', photo, studio=studio)
		except: pass
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode:
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playVideo(url):
	finalURL = False
	ARD_SCHEMES = ('http://www.ardmediathek.de', 'https://www.ardmediathek.de', 'http://mediathek.daserste.de', 'https://mediathek.daserste.de')
	RTL_SCHEMES = ('http://www.nowtv.de', 'https://www.nowtv.de', 'http://www.tvnow.de', 'https://www.tvnow.de')
	xbmc.log("[TvSpielfilm](playVideo) --- START WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)
	xbmc.log("[TvSpielfilm](playVideo) frei", xbmc.LOGNOTICE)
	try:
		content = getUrl(url)
		LINK = re.compile('<header class="broadcast-detail__header">.+?<a href="([^"]+)" class="mediathek-open col-hover-thek"', re.DOTALL).findall(content)[0]
		xbmc.log("[TvSpielfilm](playVideo) AbspielLink (Original) : %s" %(LINK), xbmc.LOGNOTICE)
	except:
		LINK = False
		xbmc.log("[TvSpielfilm](playVideo) MediathekLink-00 : MediathekLink der Sendung in TvSpielfilm NICHT gefunden !!!", xbmc.LOGERROR)
		xbmc.executebuiltin('Notification(TvSpielfilm : [COLOR red]!!! MediathekURL - ERROR !!![/COLOR], ERROR = [COLOR red]*MediathekLink* der Sendung NICHT gefunden ![/COLOR],6000,'+icon+')')
	xbmc.log("[TvSpielfilm](playVideo) frei", xbmc.LOGNOTICE)
	if LINK.startswith("https://www.arte.tv"):
		videoID = re.compile("arte.tv/de/videos/([^/]+?)/", re.DOTALL).findall(LINK)[0]
		try:
			plugin2 = xbmcaddon.Addon(id='plugin.video.L0RE.arte')
			finalURL = 'plugin://'+plugin2.getAddonInfo('id')+'/?mode=playvideo&url='+videoID
			xbmc.log("[TvSpielfilm](playVideo) AbspielLink-1 (ARTE-TV) : %s" %(finalURL), xbmc.LOGNOTICE)
		except:
			try:
				plugin3 = xbmcaddon.Addon(id='plugin.video.arteplussept')
				finalURL = 'plugin://'+plugin3.getAddonInfo('id')+'/play/'+quote_plus(videoID)
				xbmc.log("[TvSpielfilm](playVideo) AbspielLink-2 (ARTE-plussept) : %s" %(finalURL), xbmc.LOGNOTICE)
			except:
				if finalURL:
					xbmc.log("[TvSpielfilm](playVideo) AbspielLink-00 (ARTE) : *ARTE-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGERROR)
				else:
					xbmc.log("[TvSpielfilm](playVideo) AbspielLink-00 (ARTE) : KEIN *ARTE-Plugin* zur Wiedergabe vorhanden !!!", xbmc.LOGFATAL)
					xbmc.executebuiltin('Notification(TvSpielfilm : [COLOR red]!!! ADDON - ERROR !!![/COLOR], ERROR = [COLOR red]KEIN *ARTE-Plugin* installiert[/COLOR] - bitte überprüfen ...,6000,'+icon+')')
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
		xbmc.log("[TvSpielfilm](playVideo) --- RTL-Daten : ### Serie ["+videoSE+"] ### Episode ["+videoEP+"] ### ---", xbmc.LOGNOTICE)
		return RtlGetVideo(videoSE, videoEP, LINK)
	if finalURL:
		listitem = xbmcgui.ListItem(name, path=finalURL)
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	xbmc.log("[TvSpielfilm](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)

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
					xbmc.log("[TvSpielfilm](ArdGetVideo) Wir haben 2 *m3u8-Streams* (ARD+3) - wähle den Ersten : %s" %(finalURL), xbmc.LOGNOTICE)
			if not finalURL:
				for item in m3u8Links_2:
					stream = item["_stream"]
					if item["_quality"] == 'auto' and 'mil/master.m3u8' in stream:
						finalURL = stream
						xbmc.log("[TvSpielfilm](ArdGetVideo) Wir haben 1 *m3u8-Stream*  (ARD+3) - wähle Diesen : %s" %(finalURL), xbmc.LOGNOTICE)
			if finalURL and finalURL[:4] != "http":
				finalURL = "http:"+finalURL
		if mp4Links and not finalURL:
			if linkQuality == -1:
				linkQuality = 0
				for element in mp4Links:
					if element["_quality"] != 'auto' and element["_quality"] > linkQuality and '_stream' in element:
						linkQuality = element["_quality"]
			xbmc.log("[TvSpielfilm](ArdGetVideo) ##### LINK-Qualität (ARD+3) = %s ##### [3=beste|2=mittlere|1=schlechteste]" %(str(linkQuality)), xbmc.LOGNOTICE)
			for element in mp4Links:
				if linkQuality != element["_quality"]:
					continue
				stream = element["_stream"]
				# Überprüfen, ob die ausgewählte Qualität zwei Streams enthält
				if type(stream) is list or type(stream) is tuple:
					if len(stream) > 1:
						ARD_Url = stream[0]
						xbmc.log("[TvSpielfilm](ArdGetVideo) Wir haben 2 *mp4-Streams* (ARD+3) - wähle den Ersten : %s" %(ARD_Url), xbmc.LOGNOTICE)
					else:
						ARD_Url = stream[0]
						xbmc.log("[TvSpielfilm](ArdGetVideo) Wir haben 1 *mp4-Stream* (ARD+3) in der Liste : %s" %(ARD_Url), xbmc.LOGNOTICE)
				else:
					ARD_Url = stream
					xbmc.log("[TvSpielfilm](ArdGetVideo) Wir haben 1 *mp4-Stream* (ARD+3) - wähle Diesen : %s" %(ARD_Url), xbmc.LOGNOTICE)
			if ARD_Url != "" and ARD_Url[:4] != "http":
				ARD_Url = "http:"+ARD_Url
			finalURL = VideoBEST(ARD_Url, improve='ard-YES') # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
		if not finalURL:
			finalURL = ndrPodcastHack(finalURL)
			finalURL = dwHack(finalURL)
			xbmc.log("[TvSpielfilm](ArdGetVideo) finalURL (ARD+3) NICHT gefunden - nutze Hack !", xbmc.LOGNOTICE)
		else:
			listitem = xbmcgui.ListItem(name, path=finalURL)
			xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
			xbmc.log("[TvSpielfilm](ArdGetVideo) END-Qualität (ARD+3) : %s" %(finalURL), xbmc.LOGNOTICE)
	except:
		xbmc.log("[TvSpielfilm](ArdGetVideo) AbspielLink-00 (ARD+3) : *ARD-Plugin* Der angeforderte -VideoLink- existiert NICHT !!!", xbmc.LOGERROR)
		xbmc.executebuiltin('Notification(TvSpielfilm : [COLOR red]!!! VideoURL - ERROR !!![/COLOR], ERROR = [COLOR red]Der angeforderte *VideoLink* existiert NICHT ![/COLOR],6000,'+icon+')')
	xbmc.log("[TvSpielfilm](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)

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
			content = getUrl('http://api.tvnow.de/v3/movies/%s/%s?fields=manifest,isDrm,free' %(SERIES, EPISODE))
			response = json.loads(content)
			drm = response["isDrm"]
			free = response["free"]
			xbmc.log("[TvSpielfilm](RtlGetVideo) --- RTL-Optionen : ### DRM = %s ### FREE = %s ### ---" %(drm, free), xbmc.LOGNOTICE)
			videoFREE = response["manifest"]["dashclear"].strip()
			if drm == True:
				debug("(RtlGetVideo) ~~~ Video ist DRM - geschützt ~~~")
				try:
					videoDRM = response["manifest"]["dash"].strip()
				except:
					videoDRM = "0"
				xbmc.log("[TvSpielfilm](RtlGetVideo) videoDRM : %s" %(videoDRM), xbmc.LOGNOTICE)
			else:
				videoDRM = "0"
				xbmc.log("[TvSpielfilm](RtlGetVideo) videoFREE : %s" %(videoFREE), xbmc.LOGNOTICE)
			if videoDRM != "0":
				streamURL = videoDRM.replace('vodnowusodash.secure.footprint.net', 'vodnowusodash-a.akamaihd.net').split('.mpd')[0]+'.mpd'
				protected = "1"
			else:
				streamURL = videoFREE.replace('vodnowusodash.secure.footprint.net', 'vodnowusodash-a.akamaihd.net').split('.mpd')[0]+'.mpd'
				protected = "0"
			if streamURL:
				xbmc.log("[TvSpielfilm](RtlGetVideo) END-Qualität (TVnow) : %s" %(streamURL), xbmc.LOGNOTICE)
				listitem = xbmcgui.ListItem(path='plugin://plugin.video.rtlnow/?mode=playdash&xstream='+str(streamURL)+'&xlink='+REFERER+'&xdrm='+protected)
				xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
		except:
			xbmc.log("[TvSpielfilm](RtlGetVideo) AbspielLink-00 (TVnow) : *TVnow-Plugin* Der angeforderte -VideoLink- existiert NICHT !!!", xbmc.LOGERROR)
			xbmc.executebuiltin('Notification(TvSpielfilm : [COLOR red]!!! VideoURL - ERROR !!![/COLOR], ERROR = [COLOR red]Der angeforderte *VideoLink* existiert NICHT ![/COLOR],6000,'+icon+')')
	else:
		xbmc.log("[TvSpielfilm](playVideo) AbspielLink-00 (TVnow) : KEIN *TVnow-Plugin* zur Wiedergabe vorhanden !!!", xbmc.LOGFATAL)
		xbmc.executebuiltin('Notification(TvSpielfilm : [COLOR red]!!! ADDON - ERROR !!![/COLOR], ERROR = [COLOR red]KEIN *TVnow-Plugin* installiert[/COLOR] - bitte überprüfen ...,6000,'+icon+')')
		pass
	xbmc.log("[TvSpielfilm](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)

def ZdfGetVideo(url):
	try: 
		content = getUrl(url)
		firstURL = json.loads(re.compile("data-zdfplayer-jsb='(\{.*?\})'", re.DOTALL).findall(content)[0])
		if firstURL:
			teaser = firstURL['content']
			secret = firstURL['apiToken']
			header = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'), ('Api-Auth', 'Bearer '+secret)]
			xbmc.log("[TvSpielfilm](ZdfGetVideo) SECRET gefunden (ZDF+3) : xxxxx %s xxxxx" %str(secret), xbmc.LOGNOTICE)
			if teaser[:4] != "http":
				teaser = ZDFapiUrl+teaser
			secondURL = getUrl(teaser, header=header)
			element = json.loads(secondURL)
			if element['contentType'] == "episode":
				if not element['hasVideo']:
					return False
				if "mainVideoContent" in element:
					component = element['mainVideoContent']['http://zdf.de/rels/target']
				elif "mainContent" in element:
					component = element['mainContent'][0]['videoContent'][0]['http://zdf.de/rels/target']
				videoFOUND = ZDFapiUrl+component['http://zdf.de/rels/streams/ptmd']
			elif element['contentType'] == "clip":
				videoFOUND = ZDFapiUrl+element['mainVideoContent']['http://zdf.de/rels/target']['http://zdf.de/rels/streams/ptmd']
				#videoFOUND2 = ZDFapiUrl+element['mainVideoContent']['http://zdf.de/rels/target']['http://zdf.de/rels/streams/ptmd-template'].replace('{playerId}', 'ngplayer_2_3')
			if videoFOUND:
				thirdURL = getUrl(videoFOUND, header=header)
				jsonObject = json.loads(thirdURL)
				return ZdfExtractQuality(jsonObject)
	except:
		xbmc.log("[TvSpielfilm](ZdfGetVideo) AbspielLink-00 (ZDF+3) : *ZDF-Plugin* Der angeforderte -VideoLink- existiert NICHT !!!", xbmc.LOGERROR)
		xbmc.log("[TvSpielfilm](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)
		xbmc.executebuiltin('Notification(TvSpielfilm : [COLOR red]!!! VideoURL - ERROR !!![/COLOR], ERROR = [COLOR red]Der angeforderte *VideoLink* existiert NICHT ![/COLOR],6000,'+icon+')')

def ZdfExtractQuality(jsonObject):
	DATA = {}
	DATA['media'] = []
	QUALITIES = ['auto', 'hd', 'veryhigh', 'high', 'med']
	finalURL = False
	try:
		for each in jsonObject['priorityList']:
			if preferredStreamType == "0" and each['formitaeten'][0]['type'] == 'h264_aac_ts_http_m3u8_http':
				for found in QUALITIES:
					for quality in each['formitaeten'][0]['qualities']:
						if quality['quality'] == found:
							DATA['media'].append({'url': quality['audio']['tracks'][0]['uri'], 'type': 'video', 'mimeType': 'application/x-mpegURL'})
				finalURL = DATA['media'][0]['url']
				xbmc.log("[TvSpielfilm](ZdfExtractQuality) m3u8-Stream (ZDF+3) : %s" %(finalURL), xbmc.LOGNOTICE)
			if each['formitaeten'][0]['type'] == 'h264_aac_mp4_http_na_na' and not finalURL:
				for found in QUALITIES:
					for quality in each['formitaeten'][0]['qualities']:
						if quality['quality'] == found:
							DATA['media'].append({'url': quality['audio']['tracks'][0]['uri'], 'type': 'video', 'mimeType': 'video/mp4'})
				xbmc.log("[TvSpielfilm](ZdfExtractQuality) ZDF-STANDARDurl : %s" %(DATA['media'][0]['url']), xbmc.LOGNOTICE)
				finalURL = VideoBEST(DATA['media'][0]['url'], improve='zdf-YES') # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
		if not finalURL:
			xbmc.log("[TvSpielfilm](ZdfExtractQuality) AbspielLink-00 (ZDF+3) : *ZDF-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGERROR)
		else:
			listitem = xbmcgui.ListItem(name, path=finalURL)
			xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
			xbmc.log("[TvSpielfilm](ZdfExtractQuality) END-Qualität (ZDF+3) : %s" %(finalURL), xbmc.LOGNOTICE)
	except:
		xbmc.log("[TvSpielfilm](ZdfExtractQuality) AbspielLink-00 (ZDF+3) : *ZDF-Plugin* Fehler bei Anforderung des AbspielLinks !!!", xbmc.LOGERROR)
	xbmc.log("[TvSpielfilm](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)

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
				channelID = '  (DasErste)'
			elif 'ONE' in channelID:
				channelID = '  (ARDone)'
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

def queueVideo(url, name, image):
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	listitem = xbmcgui.ListItem(name, thumbnailImage=image)
	if useThumbAsFanart and image != icon:
		listitem.setArt({'fanart': image})
	else:
		listitem.setArt({'fanart': defaultFanart})
	playlist.add(url, listitem)

def addDir(name, url, mode, image, plot=None):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
	if useThumbAsFanart and image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

def addLink(name, url, mode, image, plot=None, studio=None, genre=None, duration=None, director=None, rating=None):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Studio": studio, "Genre": genre, "Duration": duration, "Director": director, "Rating": rating})
	if useThumbAsFanart and image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	if duration is not None:
		liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.addContextMenuItems([(translation(40201), 'RunPlugin(plugin://'+addon.getAddonInfo('id')+'/?mode=queueVideo&url='+quote_plus(u)+'&name='+quote_plus(name)+'&image='+quote_plus(image)+')',)])
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
image = unquote_plus(params.get('image', ''))
referer = unquote_plus(params.get('referer', ''))

if mode == 'listChannel':
	listChannel(url)
elif mode == 'listVideos_Day_Channel_Highlights':
	listVideos_Day_Channel_Highlights(url)
elif mode == 'listVideosGenre':
	listVideosGenre(url)
elif mode == 'playVideo':
	playVideo(url)
elif mode == 'queueVideo':
	queueVideo(url, name, image)
else:
	index()