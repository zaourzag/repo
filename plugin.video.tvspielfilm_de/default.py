#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
try: import simplejson as json
except ImportError: import json
import urllib
import urllib2
import urlparse
import time
import socket
from datetime import date,datetime,timedelta
from operator import itemgetter
from StringIO import StringIO
import gzip

token = '23a1db22b51b13162bd0b86b24e556c8c6b6272d reraeB'
getheader = {'Api-Auth': token[::-1]}

main_url = sys.argv[0]
pluginhandle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

addonID = 'plugin.video.tvspielfilm_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(40)
translation = addon.getLocalizedString
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).decode('utf-8')
dataPath = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
fanart = os.path.join(addonPath, 'fanart.jpg').decode('utf-8')
icon = os.path.join(addonPath, 'icon.png').decode('utf-8')
preferredStreamType = addon.getSetting("streamSelection")
showSender = addon.getSetting("enableSender")
showNOW = addon.getSetting("enableTVnow")
enableDebug = addon.getSetting("enableDebug")
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == 'true'
forceViewMode = addon.getSetting("forceView") 
viewMode = str(addon.getSetting("viewID"))
baseUrl = "http://www.tvspielfilm.de"
dateUrl = "/mediathek/nach-datum/"


if not os.path.isdir(dataPath):
	os.makedirs(dataPath)


def debug(msg, level=xbmc.LOGNOTICE):
	if enableDebug == 'true':
		xbmc.log('[TvSpielfilm]'+msg, level)

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

	addDir("Auswahl vom "+w1+", den "+m1, baseUrl+dateUrl+"?date="+s1, 'listVideosNachTag', icon)
	addDir("Auswahl vom "+w2+", den "+m2, baseUrl+dateUrl+"?date="+s2, 'listVideosNachTag', icon)
	addDir("Auswahl vom "+w3+", den "+m3, baseUrl+dateUrl+"?date="+s3, 'listVideosNachTag', icon)
	addDir("Auswahl vom "+w4+", den "+m4, baseUrl+dateUrl+"?date="+s4, 'listVideosNachTag', icon)
	addDir("Auswahl vom "+w5+", den "+m5, baseUrl+dateUrl+"?date="+s5, 'listVideosNachTag', icon)
	addDir("+ TV-HIGHLIGHTS +", "", 'listVideosAlle', icon)
	addDir("* Spielfilme *", "Spielfilm", 'listVideosGenre', icon)
	addDir("* Serien *", "Serie", 'listVideosGenre', icon)
	addDir("* Reportagen *", "Report", 'listVideosGenre', icon)
	addDir("* Unterhaltung *", "Unterhaltung", 'listVideosGenre', icon)
	addDir("* Kinder *", "Kinder", 'listVideosGenre', icon)
	addDir("* Sport *", "Sport", 'listVideosGenre', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def listVideosNachTag(url=""):
	content = getUrl(url)
	debug("(listVideosNachTag) MEDIATHEK : %s" %url)
	if showNOW == 'true':
		debug("(listVideosNachTag) --- NowTV - Sender EINGEBLENDET ---")
	else:
		debug("(listVideosNachTag) --- NowTV - Sender AUSGEBLENDET ---")
	content = content[content.find('<form id="tvScheduleForm" action="/mediathek/nach-datum"')+1:]
	content = content[:content.find('<aside class="aside">')]
	spl = content.split('<div class="video-box"')
	entries = []
	for i in range(1, len(spl), 1):
		entry = spl[i]
		try:
			match1 = re.compile('class="mainImage" title="(.*?)">', re.DOTALL).findall(entry)
			match2= re.compile('<p class="subtitle">(.*?)</p>\s+<p class="h3">(.*?)</p>', re.DOTALL).findall(entry)
			if (match2[0][0] and match2[0][1]):
				title = cleanTitle(match2[0][1].strip())+" - "+cleanTitle(match2[0][0].strip())
			else:
				title = cleanTitle(match1[0].strip())
			img = re.compile('<img src="(http.*?.jpg)"', re.DOTALL).findall(entry)[0]
			if ',' in img:
				thumb = img.split(',')[0].rstrip()+'.jpg'
			else:
				thumb = img
			match3 = re.compile('<span class="logotype chl_bg_m c-.+?">(.*?)</span>', re.DOTALL).findall(entry)
			senderID = cleanTitle(match3[0].strip())
			senderID = cleanSender(senderID.strip())
			url = re.compile('<div class="teaser">\s+<a href="(http://www.tvspielfilm.de/mediathek/.*?)"', re.DOTALL).findall(entry)[0]
			match4 = re.compile('<p class="teaser">(.*?)</p>', re.DOTALL).findall(entry)
			plot = cleanTitle(match4[0].strip())
			if showSender == 'true':
				name = title+senderID
			else:
				name = title
			if showNOW == 'true':
				pass
			else:
				if ("RTL" in senderID or "VOX" in senderID or "SUPER" in senderID):
					continue
			debug("(listVideosNachTag) Name - %s" %name)
			debug("(listVideosNachTag) Link : %s" %url)
			debug("(listVideosNachTag) Icon : %s" %thumb)
			addLink(name, url, 'playVideo', thumb, plot)
		except:
			pass
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode == 'true':
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listVideosAlle():
	content = getUrl(baseUrl+"/mediathek/")
	debug("(listVideosAlle) MEDIATHEK : %s/mediathek/ - TV-HIGHLIGHTS" %baseUrl)
	if showNOW == 'true':
		debug("(listVideosAlle) --- NowTV - Sender EINGEBLENDET ---")
	else:
		debug("(listVideosAlle) --- NowTV - Sender AUSGEBLENDET ---")
	content = content[content.find('<div class="carousel-container">')+1:]
	content = content[:content.find('<div id="carousel-left"></div>')]
	spl = content.split('<div class="carousel-feature"')
	entries = []
	for i in range(1, len(spl), 1):
		entry = spl[i]
		try:
			match1 = re.compile('title="(.*?)">', re.DOTALL).findall(entry)
			match2= re.compile('<span class="sub-heading">(.*?)</span>\s+<span class="heading">(.*	?)</span>\s+</li>', re.DOTALL).findall(entry)
			reduce = match2[0][0].strip()
			shorten = match2[0][1].strip()
			if match2[0][1] == match1[0]:
				title = cleanTitle(match2[0][1].strip())
			elif ('...' in match2[0][1] and not '...' in match2[0][0]):
				title = cleanTitle(match1[0].replace(reduce, "").strip())+" - "+cleanTitle(reduce.strip())
			elif ('...' in match2[0][1] and '...' in match2[0][0]):
				title = cleanTitle(match1[0].strip())
			else:
				title = cleanTitle(shorten.strip())+" - "+cleanTitle(match1[0].replace(shorten, "").strip())
			url = re.compile('<a href="(http://www.tvspielfilm.de/mediathek/.*?)"', re.DOTALL).findall(entry)[0]
			img = re.compile('<img src="(http.*?.jpg)"', re.DOTALL).findall(entry)[0]
			if ',' in img:
				thumb = img.split(',')[0].rstrip()+'.jpg'
			else:
				thumb = img
			match3 = re.compile('<span class="logotype chl_bg_m c-.+?">(.*?)</span>', re.DOTALL).findall(entry)
			senderID = cleanTitle(match3[0].strip())
			senderID = cleanSender(senderID.strip())
			if showSender == 'true':
				name = title+senderID
			else:
				name = title
			if showNOW == 'true':
				pass
			else:
				if ("RTL" in senderID or "VOX" in senderID or "SUPER" in senderID):
					continue
			debug("(listVideosAlle) Name - %s" %name)
			debug("(listVideosGenre) Link : %s" %url)
			debug("(listVideosAlle) Icon : %s" %thumb)
			addLink(name, url, 'playVideo', thumb)
		except:
			pass
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode == 'true':
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listVideosGenre(type):
	content = getUrl(baseUrl+"/mediathek/")
	debug("(listVideosGenre) MEDIATHEK : %s/mediathek/ - Genre = *%s*" %(baseUrl, type.upper()))
	if showNOW == 'true':
		debug("(listVideosGenre) --- NowTV - Sender EINGEBLENDET ---")
	else:
		debug("(listVideosGenre) --- NowTV - Sender AUSGEBLENDET ---")
	content = content[content.find('<span>'+type+'</span>')+1:]
	content = content[:content.find('<div class="scroll-box">')]
	spl = content.split('<div class="el"')
	entries = []
	for i in range(1, len(spl), 1):
		entry = spl[i]
		try:
			match1 = re.compile('title="(.*?)">', re.DOTALL).findall(entry)
			match2= re.compile('<strong>(.*?)</strong>\s+<span>(.*?)</span>', re.DOTALL).findall(entry)
			reduce = match2[0][0].strip()
			shorten = match2[0][1].strip()
			if match2[0][0] == match1[0]:
				title = cleanTitle(match2[0][0].strip())
			elif ('...' in match2[0][0] and not '...' in match2[0][1]):
				title = cleanTitle(match1[0].replace(shorten, "").strip())+" - "+cleanTitle(shorten.strip())
			elif ('...' in match2[0][0] and '...' in match2[0][1]):
				title = cleanTitle(match1[0].strip())
			else:
				title = cleanTitle(reduce.strip())+" - "+cleanTitle(match1[0].replace(reduce, "").strip())
			match3 = re.compile('<a href="http://www.tvspielfilm.de/tv-programm/.+?" target="_self" title=".+?">(.*?)</a>', re.DOTALL).findall(entry)
			senderID = cleanTitle(match3[0].strip())
			senderID = cleanSender(senderID.strip())
			url = re.compile('<a href="(http://www.tvspielfilm.de/mediathek/.*?)"', re.DOTALL).findall(entry)[0]
			img = re.compile('<img src="(http.*?.jpg)"', re.DOTALL).findall(entry)[0]
			if ',' in img:
				thumb = img.split(',')[0].rstrip()+'.jpg'
			else:
				thumb = img
			if showSender == 'true':
				name = title+senderID
			else:
				name = title
			if showNOW == 'true':
				pass
			else:
				if ("RTL" in senderID or "VOX" in senderID or "SUPER" in senderID):
					continue
			debug("(listVideosGenre) Name - %s" %name)
			debug("(listVideosGenre) Link : %s" %url)
			debug("(listVideosGenre) Icon : %s" %thumb)
			addLink(name, url, 'playVideo', thumb)
		except:
			pass
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode == 'true':
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playVideo(url):
	xbmc.log("[TvSpielfilm](playVideo) --- START WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)
	xbmc.log("[TvSpielfilm](playVideo) frei", xbmc.LOGNOTICE)
	content = getUrl(url)
	url = re.compile('<div class="film-holder">\s*<a href=\"([^"]+)" class="mediathek-open col-hover-thek".+?\s*<span class="btn-play">Play</span>', re.DOTALL).findall(content)[0]
	finalURL = ""
	xbmc.log("[TvSpielfilm](playVideo) AbspielLink (Original) : %s" %(url), xbmc.LOGNOTICE)
	xbmc.log("[TvSpielfilm](playVideo) frei", xbmc.LOGNOTICE)
	if url.startswith("http://www.arte.tv"):
		videoID = re.compile("http://www.arte.tv/guide/de/([^/]+?)/", re.DOTALL).findall(url)[0]
		xbmc.sleep(1000)
		try:
			pluginID_1 = 'plugin.video.arte_tv'
			plugin1 = xbmcaddon.Addon(id=pluginID_1)
			finalURL = 'plugin://'+plugin1.getAddonInfo('id')+'/?mode=play-video&id='+videoID
			xbmc.log("[TvSpielfilm](playVideo) AbspielLink-1 (ARTE-TV) : %s" %(finalURL), xbmc.LOGNOTICE)
		except:
			try:
				pluginID_2 = 'plugin.video.arteplussept'
				plugin2 = xbmcaddon.Addon(id=pluginID_2)
				finalURL = 'plugin://'+plugin2.getAddonInfo('id')+'/play/'+urllib.quote_plus(videoID)
				xbmc.log("[TvSpielfilm](playVideo) AbspielLink-2 (ARTE-plussept) : %s" %(finalURL), xbmc.LOGNOTICE)
			except:
				if finalURL:
					xbmc.log("[TvSpielfilm](playVideo) AbspielLink-00 (ARTE) : *ARTE-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGERROR)
				else:
					xbmc.log("[TvSpielfilm](playVideo) AbspielLink-00 (ARTE) : KEIN *ARTE-Plugin* zur Wiedergabe vorhanden !!!", xbmc.LOGFATAL)
					xbmc.executebuiltin('Notification(TvSpielfilm : [COLOR red]!!! ADDON - ERROR !!![/COLOR], ERROR = [COLOR red]KEIN *ARTE-Plugin* installiert[/COLOR] - bitte überprüfen ...,6000,'+icon+')')
				pass
	elif (url.startswith("http://www.ardmediathek.de") or url.startswith("http://mediathek.daserste.de")):
		videoID = url.split('documentId=')[1]
		if '&' in videoID:
			videoID = videoID.split('&')[0]
		return ArdGetVideo(videoID)
	elif url.startswith("https://www.zdf.de"):
		url = url[:url.find(".html")]
		videoID = urllib.unquote_plus(url)+".html"
		return ZdfGetVideo(videoID)
	elif url.startswith("http://www.nowtv.de"):
		try:
			match3 = re.compile("/(.+?)/(.+?)/(.+?)/", re.DOTALL).findall(url)
			videoID = match3[2]
			xbmc.sleep(1000)
			pluginID_3 = 'plugin.video.nowtv.de.p'
			plugin3 = xbmcaddon.Addon(id=pluginID_3)
			finalURL = 'plugin://'+plugin3.getAddonInfo('id')+'/?mode=play-video&id='+videoID
		except:
			xbmc.log("[TvSpielfilm](playVideo) AbspielLink-00 (NOWTV) : *NOWTV-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGERROR)
			xbmc.executebuiltin('Notification(TvSpielfilm : [COLOR red]!!! URL - ERROR !!![/COLOR], ERROR = [COLOR red]NowTV - wird derzeit noch NICHT unterstützt ![/COLOR],6000,'+icon+')')
			pass
	if finalURL:
		listitem = xbmcgui.ListItem(name, path=finalURL)
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
		xbmc.log("[TvSpielfilm](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)
	else:
		xbmc.log("[TvSpielfilm](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)

def ArdGetVideo(id):
	try:
		finalURL = False
		mp4URL = ""
		content = getUrl('http://www.ardmediathek.de/play/media/'+id+'?devicetype=pc&features=flash')
		result = json.loads(content)
		muvidLinks = result["_mediaArray"][0]["_mediaStreamArray"]
		normalLinks = result["_mediaArray"][1]["_mediaStreamArray"]
		linkQuality = 3 # Beste verfügbare mp4-Qualität in der ARD-Mediathek = 3 (alle anderen sind schlechter)
		# Beste Qualität ?
		if preferredStreamType == "0" and muvidLinks:
			for muvidLink in muvidLinks:
				stream = muvidLink["_stream"]
				if muvidLink["_quality"] == 'auto' and 'mil/master.m3u8' in stream:
					mp4URL = stream
					xbmc.log("[TvSpielfilm](ArdGetVideo) m3u8-Stream (ARD+3) : %s" %(str(mp4URL)), xbmc.LOGNOTICE)
		if normalLinks and mp4URL == "":
			if linkQuality == -1:
				linkQuality = 0
				for normalLink in normalLinks:
					if normalLink["_quality"] > linkQuality and '_stream' in normalLink:
						linkQuality = normalLink["_quality"]
			xbmc.log("[TvSpielfilm](ArdGetVideo) LINK-Qualität (ARD+3) : %s" %(str(linkQuality)), xbmc.LOGNOTICE)
			for normalLink in normalLinks:
				if linkQuality != normalLink["_quality"]:
					continue
				stream = normalLink["_stream"]
				# Überprüfen, ob die ausgewählte Qualität zwei Streams enthält
				if type(stream) is list or type(stream) is tuple:
					if len(stream) > 1:
						mp4URL = stream[0]
						xbmc.log("[TvSpielfilm](ArdGetVideo) Wir haben 2 Streams (ARD+3) - wähle den 1 : %s" %(str(mp4URL)), xbmc.LOGNOTICE)
					else:
						mp4URL = stream[0]
						xbmc.log("[TvSpielfilm](ArdGetVideo) Wir haben 1 Stream (ARD+3) in der Liste : %s" %(str(mp4URL)), xbmc.LOGNOTICE)
				else:
					mp4URL = stream
					xbmc.log("[TvSpielfilm](ArdGetVideo) Wir haben 1 Stream (ARD+3) - wähle Diesen : %s" %(str(mp4URL)), xbmc.LOGNOTICE)
		# *mp4URL* überprüfen, Qualität nachbessern, danach abspielen
		finalURL = mp4URL.replace('.hq.mp4', '.hd.mp4').replace('.ln.mp4', '.hq.mp4').replace('.l.mp4', '.xl.mp4').replace('_C.mp4', '_X.mp4')
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
		pass
	xbmc.log("[TvSpielfilm](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)

def ndrPodcastHack(url):
	try:
		if url.startswith('http://media.ndr.de/download/podcasts/'):
			uri = url.split('/')[-1]
			YYYYMMDD = uri.split('-')[1]
			YYYY = YYYYMMDD[:4]
			MMDD = YYYYMMDD[4:]
			return 'http://hls.ndr.de/i/ndr/'+ YYYY +'/'+ MMDD +'/'+ uri
	except:
		pass
	return url

def dwHack(url):
	try:
		if url.startswith('http://tv-download.dw.de'):
			return url.replace('_sd.mp4','_hd_dwdownload.mp4')
	except:
		pass
	return url

def ZdfGetVideo(url):
	try:
		content = getUrl(url)
		link = re.compile('"content": "(.*?)",', re.DOTALL).findall(content)[0]
		response = getUrl(link,getheader)
		ID = re.compile('"uurl":"(.*?)",', re.DOTALL).findall(response)[0]
		LinkDirekt = getUrl("https://api.zdf.de/tmd/2/portal/vod/ptmd/mediathek/"+ID)
		#LinkDirekt2 = getUrl("https://api.zdf.de/tmd/2/ngplayer_2_3/vod/ptmd/mediathek/"+ID)
		jsonObject = json.loads(LinkDirekt)
		return ZdfExtractQuality(jsonObject)
	except:
		xbmc.log("[TvSpielfilm](ZdfGetVideo) AbspielLink-00 (ZDF+3) : *ZDF-Plugin* Der angeforderte -VideoLink- existiert NICHT !!!", xbmc.LOGERROR)
		xbmc.log("[TvSpielfilm](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)
		xbmc.executebuiltin('Notification(TvSpielfilm : [COLOR red]!!! VideoURL - ERROR !!![/COLOR], ERROR = [COLOR red]Der angeforderte *VideoLink* existiert NICHT ![/COLOR],6000,'+icon+')')
		pass

def ZdfExtractQuality(jsonObject):
	try:
		DATA = {}
		DATA['media'] = []
		finalURL = False
		mp4URL = ""
		for each in jsonObject['priorityList']:
			if preferredStreamType == "0" and each['formitaeten'][0]['type'] == 'h264_aac_ts_http_m3u8_http':
				for quality in each['formitaeten'][0]['qualities']:
					if quality['quality'] == 'auto':
						DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
					else:
						if quality['quality'] == 'hd':
							DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
						elif quality['quality'] == 'veryhigh':
							DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
						elif quality['quality'] == 'high':
							DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
				zdfURL = DATA['media'][0]['url']
				mp4URL = zdfURL
				xbmc.log("[TvSpielfilm](ZdfExtractQuality) m3u8-Stream (ZDF+3) : %s" %(mp4URL), xbmc.LOGNOTICE)
			if each['formitaeten'][0]['type'] == 'h264_aac_mp4_http_na_na' and mp4URL == "":
				for quality in each['formitaeten'][0]['qualities']:
					if quality['quality'] == 'auto':
						DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
					else:
						if quality['quality'] == 'hd':
							DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
						elif quality['quality'] == 'veryhigh':
							DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
						elif quality['quality'] == 'high':
							DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
				# *zdfURL* überprüfen, Qualität nachbessern, danach abspielen
				zdfURL = DATA['media'][0]['url']
				xbmc.log("[TvSpielfilm](ZdfExtractQuality) ZDF-STANDARDurl : %s" %(zdfURL), xbmc.LOGNOTICE)
				higherURL =  zdfURL.replace('1456k_p13v11', '2328k_p35v11').replace('1456k_p13v12', '2328k_p35v12').replace('1496k_p13v13', '2328k_p35v13').replace('2256k_p14v11', '2328k_p35v11').replace('2256k_p14v12', '2328k_p35v12').replace('2296k_p14v13', '2328k_p35v13')
				if ('2328k_p35v11' in higherURL or '2328k_p35v12' in higherURL or '2328k_p35v13' in higherURL):
					hdURL = higherURL.replace('2328k_p35v12', '3328k_p36v12').replace('2328k_p35v13', '3328k_p36v13')
					if ('3328k_p36v12' in hdURL or '3328k_p36v13' in hdURL):
						mp4URL = hdURL
						xbmc.log("[TvSpielfilm](ZdfExtractQuality) ZDF-HDurl : %s" %(mp4URL), xbmc.LOGNOTICE)
					else:
						mp4URL = higherURL
						xbmc.log("[TvSpielfilm](ZdfExtractQuality) ZDF-HIGHERurl : %s" %(mp4URL), xbmc.LOGNOTICE)
				else:
					mp4URL = zdfURL
					xbmc.log("[TvSpielfilm](ZdfExtractQuality) ZDF-ZDFurl : %s" %(mp4URL), xbmc.LOGNOTICE)
		finalURL = mp4URL
		if not finalURL:
			xbmc.log("[TvSpielfilm](ZdfExtractQuality) AbspielLink-00 (ZDF+3) : *ZDF-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGERROR)
		else:
			listitem = xbmcgui.ListItem(name, path=finalURL)
			xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
			xbmc.log("[TvSpielfilm](ZdfExtractQuality) END-Qualität (ZDF+3) : %s" %(finalURL), xbmc.LOGNOTICE)
	except:
		xbmc.log("[TvSpielfilm](ZdfExtractQuality) AbspielLink-00 (ZDF+3) : *ZDF-Plugin* Fehler bei Anforderung des AbspielLinks !!!", xbmc.LOGERROR)
		pass
	xbmc.log("[TvSpielfilm](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)

def queueVideo(url,name,thumb):
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	listitem = xbmcgui.ListItem(name,iconImage=thumb,thumbnailImage=thumb)
	playlist.add(url,listitem)

def getUrl(url,headers=False):
	req = urllib2.Request(url)
	if headers:
		for key in headers:
			req.add_header(key, headers[key])
	else:
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/32.0')
		req.add_header('Accept-Encoding','gzip,deflate')
	response = urllib2.urlopen(req)
	if response.info().get('Content-Encoding') == 'gzip':
		buf = StringIO(response.read())
		f = gzip.GzipFile(fileobj=buf)
		link = f.read()
		f.close()
	else:
		link = response.read()
		response.close()
	return link

def cleanTitle(title):
	title = title.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('amp;', '').replace('&#39;', '\'').replace('&#039;', '\'').replace('&quot;', '"').replace('&szlig;', 'ß').replace('&ndash;', '-').replace('#', '')
	title = title.replace('&#x00c4', 'Ä').replace('&#x00e4', 'ä').replace('&#x00d6', 'Ö').replace('&#x00f6', 'ö').replace('&#x00dc', 'Ü').replace('&#x00fc', 'ü').replace('&#x00df', 'ß')
	title = title.replace('&Auml;', 'Ä').replace('&Ouml;', 'Ö').replace('&Uuml;', 'Ü').replace('&auml;', 'ä').replace('&ouml;', 'ö').replace('&uuml;', 'ü')
	title = title.replace('&agrave;', 'à').replace('&aacute;', 'á').replace('&acirc;', 'â').replace('&egrave;', 'è').replace('&eacute;', 'é').replace('&ecirc;', 'ê').replace('&igrave;', 'ì').replace('&iacute;', 'í').replace('&icirc;', 'î')
	title = title.replace('&ograve;', 'ò').replace('&oacute;', 'ó').replace('&ocirc;', 'ô').replace('&ugrave;', 'ù').replace('&uacute;', 'ú').replace('&ucirc;', 'û')
	title = title.replace("\\'", "'").replace('-<wbr/>', '').replace('<br />', ' -').replace(" ", ".").replace('Ã¶', 'ö')
	title = title.strip()
	return title

def cleanSender(senderID):
	ChannelCode = ('ARD','Das Erste','ONE','ZDF','2NEO','ZNEO','ZINFO','3SAT','Arte','ARTE','BR','HR','MDR','NDR','N3','ORF','PHOEN','RBB','SR','SWR','SWR/SR','WDR','RTL','RTL2','VOX','SRTL','SUPER')
	if senderID in ChannelCode and senderID != "":
		try:
			senderID = senderID.replace(' ', '')
			if 'ARD' in senderID:
				senderID = '  (DasErste)'
			elif 'ONE' in senderID:
				senderID = '  (ARDone)'
			elif 'Arte' in senderID:
				senderID = '  (ARTE)'
			elif '2NEO' in senderID or 'ZNEO' in senderID:
				senderID = '  (ZDFneo)'
			elif 'ZINFO' in senderID:
				senderID = '  (ZDFinfo)'
			elif '3SAT' in senderID:
				senderID = '  (3sat)'
			elif 'NDR' in senderID or 'N3' in senderID:
				senderID = '  (NDR)'
			elif 'PHOEN' in senderID:
				senderID = '  (PHOENIX)'
			elif 'SR' in senderID or 'SWR' in senderID:
				senderID = '  (SWR)'
			else:
				senderID = '  ('+senderID+')'
		except:
			pass
	elif not senderID in ChannelCode and senderID != "":
		senderID = '  ('+senderID+')'
	else:
		senderID = ""
	return senderID

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def addDir(name, url, mode, iconimage):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&thumb="+urllib.quote_plus(iconimage)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	if useThumbAsFanart:
		if not iconimage or iconimage==icon or iconimage==fanart:
			iconimage = fanart
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", fanart)
	ok = xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=liz, isFolder=True)
	return ok

def addLink(name, url, mode, iconimage, plot="", duration="", date=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	plot = plot.decode("UTF-8")
	liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Duration": duration})
	liz.setProperty("IsPlayable", "true")
	if useThumbAsFanart and iconimage:
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", fanart)
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	entries = []
	entries.append((translation(30201),'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+'&thumb='+urllib.quote_plus(iconimage)+')',))
	liz.addContextMenuItems(entries)
	ok = xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=liz, isFolder=False)
	return ok

params = parameters_string_to_dict(sys.argv[2])
name = urllib.unquote_plus(params.get('name', ''))
url = urllib.unquote_plus(params.get('url', ''))
mode = urllib.unquote_plus(params.get('mode', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
plot = urllib.unquote_plus(params.get('plot', ''))

if mode == 'listVideosNachTag':
	listVideosNachTag(url)
elif mode == 'listVideosAlle':
	listVideosAlle()
elif mode == 'listVideosGenre':
	listVideosGenre(url)
elif mode == 'playVideo':
	playVideo(url)
elif mode == 'queueVideo':
	queueVideo(url,name,thumb)
else:
	index()