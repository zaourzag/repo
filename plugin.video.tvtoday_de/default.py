# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, os, json
import urllib, urllib2
import re, string
from datetime import date,datetime,timedelta
import time, socket


pluginhandle = int(sys.argv[1])
socket.setdefaulttimeout(30)
addonID = 'plugin.video.tvtoday_de'
addon = xbmcaddon.Addon(id=addonID)
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).decode('utf-8')
dataPath = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
translation = addon.getLocalizedString
fanart = os.path.join(addonPath, 'fanart.jpg').decode('utf-8')
icon = os.path.join(addonPath, 'icon.png').decode('utf-8')
showSender = addon.getSetting("enableSender")
enableDebug = addon.getSetting("enableDebug")
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == 'true'
forceViewMode = addon.getSetting("forceView") 
viewMode = str(addon.getSetting("viewID"))
baseUrl = "http://www.tvtoday.de"
dateUrl = "/mediathek/nach-datum/"


if not os.path.isdir(dataPath):
	os.mkdir(dataPath)


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
	content = content[content.find('<section data-style="modules/movie-starts"')+1:]
	spl = content.split('<div data-style="elements/teaser/teaser-l"')
	entries = []
	for i in range(1, len(spl), 1):
		entry = spl[i]
		if "RTL" not in entry and "RTL2" not in entry and "VOX" not in entry and "SRTL" not in entry:
			match1= re.compile('<p class="h2">(.*?)</p>.+?<span class="date">(.*?)</span>', re.DOTALL).findall(entry)
			match2 = re.compile('<img alt="(.*?)"', re.DOTALL).findall(entry)
			if match1:
				title = cleanTitle(match1[0][0].strip())+" - "+cleanTitle(match1[0][1].strip())
			elif match2:
				title = cleanTitle(match2[0].strip())
			match3 = re.compile('<p class="short-copy">(.*?)</p>', re.DOTALL).findall(entry)
			plot = cleanTitle(match3[0].strip())
			url = re.compile('href="(.*?)">', re.DOTALL).findall(entry)[0]
			if not baseUrl in url:
				fullUrl = baseUrl+url
			else:
				fullUrl = url
			thumb = re.compile('src="(.*?).jpg"', re.DOTALL).findall(entry)[0]
			thumb = thumb+".jpg"
			match6 = re.compile('data-credit="(.*?)">', re.DOTALL).findall(entry)
			senderID = cleanSender(match6[0].strip())
			if showSender == 'true':
				name = title+senderID
			else:
				name = title
			debug("(listVideosNachTag) Name - %s" %name)
			debug("(listVideosNachTag) Link : %s" %fullUrl)
			debug("(listVideosNachTag) Icon : %s" %thumb)
			addLink(name, fullUrl, 'playVideo', thumb, plot)
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode == 'true':
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listVideosGenre(type):
	content = getUrl(baseUrl+"/mediathek")
	debug("(listVideosGenre) MEDIATHEK : %s/mediathek/ - Genre = *%s*" %(baseUrl, type.upper()))
	content = content[content.find('<h3 class="h3 uppercase category-headline">'+type+'</h3>'):]
	content = content[:content.find('<div class="banner-container">')]
	match = re.compile('href="([^"]+)".*?src="([^"]+).jpg"\s+alt="(.*?)"(.*?)<span class="logo chl_bg_m', re.DOTALL).findall(content)
	for url, thumb, title, chtml in match:
		if 'mediathek/nach-sender' in url or '#' in url:
			continue
		if not baseUrl in url:
			fullUrl = baseUrl+url
		else:
			fullUrl = url
		thumb = thumb+".jpg"
		title = cleanTitle(title.strip())
		match4 = re.compile('data-credit="(.*?)"', re.DOTALL).findall(chtml)
		senderID = cleanSender(match4[0].strip())
		if "RTL" in senderID or "RTL2" in senderID or "VOX" in senderID or "SRTL" in senderID:
			continue
		if title == "":
			match5 = re.compile('<p class="h7 name">([^"]+)</p>', re.DOTALL).findall(chtml)
			title = cleanTitle(match5[0].strip())
		match6 = re.compile('<p class="small-meta description">(.*?)</p>', re.DOTALL).findall(chtml)
		plot = cleanTitle(match6[0].strip())
		if showSender == 'true':
			name = title+senderID
		else:
			name = title
		debug("(listVideosGenre) Name - %s" %name)
		debug("(listVideosGenre) Link : %s" %fullUrl)
		debug("(listVideosGenre) Icon : %s" %thumb)
		addLink(name, fullUrl, 'playVideo', thumb, plot)
	xbmcplugin.endOfDirectory(pluginhandle)
	if forceViewMode == 'true':
		xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playVideo(urlMain):
	xbmc.log("[TvToday](playVideo) --- START WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)
	xbmc.log("[TvToday](playVideo) frei", xbmc.LOGNOTICE)
	content = getUrl(urlMain)
	url = re.compile('<div class="img-wrapper stage">\s*<a href=\"([^"]+)" \s*target=', re.DOTALL).findall(content)[0]
	finalUrl = ""
	xbmc.log("[TvToday](playVideo) AbspielLink (Original) : %s" %(url), xbmc.LOGNOTICE)
	xbmc.log("[TvToday](playVideo) frei", xbmc.LOGNOTICE)
	if url.startswith("http://www.arte.tv"):
		id = re.compile("http://www.arte.tv/guide/de/([^/]+?)/", re.DOTALL).findall(url)[0]
		xbmc.sleep(1000)
		try:
			xbmcaddon.Addon('plugin.video.arte_tv')
			finalUrl ='plugin://plugin.video.arte_tv/?mode=play-video&id='+id
			xbmc.log("[TvToday](playVideo) AbspielLink-1 (ARTE-TV) : %s" %(finalUrl), xbmc.LOGNOTICE)
		except:
			try:
				xbmcaddon.Addon('plugin.video.arteplussept')
				finalUrl ='plugin://plugin.video.arteplussept/play/'+urllib.quote_plus(id)
				xbmc.log("[TvToday](playVideo) AbspielLink-2 (ARTE-plussept) : %s" %(finalUrl), xbmc.LOGNOTICE)
			except:
				if finalUrl:
					xbmc.log("[TvToday](playVideo) AbspielLink-00 (ARTE) : *ARTE-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGFATAL)
				else:
					xbmc.log("[TvToday](playVideo) AbspielLink-00 (ARTE) : *KEIN *ARTE-Plugin* zur Wiedergabe vorhanden !!!", xbmc.LOGFATAL)
	elif url.startswith("http://mediathek.daserste.de"):
		import libArd
		url = re.compile('documentId=([0-9]+)', re.DOTALL).findall(content)[0]
		videoID = urllib.quote_plus(url)
		videoUrl,subUrl = libArd.getVideoUrl(videoID)
		xbmc.sleep(1000)
		finalUrl = str(videoUrl)
		if finalUrl:
			xbmc.log("[TvToday](playVideo) AbspielLink (DasErste) : %s" %(finalUrl), xbmc.LOGNOTICE)
		else:
			xbmc.log("[TvToday](playVideo) AbspielLink-00 (DasErste) : *DasErste-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGFATAL)
	elif url.startswith("http://www.ardmediathek.de"):
		import libArd
		url = url[url.find("documentId=")+11:]
		if "&" in url:
			url = url[:url.find("&")]
		videoID = urllib.quote_plus(url)
		videoUrl,subUrl = libArd.getVideoUrl(videoID)
		xbmc.sleep(1000)
		finalUrl = str(videoUrl)
		if finalUrl:
			xbmc.log("[TvToday](playVideo) AbspielLink (ARD+3) : %s" %(finalUrl), xbmc.LOGNOTICE)
		else:
			xbmc.log("[TvToday](playVideo) AbspielLink-00 (ARD+3) : *ARD+3-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGFATAL)
	elif url.startswith("https://www.zdf.de"):
		import libZdf
		# libZdf.libZdfGetVideoHtml('https://www.zdf.de/uri/vcms_beitrag_'+result)
		url = url[:url.find(".html")]
		videoID = urllib.unquote_plus(url)+".html"
		xbmc.log("[TvToday](playVideo) AbspielLink-1 (ZDF+3) : %s" %(videoID), xbmc.LOGNOTICE)
		finalUrl = libZdf.libZdfGetVideoHtml(videoID)
		if finalUrl:
			xbmc.log("[TvToday](playVideo) AbspielLink-2 (ZDF+3) : %s" %(finalUrl), xbmc.LOGNOTICE)
		else:
			xbmc.log("[TvToday](playVideo) AbspielLink-00 (ZDF+3) : *ZDF-Plugin* VIDEO konnte NICHT abgespielt werden !!!", xbmc.LOGFATAL)
	xbmc.log("[TvToday](playVideo) frei", xbmc.LOGNOTICE)
	xbmc.log("[TvToday](playVideo) --- ENDE WIEDERGABE ANFORDERUNG ---", xbmc.LOGNOTICE)
	if finalUrl:
		listitem = xbmcgui.ListItem(path=finalUrl)
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def queueVideo(url, name):
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	listitem = xbmcgui.ListItem(name)
	playlist.add(url, listitem)

def getUrl(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/22.0')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()
	return link

def cleanTitle(title):
	title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("amp;", "").replace("&#39;", "\"").replace("&#039;", "\"").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-").replace("#", "")
	title = title.replace("&#x00c4", "Ä").replace("&#x00e4", "ä").replace("&#x00d6", "Ö").replace("&#x00f6", "ö").replace("&#x00dc", "Ü").replace("&#x00fc", "ü").replace("&#x00df", "ß")
	title = title.replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml;", "Ü").replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml;", "ü")
	title = title.replace("&agrave;", "à").replace("&aacute;", "á").replace("&acirc;", "â").replace("&egrave;", "è").replace("&eacute;", "é").replace("&ecirc;", "ê").replace("&igrave;", "ì").replace("&iacute;", "í").replace("&icirc;", "î")
	title = title.replace("&ograve;", "ò").replace("&oacute;", "ó").replace("&ocirc;", "ô").replace("&ugrave;", "ù").replace("&uacute;", "ú").replace("&ucirc;", "û")
	title = title.replace("\\'", "'").replace("<wbr/>", "").replace("<br />", " -").replace(" ", ".")
	title = title.strip()
	return title

def cleanSender(senderID):
	ChannelCode = ( 'ARD','MUX,''FES','ZDF','2NEO','ZINFO','2KULT','3SAT','ARTE','BR','HR','MDR','NDR','N3','ORF','PHOEN','RBB','SR','SWR','WDR','RTL','RTL2','VOX','SRTL')
	if senderID in ChannelCode and senderID != "":
		try:
			if 'ARD' in senderID:
				senderID = ' (DasErste) '
			elif 'MUX' in senderID:
				senderID = ' (EinsPlus) '
			elif 'FES' in senderID:
				senderID = ' (EinsFestival) '
			elif '2NEO' in senderID:
				senderID = ' (ZDFneo) '
			elif 'ZINFO' in senderID:
				senderID = ' (ZDFinfo) '
			elif '2KULT' in senderID:
				senderID = ' (ZDFkultur) '
			elif '3SAT' in senderID:
				senderID = ' (3sat) '
			elif 'NDR' in senderID or 'N3' in senderID:
				senderID = ' (NDR) '
			elif 'PHOEN' in senderID:
				senderID = ' (PHOENIX) '
			elif 'SR' in senderID or 'SWR' in senderID:
				senderID = ' (SWR) '
			else:
				senderID = ' ('+senderID+') '
		except:
			pass
	elif not senderID in ChannelCode and senderID != "":
		senderID = ' ('+senderID+') '
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

def addLink(name, url, mode, iconimage, desc="", duration="", date=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Aired": date, "Duration": duration})
	liz.setProperty('IsPlayable', 'true')
	liz.addStreamInfo('video', { 'duration' : duration })
	if useThumbAsFanart and iconimage:
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", fanart)
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	liz.addContextMenuItems([(translation(30001), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',)])
	ok = xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=liz, isFolder=False)
	return ok

def addDir(name, url, mode, iconimage, desc=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)+"&desc="+urllib.quote_plus(desc)
	ok = True
	desc = desc.decode("iso-8859-1")
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	if useThumbAsFanart:
		if not iconimage or iconimage==icon or iconimage==fanart:
			iconimage = fanart
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", fanart)
	ok = xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=liz, isFolder=True)
	return ok

params = parameters_string_to_dict(sys.argv[2])
name = urllib.unquote_plus(params.get('name', ''))
url = urllib.unquote_plus(params.get('url', ''))
mode = urllib.unquote_plus(params.get('mode', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))

if mode == 'listVideosNachTag':
	listVideosNachTag(url)
elif mode == 'listVideosGenre':
	listVideosGenre(url)
elif mode == 'playVideo':
	playVideo(url)
elif mode == "queueVideo":
	queueVideo(url, name)
else:
	index()