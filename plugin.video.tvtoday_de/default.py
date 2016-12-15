#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, os, json
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib, urllib2
import urlparse
import re, string
from datetime import date,datetime,timedelta
import time
import socket
from StringIO import StringIO
import gzip

token = '23a1db22b51b13162bd0b86b24e556c8c6b6272d reraeB'
getheader = {'Api-Auth': token[::-1]}

main_url = sys.argv[0]
pluginhandle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

addonID = 'plugin.video.tvtoday_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(40)
translation = addon.getLocalizedString
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).decode('utf-8')
dataPath = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
fanart = os.path.join(addonPath, 'fanart.jpg').decode('utf-8')
icon = os.path.join(addonPath, 'icon.png').decode('utf-8')
showSender = addon.getSetting("enableSender")
showNOW = addon.getSetting("enableTVnow")
enableDebug = addon.getSetting("enableDebug")
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == 'true'
forceViewMode = addon.getSetting("forceView") 
viewMode = str(addon.getSetting("viewID"))
baseUrl = "http://www.tvtoday.de"
dateUrl = "/mediathek/nach-datum/"


if not os.path.isdir(dataPath):
	os.makedirs(dataPath)


def debug(msg, level=xbmc.LOGNOTICE):
	if enableDebug == 'true':
		xbmc.log('[TvToday]'+msg, level)

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

	addDir("Auswahl vom "+w1+", den "+m1, baseUrl+dateUrl+s1+".html", 'listVideosNachTag', icon)
	addDir("Auswahl vom "+w2+", den "+m2, baseUrl+dateUrl+s2+".html", 'listVideosNachTag', icon)
	addDir("Auswahl vom "+w3+", den "+m3, baseUrl+dateUrl+s3+".html", 'listVideosNachTag', icon)
	addDir("Auswahl vom "+w4+", den "+m4, baseUrl+dateUrl+s4+".html", 'listVideosNachTag', icon)
	addDir("Auswahl vom "+w5+", den "+m5, baseUrl+dateUrl+s5+".html", 'listVideosNachTag', icon)
	addDir("* Spielfilme *", "Spielfilm", 'listVideosGenre', icon)
	addDir("* Serien *", "Serie", 'listVideosGenre', icon)
	addDir("* Reportagen *", "Reportage", 'listVideosGenre', icon)
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
		debug("(listVideosNachTag) --- NowTV - Sender möglichst AUSGEBLENDET ---")
	content = content[content.find('<section data-style="modules/movie-starts"')+1:]
	content = content[:content.find('<aside class="module" data-style="modules/marginal')]
	spl = content.split('<div data-style="elements/teaser/teaser-l"')
	entries = []
	for i in range(1, len(spl), 1):
		entry = spl[i]
		try:
			match1 = re.compile('<img alt="(.*?)"', re.DOTALL).findall(entry)
			match2= re.compile('<p class="h2">(.*?)</p>.+?<span class="date">(.*?)/span>', re.DOTALL).findall(entry)
			if (match2[0][0] and match2[0][1]):
				title = cleanTitle(match2[0][0].strip())+" - "+cleanTitle(match2[0][1].replace(", <", " ").replace(",<", " ").replace("<", "").strip())
			else:
				title = cleanTitle(match1[0].strip())
			url = re.compile('<a class="img-box" href="(.*?.html)">', re.DOTALL).findall(entry)[0]
			if not baseUrl in url:
				fullUrl = baseUrl+url
			else:
				fullUrl = url
			thumb = re.compile('src="(http.*?.jpg)"', re.DOTALL).findall(entry)[0]
			match3 = re.compile('data-credit="(.*?)">', re.DOTALL).findall(entry)
			senderID = cleanTitle(match3[0].strip())
			senderID = cleanSender(senderID.strip())
			match4 = re.compile('<p class="short-copy">(.*?)</p>', re.DOTALL).findall(entry)
			plot = cleanTitle(match4[0].strip())
			if showSender == 'true':
				name = title+senderID
			else:
				name = title
			if showNOW == 'true':
				pass
			else:
				if ("RTL" in senderID or "VOX" in senderID):
					continue
			debug("(listVideosNachTag) Name - %s" %name)
			debug("(listVideosNachTag) Link : %s" %fullUrl)
			debug("(listVideosNachTag) Icon : %s" %thumb)
			addLink(name, fullUrl, 'playVideo', thumb, plot)
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
	content = content[content.find('<h3 class="h3 uppercase category-headline">'+type+'</h3>')+1:]
	content = content[:content.find('<div class="banner-container">')]
	spl = content.split('<div class="slide js-slide"')
	entries = []
	for i in range(1, len(spl), 1):
		entry = spl[i]
		try:
			match1 = re.compile('alt="(.*?)"', re.DOTALL).findall(entry)
			match2 = re.compile('<p class="h7 name">(.*?)</p>', re.DOTALL).findall(entry)
			if match2 != "":
				title = cleanTitle(match2[0].strip())
			else:
				title = cleanTitle(match1[0].strip())
			match3 = re.compile('<span class="h6 text">(.*?)</span>', re.DOTALL).findall(entry)
			senderID = cleanTitle(match3[0].strip())
			senderID = cleanSender(senderID.strip())
			url = re.compile('<span class="logo chl_bg_m c-.+?\s+</a>\s+<a href="(.*?.html)" class="element js-hover', re.DOTALL).findall(entry)[0]
			thumb = re.compile('data-lazy-load-src="(http.*?.jpg)"', re.DOTALL).findall(entry)[0]
			if "mediathek/nach-sender" in url:
				continue
			if not baseUrl in url:
				fullUrl = baseUrl+url
			else:
				fullUrl = url
			match4 = re.compile('<p class="small-meta description">(.*?)</p>', re.DOTALL).findall(entry)
			plot = cleanTitle(match4[0].strip())
			if showSender == 'true':
				name = title+senderID
			else:
				name = title
			if showNOW == 'true':
				pass
			else:
				if ("RTL" in senderID or "VOX" in senderID):
					continue
			debug("(listVideosGenre) Name - %s" %name)
			debug("(listVideosGenre) Link : %s" %fullUrl)
			debug("(listVideosGenre) Icon : %s" %thumb)
			addLink(name, fullUrl, 'playVideo', thumb, plot)
		except:
			pass
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode == 'true':
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playVideo(url):
	xbmc.log("[TvToday](playVideo) --- START WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)
	xbmc.log("[TvToday](playVideo) frei", xbmc.LOGNOTICE)
	content = getUrl(url)
	url = re.compile('<div class="img-wrapper stage">\s*<a href=\"([^"]+)" \s*target=', re.DOTALL).findall(content)[0]
	finalUrl = ""
	xbmc.log("[TvToday](playVideo) AbspielLink (Original) : %s" %(url), xbmc.LOGNOTICE)
	xbmc.log("[TvToday](playVideo) frei", xbmc.LOGNOTICE)
	if url.startswith("http://www.arte.tv"):
		videoID = re.compile("http://www.arte.tv/guide/de/([^/]+?)/", re.DOTALL).findall(url)[0]
		xbmc.sleep(1000)
		try:
			pluginID_1 = 'plugin.video.arte_tv'
			plugin1 = xbmcaddon.Addon(id=pluginID_1)
			finalUrl = 'plugin://'+plugin1.getAddonInfo('id')+'/?mode=play-video&id='+videoID
			xbmc.log("[TvToday](playVideo) AbspielLink-1 (ARTE-TV) : %s" %(finalUrl), xbmc.LOGNOTICE)
		except:
			try:
				pluginID_2 = 'plugin.video.arteplussept'
				plugin2 = xbmcaddon.Addon(id=pluginID_2)
				finalUrl = 'plugin://'+plugin2.getAddonInfo('id')+'/play/'+urllib.quote_plus(videoID)
				xbmc.log("[TvToday](playVideo) AbspielLink-2 (ARTE-plussept) : %s" %(finalUrl), xbmc.LOGNOTICE)
			except:
				if finalUrl:
					xbmc.log("[TvToday](playVideo) AbspielLink-00 (ARTE) : *ARTE-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGERROR)
				else:
					xbmc.log("[TvToday](playVideo) AbspielLink-00 (ARTE) : KEIN *ARTE-Plugin* zur Wiedergabe vorhanden !!!", xbmc.LOGFATAL)
					xbmc.executebuiltin('Notification(TvToday : [COLOR red]!!! ADDON - ERROR !!![/COLOR], ERROR = [COLOR red]KEIN *ARTE-Plugin* installiert[/COLOR] - bitte überprüfen ...,6000,'+icon+')')
				pass
	elif (url.startswith("http://www.ardmediathek.de") or url.startswith("http://mediathek.daserste.de")):
		import libArd
		try:
			videoID = url.split('documentId=')[1]
			if '&' in videoID:
				videoID = videoID.split('&')[0]
			videoUrl,subUrl = libArd.getVideoUrl(videoID)
			xbmc.sleep(1000)
			finalUrl = str(videoUrl)
			xbmc.log("[TvToday](playVideo) AbspielLink (ARD+3) : %s" %(finalUrl), xbmc.LOGNOTICE)
		except:
			xbmc.log("[TvToday](playVideo) AbspielLink-00 (ARD+3) : *ARD-Plugin* Der angeforderte -VideoLink- existiert NICHT !!!", xbmc.LOGERROR)
			xbmc.executebuiltin('Notification(TvToday : [COLOR red]!!! VideoURL - ERROR !!![/COLOR], ERROR = [COLOR red]Der angeforderte *VideoLink* existiert NICHT ![/COLOR],6000,'+icon+')')
			pass
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
			finalUrl = 'plugin://'+plugin3.getAddonInfo('id')+'/?mode=play-video&id='+videoID
		except:
			xbmc.log("[TvToday](playVideo) AbspielLink-00 (NOWTV) : *NOWTV-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGERROR)
			xbmc.executebuiltin('Notification(TvToday : [COLOR red]!!! URL - ERROR !!![/COLOR], ERROR = [COLOR red]NowTV - wird derzeit noch NICHT unterstützt ![/COLOR],6000,'+icon+')')
			pass
	if not url.startswith("https://www.zdf.de"):
		xbmc.log("[TvToday](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)
	if finalUrl:
		listitem = xbmcgui.ListItem(name, path=finalUrl)
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def ZdfGetVideo(url):
	try:
		content = getUrl(url)
		link = re.compile('"content": "(.*?)",', re.DOTALL).findall(content)[0]
		response = getUrl(link,getheader)
		ID = re.compile('"uurl":"(.*?)",', re.DOTALL).findall(response)[0]
		LinkDirekt = getUrl("https://api.zdf.de//tmd/2/portal/vod/ptmd/mediathek/"+ID)
		#LinkDownload = getUrl("https://api.zdf.de/tmd/2/ngplayer_2_3/vod/ptmd/mediathek/"+ID)
		jsonObject = json.loads(LinkDirekt)
		return extractLinks(jsonObject)
	except:
		xbmc.log("[TvToday](playVideo) AbspielLink-00 (ZDF+3) : *ZDF-Plugin* Der angeforderte -VideoLink- existiert NICHT !!!", xbmc.LOGERROR)
		xbmc.executebuiltin('Notification(TvToday : [COLOR red]!!! VideoURL - ERROR !!![/COLOR], ERROR = [COLOR red]Der angeforderte *VideoLink* existiert NICHT ![/COLOR],6000,'+icon+')')
		pass

def extractLinks(jsonObject):
	DATA = {}
	DATA['media'] = []
	try:
		for each in jsonObject['priorityList']:
			if each['formitaeten'][0]['type'] == 'h264_aac_ts_http_m3u8_http':
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
						elif quality['quality'] == 'med':
							DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
						elif quality['quality'] == 'low':
							DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
					finalUrl = DATA['media'][0]['url']
					xbmc.log("[TvToday](extractLinks) m3u8-Quality (ZDF+3) : %s" %(finalUrl), xbmc.LOGNOTICE)
	except:
		try:
			for each in jsonObject['priorityList']:
				if each['formitaeten'][0]['type'] == 'h264_aac_mp4_http_na_na':
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
							elif quality['quality'] == 'med':
								DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
							elif quality['quality'] == 'low':
								DATA['media'].append({'url':quality['audio']['tracks'][0]['uri'], 'type': 'video', 'stream':'HLS'})
						finalUrl = DATA['media'][0]['url']
						xbmc.log("[TvToday](extractLinks) mp4-Quality (ZDF+3) : %s" %(finalUrl), xbmc.LOGNOTICE)
		except:
			pass
	if finalUrl:
		listitem = xbmcgui.ListItem(name, path=str(finalUrl))
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	else:
		xbmc.log("[TvToday](extractLinks) AbspielLink-00 (ZDF+3) : *ZDF-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGERROR)
	xbmc.log("[TvToday](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)

def queueVideo(url,name,thumb):
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	listitem = xbmcgui.ListItem(name,iconImage=thumb,thumbnailImage=thumb)
	playlist.add(url,listitem)

def getUrl(url,headers={}):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/25.0')
	req.add_header('Accept-Encoding','gzip,deflate')
	for key in headers:
		req.add_header(key, headers[key])
	response = urllib2.urlopen(req)
	if response.info().get('Content-Encoding') == 'gzip':
		buf = StringIO(response.read())
		f = gzip.GzipFile(fileobj=buf)
		link = f.read()
		f.close()
	else:
		link = response.read().decode('utf-8', 'ignore').encode('utf-8', 'ignore')
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
	ChannelCode = ('ARD','Das Erste','ONE','ZDF','2NEO','ZNEO','ZINFO','3SAT','Arte','ARTE','BR','HR','MDR','NDR','N3','ORF','PHOEN','RBB','SR','SWR','SWR/SR','WDR','RTL','RTL2','VOX','SRTL')
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
elif mode == 'listVideosGenre':
	listVideosGenre(url)
elif mode == 'playVideo':
	playVideo(url)
elif mode == 'queueVideo':
	queueVideo(url,name,thumb)
else:
	index()