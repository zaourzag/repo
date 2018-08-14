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
import datetime
from bs4 import BeautifulSoup


global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
#args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
temp        = xbmc.translatePath(os.path.join(dataPath, 'temp', '')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg').encode('utf-8').decode('utf-8')
icon = os.path.join(addonPath, 'icon.png').encode('utf-8').decode('utf-8')
country = addon.getSetting("sprache")
prefQuality = int(addon.getSetting("quality"))
baseURL = "https://www.arte.tv/"
ARTE_apiURL = "https://www.arte.tv/guide/api/api"

xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

if xbmcvfs.exists(temp) and os.path.isdir(temp):
	shutil.rmtree(temp, ignore_errors=True)
	xbmc.sleep(500)
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

def log_Special(msg, level=xbmc.LOGNOTICE):
	msg = py2_enc(msg)
	xbmc.log('[ARTE]'+msg, level)

def debug(content):
	log(content, xbmc.LOGDEBUG)

def notice(content):
	log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
	msg = py2_enc(msg)
	xbmc.log('[%s] %s' %(addon.getAddonInfo('id'), msg), level) 

def getUrl(url, header=None, referer=None):
	global cj
	debug("Get Url : "+url)
	for cook in cj:
		debug("Cookie : "+str(cook))
	opener = build_opener(HTTPCookieProcessor(cj))
	try:
		if header:
			opener.addheaders = header
		else:
			opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')]
		if referer:
			opener.addheaders = [('Referer', referer)]
		response = opener.open(url, timeout=30)
		content = py3_dec(response.read())
	except Exception as e:
		failure = str(e)
		if hasattr(e, 'code'):
			log_Special("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
		elif hasattr(e, 'reason'):
			log_Special("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
		content = ""
		return sys.exit(0)
	opener.close()
	cj.save(cookie, ignore_discard=True, ignore_expires=True)
	return content

# Haupt Menu Anzeigen     
def menu():
	if country=="de":
		addDir("Themen", "", "liste", icon)
		addDir("Programm", "", "datummenu", icon)
		addDir("Sendungen A-Z", baseURL+country+"/videos/sendungen/", "abiszetc", icon)
		addDir("Meistgesehen", baseURL+country+"/videos/meistgesehen/", "abiszetc", icon)
		addDir("Neueste Videos", baseURL+country+"/videos/neueste-videos/", "abiszetc", icon)
		addDir("Letzte Chance", baseURL+country+"/videos/letzte-chance/", "abiszetc", icon)
		addDir("Videos sortiert nach Laufzeit", "", "listVideos_Time", icon)
		addDir("Live TV", "", "live", icon)
		addDir("Suche ...", "", "SearchArte", icon)
		addDir("Einstellungen", "", "Settings", icon)
	elif country=="fr":
		addDir("Sujets", "", "liste", icon)
		addDir("Guide +7", "", "datummenu", icon)
		addDir("Émissions A-Z", baseURL+country+"/videos/emissions/", "abiszetc", icon)
		addDir("Les plus vues", baseURL+country+"/videos/plus-vues/", "abiszetc", icon)
		addDir("Les plus récentes", baseURL+country+"/videos/plus-recentes/", "abiszetc", icon)
		addDir("Dernière chance", baseURL+country+"/videos/derniere-chance/", "abiszetc", icon)
		addDir("Vidéos triées par durée", "", "listVideos_Time", icon)
		addDir("Recherche ...", "", "SearchArte", icon)
		addDir("Paramètres", "", "Settings", icon)
	xbmcplugin.endOfDirectory(addon_handle)

def liste():
	UN_Supported = ['360', 'Accue', 'Direct', 'Digitale', 'Edition', 'Guide', 'Home', 'Live', 'Magazin', 'productions', 'Programm', 'VOD/DVD']
	content = getUrl(baseURL+country+"/")
	htmlPage = BeautifulSoup(content, 'html.parser')
	elemente = htmlPage.find_all("div",attrs={"list":"left"})
	for element in elemente:
		link = element.find("a")
		url = link["href"]
		name = link.text.strip()
		if not any(x in name for x in UN_Supported):
			addDir(name, url, "subrubrik", icon)
	xbmcplugin.endOfDirectory(addon_handle)

def subrubrik(surl):
	content=getUrl(surl)
	htmlPage = BeautifulSoup(content, 'html.parser')
	elemente = htmlPage.find_all("div",attrs={"list":"submenu"})
	anz=0
	for element in elemente:
		try:
			debug("++++++++++")
			debug("Try to get subrubrik: "+str(element))
			debug("++++++++++")
			link = element.find("a")
			url = link["href"]
			name = link.text.strip()
			if not "arte info" in name.lower() and surl in url:
				addDir(name, url, "videoliste", icon)
				anz=1
		except: 
			debug("----------")
			debug("Exception subrubrik: "+str(element))
			debug("----------")
	if anz == 0:
		videoliste(surl)
	xbmcplugin.endOfDirectory(addon_handle) 

def videoliste(url, page="1"):  
	debug("Start Videoliste")
	debug(url)
	SUPPORTED = ['Ausschnitt', 'Bonus', 'Live', 'Programm', 'Programme']
	# https://www.arte.tv/sites/de/webproductions/api/?lang=de&paged=3  
	if int(page) == 1:
		content = getUrl(url)
		content = re.compile(' window.__INITIAL_STATE__ = (.+?)window.__CLASS_IDS__ =', re.DOTALL).findall(content)[0]
		content = content.strip()[:-1]
		debug("+++++++++++++++")
		debug(content)
		debug("+++++++++++++++")
		struktur1 = json.loads(content)
		sub1 = struktur1["pages"]["list"]
		key = list(sub1)[0]
		sub2 = sub1[key]["zones"]
		for zone in sub2:
			debug(str(zone))
			try:
				debug(zone["data"][0]["kind"]["label"])
				if any(x in zone["data"][0]["kind"]["label"] for x in SUPPORTED):
					category = zone["code"]["name"]
					idd = zone["code"]["id"]
					break
			except: pass
		# URL = https://www.arte.tv/guide/api/api/zones/de/videos_subcategory?id=AJO&page=2&limit=10
		url = ARTE_apiURL+"/zones/"+country+"/"+category+"?id="+str(idd)
	jsonurl = url+"&page="+page+"&limit=50"
	debug(jsonurl)
	content = getUrl(jsonurl)
	struktur2 = json.loads(content)
	for element in struktur2["data"]:
		DATA = {}
		DATA['media'] = []
		RESOLUTIONS = [1920, 1280, 940, 720, 620]
		videoURL = element["url"]
		title = py2_enc(element["title"])
		try:
			subtitle = py2_enc(element["subtitle"])
			title += " - "+subtitle
		except: pass
		try: desc = py2_enc(element["description"])
		except: desc=""
		try:
			for found in RESOLUTIONS:
				for quality in element["images"]["landscape"]["resolutions"]:
					if int(quality["width"]) == found:
						DATA['media'].append({'imageURL': quality["url"]})
			photo = DATA['media'][0]['imageURL']
		except: photo = element["images"]["landscape"]["resolutions"][-1]["url"]
		duration = element["duration"]
		if duration and duration != "" and duration != "0":
			addLink(title, videoURL, "playvideo", photo, desc=desc, duration=duration)
	try:
		debug("NextPage try:")
		nextpage = struktur2["nextPage"]
		# NEXTPAGE = https://api-cdn.arte.tv/api/emac/v3/de/web/zones/videos_subcategory?id=AJO&page=2&limit=10
		debug("search for nextPage: "+nextpage)
		if nextpage.startswith("http"):
			addDir("[COLOR chartreuse]Nächste Seite  >>>[/COLOR]", url, "videoliste", icon, page=int(page)+1)
	except: pass
	xbmcplugin.endOfDirectory(addon_handle)

def abiszetc(url, page="1", query=""):
	newUrl = url
	if int(page) == 1:
		content = getUrl(url)
		content = re.compile(' window.__INITIAL_STATE__ = (.+?)window.__CLASS_IDS__ =', re.DOTALL).findall(content)[0]
		content = content.strip()[:-1]
		debug("##########")
		debug(content)
		debug("##########")
		struktur1 = json.loads(content)
		sub1 = struktur1["pages"]["list"]
		key = list(sub1)[0]
		sub2 = sub1[key]["zones"]
		category = sub2[0]["code"]["name"]
		debug("CATEGORY: "+str(category))
		url = ARTE_apiURL+"/zones/"+country+"/"+category
	if query != "":
		# SEARCH = https://www.arte.tv/guide/api/api/zones/de/listing_SEARCH?page=2&limit=20&query=concert
		jsonurl = url+"?page="+page+"&limit=50&query="+query
	else:
		# STANDARD =  https://www.arte.tv/guide/api/api/zones/de/listing_MOST_VIEWED?page=2&limit=20
		jsonurl = url+"?page="+page+"&limit=50"
	content = getUrl(jsonurl)
	struktur2 = json.loads(content)
	for element in struktur2["data"]:
		DATA = {}
		DATA['media'] = []
		RESOLUTIONS = [1920, 1280, 940, 720, 620]
		videoURL = element["url"]
		title = py2_enc(element["title"])
		try:
			subtitle = py2_enc(element["subtitle"])
			title += " - "+subtitle
		except: pass
		try: desc = py2_enc(element["description"])
		except: desc=""
		try:
			for found in RESOLUTIONS:
				for quality in element["images"]["landscape"]["resolutions"]:
					if int(quality["width"]) == found:
						DATA['media'].append({'imageURL': quality["url"]})
			photo = DATA['media'][0]['imageURL']
		except: photo = element["images"]["landscape"]["resolutions"][-1]["url"]
		duration = element["duration"]
		if "/sendungen/" in newUrl.lower() or "/emissions/" in newUrl.lower():
			addDir(title, videoURL, "videoliste", photo, desc=desc)
		else:
			if duration and duration != "" and duration != "0":
				addLink(title, videoURL, "playvideo", photo, desc=desc, duration=duration)
	try:
		debug("NextPage try:")
		nextpage = struktur2["nextPage"]
		# NEXTPAGE = https://api-cdn.arte.tv/api/emac/v3/de/web/zones/listing_MAGAZINES?page=2&limit=20
		debug("search for nextPage: "+nextpage)
		if nextpage.startswith("http"):
			if "search" in nextpage.lower():
				addDir("[COLOR chartreuse]Nächste Seite  >>>[/COLOR]", url, "abiszetc", icon, page=int(page)+1, query=query)
			else:
				addDir("[COLOR chartreuse]Nächste Seite  >>>[/COLOR]", url, "abiszetc", icon, page=int(page)+1)
	except: pass
	xbmcplugin.endOfDirectory(addon_handle)

def datummenu():
	if country=="de":
		addDir("Zukunft","-30", "datumselect", icon)
		addDir("Vergangenheit", "30", "datumselect", icon)
	elif country=="fr":
		addDir("Avenir", "-30", "datumselect", icon)
		addDir("Passé", "30", "datumselect", icon)
	xbmcplugin.endOfDirectory(addon_handle)
	
def datumselect(wert):
	if int(wert) < 0:
		start = 0
		end = int(wert)
		sprung = -1
	elif int(wert) > 0:
		start = 0
		end = int(wert)
		sprung = 1
	for i in range(start, end, sprung):
		title = (datetime.date.today()-datetime.timedelta(days=i)).strftime("%d/%m/%Y")
		suche = (datetime.date.today()-datetime.timedelta(days=i)).strftime("%y-%m-%d")
		addDir(title, suche, "showday", icon)
	xbmcplugin.endOfDirectory(addon_handle)

def showday(tag):
	# URL-Tag = https://www.arte.tv/guide/api/api/pages/de/TV_GUIDE/?day=18-08-14
	url = ARTE_apiURL+"/pages/"+country+"/TV_GUIDE/?day="+tag
	content = getUrl(url)
	struktur = json.loads(content)
	for element in struktur["zones"][-1]["data"]:
		DATA = {}
		DATA['media'] = []
		RESOLUTIONS = [1920, 1280, 940, 720, 620]
		videoURL = element["url"]
		title = py2_enc(element["title"])
		try:
			subtitle = py2_enc(element["subtitle"])
			title += " - "+subtitle
		except: pass
		try: desc = py2_enc(element["fullDescription"])
		except: desc=""
		try:
			for found in RESOLUTIONS:
				for quality in element["images"]["landscape"]["resolutions"]:
					if int(quality["width"]) == found:
						DATA['media'].append({'imageURL': quality["url"]})
			photo = DATA['media'][0]['imageURL']
		except: photo = element["images"]["landscape"]["resolutions"][-1]["url"]
		duration = element["duration"]
		broadcastDates = element["broadcastDates"][0]
		#"2018-02-28T04:00:00Z"
		try:
			datetime_object = datetime.datetime.strptime(broadcastDates, '%Y-%m-%dT%H:%M:%SZ')
		except TypeError:
			datetime_object = datetime.datetime(*(time.strptime(broadcastDates, '%Y-%m-%dT%H:%M:%SZ')[0:6]))
		wann = "[COLOR orangered]"+datetime_object.strftime("%H:%M")+"[/COLOR]"
		debug("-----------------------")
		debug(wann)
		stickers = str(element["stickers"])
		if "PLAYABLE" in stickers:
			addLink(wann+"  "+title, videoURL, "playvideo", photo, desc=desc, duration=duration)
	xbmcplugin.endOfDirectory(addon_handle)

def listVideos_Time():
	if country=="de":
		addDir("Videos 0 bis 5 Min.", baseURL+country+"/videos/5-min/", "abiszetc", icon)
		addDir("Videos 5 bis 15 Min.", baseURL+country+"/videos/15-min/", "abiszetc", icon)
		addDir("Videos 15 bis 60 Min.", baseURL+country+"/videos/1-stunde/", "abiszetc", icon)
		addDir("Videos > 60 Min.", baseURL+country+"/videos/viel-zeit/", "abiszetc", icon)
	elif country=="fr":
		addDir("Vidéos 0 à 5 min.", baseURL+country+"/videos/5-min/", "abiszetc", icon)
		addDir("Vidéos 5 à 15 min.", baseURL+country+"/videos/15-min/", "abiszetc", icon)
		addDir("Vidéos 15 à 60 min.", baseURL+country+"/videos/1-heure/", "abiszetc", icon)
		addDir("Vidéos > 60 min.", baseURL+country+"/videos/beaucoup/", "abiszetc", icon)
	xbmcplugin.endOfDirectory(addon_handle)

def live():
	addLink("Arte HD", "https://artelive-lh.akamaihd.net/i/artelive_de@393591/index_1_av-p.m3u8", "playlive", icon)
	addLink("ARTE Event 1", "https://arteevent01-lh.akamaihd.net/i/arte_event01@395110/index_1_av-p.m3u8", "playlive", icon)
	addLink("ARTE Event 2", "https://arteevent02-lh.akamaihd.net/i/arte_event02@308866/index_1_av-p.m3u8", "playlive", icon)
	addLink("ARTE Event 3", "https://arteevent03-lh.akamaihd.net/i/arte_event03@305298/index_1_av-p.m3u8", "playlive", icon)
	addLink("ARTE Event 4", "https://arteevent04-lh.akamaihd.net/i/arte_event04@308879/index_1_av-p.m3u8", "playlive", icon)
	xbmcplugin.endOfDirectory(addon_handle)

def playlive(url):
	listitem = xbmcgui.ListItem(path=url)  
	xbmcplugin.setResolvedUrl(addon_handle, True, listitem)

def SearchArte():
	#SEARCH = https://www.arte.tv/guide/api/api/zones/de/listing_SEARCH?page=1&limit=20&query=filme
	someReceived = False
	word = xbmcgui.Dialog().input("Search ARTE ...", type=xbmcgui.INPUT_ALPHANUM)
	word = quote_plus(word, safe='')
	if word == "": return
	title_SEARCH = baseURL+country+"/search/?q="+word
	debug("SearchArte - Url: "+title_SEARCH)
	try:
		result = getUrl(title_SEARCH)
		content = re.findall('<span class="font-size-l">(.*?)</span>',result,re.S)[0]
	except: content = "OKAY"
	debug("SearchArte - Result: "+content)
	if content == "OKAY":
		abiszetc(title_SEARCH, query=word)
		someReceived = True
	elif ("keine daten verfügbar" in content.lower() or "aucun résultat" in content.lower() or not someReceived):
		if country=="de":
			addDir("[B][COLOR FFFF456E]!!! Zu dem gesuchten Begriff wurden KEINE Ergebnisse gefunden !!![/COLOR][/B]", word, "", icon)
		elif country=="fr":
			addDir("[B][COLOR FFFF456E]!!! Aucun résultat n'a été trouvé pour le terme recherché !!![/COLOR][/B]", word, "", icon)
	else: pass
	xbmcplugin.endOfDirectory(addon_handle)

def playvideo(url):
	# Übergabe des Abspiellinks von anderem Video-ADDON: plugin://plugin.video.L0RE.arte/?mode=playvideo&url=048256-000-A oder: plugin://plugin.video.L0RE.arte/?mode=playvideo&url=https://www.arte.tv/de/videos/048256-000-A/wir-waren-koenige/
	try:
		if url.startswith('http'):
			idd = re.compile('/videos/(.+?)/', re.DOTALL).findall(url)[0]
		else:
			idd = url
		if country=="de":
			standards1="OV" # Stumm oder Originalversion
			standards2="OmU" # Original mit deutschen Untertiteln
			standards3="DE" # Original deutsch
		elif country=="fr":
			standards1="VOSTF" # Stumm oder Original mit französischen Untertiteln
			standards2="VF" # französisch vertont
			standards3="VOF" # Original französisch
		#elif country=="pl":
			#sub="DE-POL"
		#elif country=="es":
			#sub="DE-ESP"
		try: 
			content = getUrl("https://api.arte.tv/api/player/v1/config/"+country+"/"+idd+"?autostart=0&lifeCycle=1")
		except: return -1 # no network
		finalURL = False
		stream = json.loads(content)['videoJsonPlayer']
		stream_offer = stream['VSR']
		debug("----->")
		for element in stream_offer:
			debug(stream['VSR'][element])
			if int(stream['VSR'][element]["versionProg"]) == 1 and stream['VSR'][element]["mediaType"].lower() == "mp4":
				if stream['VSR'][element]["versionShortLibelle"]==standards3 and stream['VSR'][element]["height"]==prefQuality:
					finalURL = stream['VSR'][element]["url"]
				if not finalURL and stream['VSR'][element]["versionShortLibelle"]==standards2 and stream['VSR'][element]["height"]==prefQuality:
					finalURL = stream['VSR'][element]["url"]
				if not finalURL and stream['VSR'][element]["versionShortLibelle"]==standards1 and stream['VSR'][element]["height"]==prefQuality:
					finalURL = stream['VSR'][element]["url"]
				if not finalURL and "VO" in stream['VSR'][element]["versionCode"] and stream['VSR'][element]["height"]==prefQuality:
					finalURL = stream['VSR'][element]["url"]
		debug(str(prefQuality))
		debug("playvideo - finalUrl: "+finalURL)
		debug("<-----")
		if finalURL:
			listitem = xbmcgui.ListItem(path=finalURL)
			listitem.setProperty('IsPlayable', 'true')
			xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
		else:
			xbmcgui.Dialog().notification(addon.getAddonInfo('id')+" : [COLOR red]!!! STREAM - URL - ERROR !!![/COLOR]", "ERROR = [COLOR red]KEINE passende *Stream-Url* auf ARTE gefunden ![/COLOR]", xbmcgui.NOTIFICATION_ERROR, 6000)
	except:
		xbmcgui.Dialog().notification(addon.getAddonInfo('id')+" : [COLOR red]!!! VIDEO - URL - ERROR !!![/COLOR]", "ERROR = [COLOR red]Der übertragene *Video-Abspiel-Link* ist FEHLERHAFT ![/COLOR]", xbmcgui.NOTIFICATION_ERROR, 6000)

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def addDir(name, url, mode, image, desc=None, page=1, query=""):   
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&query="+str(query)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	if image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

def addLink(name, url, mode, image, desc=None, duration=None, genre=None):
	if duration:
		xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DURATION)
	debug("URL ADDLINK :"+quote_plus(url))
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration, "Genre": genre, "Studio": "ARTE"})
	if image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

params = parameters_string_to_dict(sys.argv[2])
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
image = unquote_plus(params.get('image', ''))
page = unquote_plus(params.get('page', ''))
query = unquote_plus(params.get('query', ''))
referer = unquote_plus(params.get('referer', ''))

# Wenn Kategory ausgewählt wurde
if mode == 'liste':
	liste()
elif mode == 'subrubrik':
	subrubrik(url)
elif mode == 'videoliste':
	videoliste(url, page)
elif mode == 'abiszetc':
	abiszetc(url, page, query)
elif mode == 'datummenu':
	datummenu()
elif mode == 'datumselect':
	datumselect(url)
elif mode == 'showday':
	showday(url)
elif mode == 'listVideos_Time':
	listVideos_Time()
elif mode == 'live':
	live()
elif mode == 'playlive':
	playlive(url)
elif mode == 'SearchArte':
	SearchArte()
elif mode == 'playvideo':
	playvideo(url)
elif mode == 'Settings':
	addon.openSettings()
	# Haupt Menü Anzeigen 
else:
	menu()