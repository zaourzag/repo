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
elif PY3:
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse  # Python 3+
	from urllib.request import build_opener, HTTPCookieProcessor, Request, urlopen  # Python 3+
	from http.cookiejar import LWPCookieJar  # Python 3+
import json
import xbmcvfs
import shutil
import socket
import time
import datetime
from bs4 import BeautifulSoup


global debuging
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath    = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
temp           = xbmc.translatePath(os.path.join(dataPath, 'temp', '')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg')
icon = os.path.join(addonPath, 'icon.png')
COUNTRY = addon.getSetting('sprache')
prefQUALITY = {'1280x720':720, '720x406':406, '640x360':360, '384x216':216}[addon.getSetting('prefVideoQuality')]
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

def failing(content):
	log(content, xbmc.LOGERROR)

def debug(content):
	log(content, xbmc.LOGDEBUG)

def log(msg, level=xbmc.LOGNOTICE):
	msg = py2_enc(msg)
	xbmc.log("["+addon.getAddonInfo('id')+"-"+addon.getAddonInfo('version')+"]"+msg, level)

def getUrl(url, header=None, referer=None):
	global cj
	for cook in cj:
		debug("(getUrl) Cookie : "+str(cook))
	opener = build_opener(HTTPCookieProcessor(cj))
	try:
		if header:
			opener.addheaders = header
		else:
			opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36')]
		if referer:
			opener.addheaders = [('Referer', referer)]
		response = opener.open(url, timeout=30)
		content = py3_dec(response.read())
	except Exception as e:
		failure = str(e)
		if hasattr(e, 'code'):
			failing("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
		elif hasattr(e, 'reason'):
			failing("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
		content = ""
		return sys.exit(0)
	opener.close()
	try: cj.save(cookie, ignore_discard=True, ignore_expires=True)
	except: pass
	return content

def index():
	debug("(index) -------------------------------------------------------- START = index -------------------------------------------------------")
	if COUNTRY=="de":
		addDir("Themen", "", "listThemes", icon)
		addDir("Programm sortiert nach Datum", "", "listDatum", icon)
		addDir("Videos sortiert nach Laufzeit", "", "listRunTime", icon)
		addDir("Sendungen A-Z", baseURL+COUNTRY+"/videos/sendungen/", "videos_AbisZ", icon)
		addDir("Meistgesehen", baseURL+COUNTRY+"/videos/meistgesehen/", "videos_AbisZ", icon)
		addDir("Neueste Videos", baseURL+COUNTRY+"/videos/neueste-videos/", "videos_AbisZ", icon)
		addDir("Letzte Chance", baseURL+COUNTRY+"/videos/letzte-chance/", "videos_AbisZ", icon)
		addDir("Suche ...", "", "SearchArte", icon)
		addDir("Live TV", "", "liveTV", icon)
		addDir("ARTE Einstellungen", "", "Settings", icon)
	elif COUNTRY=="fr":
		addDir("Sujets", "", "listThemes", icon)
		addDir("Programme trié par date", "", "listDatum", icon)
		addDir("Vidéos triées par durée", "", "listRunTime", icon)
		addDir("Émissions A-Z", baseURL+COUNTRY+"/videos/emissions/", "videos_AbisZ", icon)
		addDir("Les plus vues", baseURL+COUNTRY+"/videos/plus-vues/", "videos_AbisZ", icon)
		addDir("Les plus récentes", baseURL+COUNTRY+"/videos/plus-recentes/", "videos_AbisZ", icon)
		addDir("Dernière chance", baseURL+COUNTRY+"/videos/derniere-chance/", "videos_AbisZ", icon)
		addDir("Recherche ...", "", "SearchArte", icon)
		addDir("ARTE Paramètres", "", "Settings", icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def listThemes():
	debug("(listThemes) ------------------------------------------------ START = listThemes -----------------------------------------------")
	UN_Supported = ['360', 'Accue', 'Direct', 'Digitale', 'Edition', 'Guide', 'Home', 'Live', 'Magazin', 'productions', 'Programm', 'VOD/DVD']
	content = getUrl(baseURL+COUNTRY+"/")
	htmlPage = BeautifulSoup(content, 'html.parser')
	elemente = htmlPage.find_all("div",attrs={"list":"left"})
	for element in elemente:
		link = element.find("a")
		url = link["href"]
		name = link.text.strip()
		debug("(listThemes) ### Name = {0} || Url = {1} ###".format(name, url))
		if not any(x in name for x in UN_Supported):
			debug("(listThemes) filtered ### Name = {0} || Url = {1} ###".format(name, url))
			debug("++++++++++++++++++++++++")
			addDir(name, url, "listSubThemes", icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def listSubThemes(surl):
	debug("(listSubThemes) ------------------------------------------------ START = listSubThemes -----------------------------------------------")
	content = getUrl(surl)
	htmlPage = BeautifulSoup(content, 'html.parser')
	elemente = htmlPage.find_all("div",attrs={"list":"submenu"})
	anz=0
	for element in elemente:
		try:
			debug("Try to get listSubThemes: "+str(element))
			link = element.find("a")
			url = link["href"]
			name = link.text.strip()
			if not "arte info" in name.lower() and surl in url:
				debug("(listSubThemes) ready ### Name = {0} || Url = {1} ###".format(name, url))
				debug("++++++++++++++++++++++++")
				addDir(name, url, "videos_Themes", icon)
				anz=1
		except: 
			debug("----------")
			debug("ERROR - listSubThemes: "+str(element))
			debug("----------")
	if anz == 0:
		videos_Themes(surl)
		debug("(listSubThemes) ----- Nothing FOUND - goto = videos_Themes -----")
	xbmcplugin.endOfDirectory(pluginhandle) 

def videos_Themes(url, page="1"):
	debug("(videos_Themes) ------------------------------------------------ START = videos_Themes -----------------------------------------------")
	debug("(videos_Themes) URL : "+url)
	SUPPORTED = ['Ausschnitt', 'Bonus', 'Live', 'Programm', 'Programme']
	# https://www.arte.tv/sites/de/webproductions/api/?lang=de&paged=3  
	if int(page) == 1:
		content = getUrl(url)
		content = re.compile(' window.__INITIAL_STATE__ = (.+?)window.__CLASS_IDS__ =', re.DOTALL).findall(content)[0]
		content = content.strip()[:-1]
		debug("++++++++++++++++++++++++")
		debug("(videos_Themes) CONTENT : "+str(content))
		debug("++++++++++++++++++++++++")
		struktur1 = json.loads(content)
		sub1 = struktur1["pages"]["list"]
		key = list(sub1)[0]
		sub2 = sub1[key]["zones"]
		for zone in sub2:
			try:
				debug("(videos_Themes) <ZONE-Supported> : "+zone["data"][0]["kind"]["label"])
				if any(x in zone["data"][0]["kind"]["label"] for x in SUPPORTED):
					debug("(videos_Themes) <ZONE-Category> : "+zone["code"]["name"])
					category = zone["code"]["name"].replace('highlights_subcategory', 'videos_subcategory').replace('collection_sublights', 'collection_videos')
					debug("(videos_Themes) <ZONE-ID> : "+zone["code"]["id"])
					idd = zone["code"]["id"]
					break
			except: pass
		# URL = https://www.arte.tv/guide/api/api/zones/de/videos_subcategory/?id=AJO&page=2&limit=10
		url = ARTE_apiURL+"/zones/"+COUNTRY+"/"+category+"/?id="+str(idd)
	jsonurl = url+"&page="+page+"&limit=50"
	debug("(videos_Themes) complete JSON-URL : "+jsonurl)
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
					if int(quality["w"]) == found:
						DATA['media'].append({'imageURL': quality["url"]})
			photo = DATA['media'][0]['imageURL']
		except: photo = element["images"]["landscape"]["resolutions"][-1]["url"]
		duration = element["duration"]
		debug("(videos_Themes) ### Title = {0} ###".format(title))
		debug("(videos_Themes) ### vidURL = {0} ###".format(videoURL))
		debug("(videos_Themes) ### Duration = {0} ###".format(duration))
		debug("(videos_Themes) ### Thumb = {0} ###".format(photo))
		if duration and duration != "" and duration != "0":
			addLink(title, videoURL, "playvideo", photo, desc, duration)
	try:
		debug("(videos_Themes) Search for NextPage ...")
		nextpage = struktur2["nextPage"]
		# NEXTPAGE = https://api-cdn.arte.tv/api/emac/v3/de/web/zones/videos_subcategory/?id=AJO&page=2&limit=10
		debug("(videos_Themes) This is NextPage : "+nextpage)
		if nextpage.startswith("http"):
			addDir("[COLOR lime]Nächste Seite  >>>[/COLOR]", url, "videos_Themes", icon, page=int(page)+1)
	except: pass
	xbmcplugin.endOfDirectory(pluginhandle)

def listDatum():
	debug("(listDatum) ------------------------------------------------ START = listDatum -----------------------------------------------")
	if COUNTRY=="de":
		addDir("Zukunft","-22", "datumSelect", icon)
		addDir("Vergangenheit", "22", "datumSelect", icon)
	elif COUNTRY=="fr":
		addDir("Avenir", "-21", "datumSelect", icon)
		addDir("Passé", "21", "datumSelect", icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def datumSelect(wert):
	debug("(datumSelect) ------------------------------------------------ START = datumSelect -----------------------------------------------")
	if int(wert) < 0:
		start = 0
		end = int(wert)
		sprung = -1
	elif int(wert) > 0:
		start = 0
		end = int(wert)
		sprung = 1
	for i in range(start, end, sprung):
		title = (datetime.date.today()-datetime.timedelta(days=i)).strftime("%d-%m-%Y")
		suche = (datetime.date.today()-datetime.timedelta(days=i)).strftime("%Y-%m-%d")
		addDir(title, suche, "videos_Datum", icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def videos_Datum(tag):
	debug("(videos_Datum) ------------------------------------------------ START = videos_Datum -----------------------------------------------")
	# URL-Tag = https://www.arte.tv/guide/api/api/pages/de/TV_GUIDE/?day=2018-08-14
	url = ARTE_apiURL+"/pages/"+COUNTRY+"/TV_GUIDE/?day="+tag
	debug("(videos_Datum) URL : "+url)
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
					if int(quality["w"]) == found:
						DATA['media'].append({'imageURL': quality["url"]})
			photo = DATA['media'][0]['imageURL']
		except: photo = element["images"]["landscape"]["resolutions"][-1]["url"]
		duration = element["duration"]
		broadcastDates = element["broadcastDates"][0]
		#"2018-02-28T04:00:00Z"
		debug("(videos_Datum) ### Title = {0} ### Duration = {1} ###".format(title, duration))
		debug("(videos_Datum) ### Date = {0} ### Thumb = {1} ###".format(broadcastDates, photo))
		try:
			datetime_object = datetime.datetime.strptime(broadcastDates, '%Y-%m-%dT%H:%M:%SZ')
		except TypeError:
			datetime_object = datetime.datetime(*(time.strptime(broadcastDates, '%Y-%m-%dT%H:%M:%SZ')[0:6]))
		#LOCALTIME = datetime_object.replace(tzinfo=pytz.utc).astimezone(tz.tzlocal())
		LOCALTIME = utc_to_local(datetime_object)
		wann = "[COLOR orangered]"+LOCALTIME.strftime("%H:%M")+"[/COLOR]"
		debug("(videos_Datum) ### New-Title = {0}  {1} ###".format(LOCALTIME.strftime("%H:%M"), title))
		stickers = str(element["stickers"])
		if "FULL_VIDEO" in stickers:
			addLink(wann+"  "+title, videoURL, "playvideo", photo, desc, duration)
	xbmcplugin.endOfDirectory(pluginhandle)

def listRunTime():
	debug("(listRunTime) ------------------------------------------------ START = listRunTime -----------------------------------------------")
	if COUNTRY=="de":
		addDir("Videos 0 bis 5 Min.", baseURL+COUNTRY+"/videos/5-min/", "videos_AbisZ", icon, query="@maxDuration=5@minDuration=0")
		addDir("Videos 5 bis 15 Min.", baseURL+COUNTRY+"/videos/15-min/", "videos_AbisZ", icon, query="@maxDuration=15@minDuration=5")
		addDir("Videos 15 bis 60 Min.", baseURL+COUNTRY+"/videos/1-stunde/", "videos_AbisZ", icon, query="@maxDuration=60@minDuration=15")
		addDir("Videos > 60 Min.", baseURL+COUNTRY+"/videos/viel-zeit/", "videos_AbisZ", icon, query="@minDuration=60")
	elif COUNTRY=="fr":
		addDir("Vidéos 0 à 5 min.", baseURL+COUNTRY+"/videos/5-min/", "videos_AbisZ", icon, query="@maxDuration=5@minDuration=0")
		addDir("Vidéos 5 à 15 min.", baseURL+COUNTRY+"/videos/15-min/", "videos_AbisZ", icon, query="@maxDuration=15@minDuration=5")
		addDir("Vidéos 15 à 60 min.", baseURL+COUNTRY+"/videos/1-heure/", "videos_AbisZ", icon, query="@maxDuration=60@minDuration=15")
		addDir("Vidéos > 60 min.", baseURL+COUNTRY+"/videos/beaucoup/", "videos_AbisZ", icon, query="@minDuration=60")
	xbmcplugin.endOfDirectory(pluginhandle)

def SearchArte():
	debug("(SearchArte) ------------------------------------------------ START = SearchArte -----------------------------------------------")
	#SEARCH = https://www.arte.tv/guide/api/api/zones/de/listing_SEARCH?page=1&limit=20&query=filme
	someReceived = False
	word = xbmcgui.Dialog().input("Search ARTE ...", type=xbmcgui.INPUT_ALPHANUM)
	word = quote_plus(word, safe='')
	if word == "": return
	title_SEARCH = baseURL+COUNTRY+"/search/?q="+word
	debug("(SearchArte) Search-Url : "+title_SEARCH)
	try:
		result = getUrl(title_SEARCH)
		content = re.findall('<span class="font-size-l">(.*?)</span>', result, re.S)[0]
	except: content = "OKAY"
	debug("(SearchArte) Search-Result : "+str(content))
	if content == "OKAY":
		videos_AbisZ(title_SEARCH, query=word)
		someReceived = True
	elif ("keine daten verfügbar" in content.lower() or "aucun résultat" in content.lower() or not someReceived):
		if COUNTRY=="de":
			addDir("[B][COLOR FFFF456E]!!! Zu dem gesuchten Begriff wurden KEINE Ergebnisse gefunden !!![/COLOR][/B]", word, "", icon)
		elif COUNTRY=="fr":
			addDir("[B][COLOR FFFF456E]!!! Aucun résultat n'a été trouvé pour le terme recherché !!![/COLOR][/B]", word, "", icon)
	else: pass
	xbmcplugin.endOfDirectory(pluginhandle)

def videos_AbisZ(url, page="1", query=""):
	debug("(videos_AbisZ) ------------------------------------------------ START = videos_AbisZ -----------------------------------------------")
	debug("(videos_AbisZ) URL : "+url+" || QUERY : "+query)
	newUrl = url
	if int(page) == 1:
		content = getUrl(url)
		content = re.compile(' window.__INITIAL_STATE__ = (.+?)window.__CLASS_IDS__ =', re.DOTALL).findall(content)[0]
		content = content.strip()[:-1]
		debug("++++++++++++++++++++++++")
		debug("(videos_AbisZ) CONTENT : "+str(content))
		debug("++++++++++++++++++++++++")
		struktur1 = json.loads(content)
		sub1 = struktur1["pages"]["list"]
		key = list(sub1)[0]
		sub2 = sub1[key]["zones"]
		category = sub2[0]["code"]["name"]
		debug("(videos_AbisZ) found CATEGORY : "+str(category))
		url = ARTE_apiURL+"/zones/"+COUNTRY+"/"+category+"/"
	if query != "":
		if "minDuration" in query:
			# DURATION = https://www.arte.tv/guide/api/api/zones/de/listing_DURATION/?page=2&limit=20&maxDuration=5&minDuration=0
			jsonurl = url+"?page="+page+"&limit=50"+query.replace("@", "&")
		else:
			# SEARCH = https://www.arte.tv/guide/api/api/zones/de/listing_SEARCH/?page=2&limit=20&query=concert
			jsonurl = url+"?page="+page+"&limit=50&query="+query.replace(" ", "+")
	else:
		# STANDARD =  https://www.arte.tv/guide/api/api/zones/de/listing_MOST_VIEWED/?page=2&limit=20
		jsonurl = url+"?page="+page+"&limit=50"
	debug("(videos_AbisZ) complete JSON-URL : "+jsonurl)
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
					if int(quality["w"]) == found:
						DATA['media'].append({'imageURL': quality["url"]})
			photo = DATA['media'][0]['imageURL']
		except: photo = element["images"]["landscape"]["resolutions"][-1]["url"]
		duration = element["duration"]
		debug("(videos_AbisZ) ### Title = {0} ###".format(title))
		debug("(videos_AbisZ) ### vidURL = {0} ###".format(videoURL))
		debug("(videos_AbisZ) ### Duration = {0} ###".format(duration))
		debug("(videos_AbisZ) ### Thumb = {0} ###".format(photo))
		if "/sendungen/" in newUrl.lower() or "/emissions/" in newUrl.lower():
			addDir(title, videoURL, "videos_Themes", photo, desc)
		else:
			if duration and duration != "" and duration != "0":
				addLink(title, videoURL, "playvideo", photo, desc, duration)
	try:
		debug("(videos_AbisZ) Search for NextPage ...")
		nextpage = struktur2["nextPage"]
		# NEXTPAGE = https://api-cdn.arte.tv/api/emac/v3/de/web/zones/listing_MAGAZINES?page=2&limit=20
		debug("(videos_AbisZ) This is NextPage : "+nextpage)
		if nextpage.startswith("http"):
			if ("search" in nextpage.lower() or "minduration" in nextpage.lower()):
				addDir("[COLOR lime]Nächste Seite  >>>[/COLOR]", url, "videos_AbisZ", icon, page=int(page)+1, query=query)
			else:
				addDir("[COLOR lime]Nächste Seite  >>>[/COLOR]", url, "videos_AbisZ", icon, page=int(page)+1)
	except: pass
	xbmcplugin.endOfDirectory(pluginhandle)

def playvideo(url):
	debug("(playvideo) ------------------------------------------------ START = playvideo -----------------------------------------------")
	# Übergabe des Abspiellinks von anderem Video-ADDON: plugin://plugin.video.L0RE.arte/?mode=playvideo&url=048256-000-A oder: plugin://plugin.video.L0RE.arte/?mode=playvideo&url=https://www.arte.tv/de/videos/048256-000-A/wir-waren-koenige/
	DATA = {}
	DATA['media'] = []
	finalURL = False
	try:
		if url[:4] == "http":
			idd = re.compile('/videos/(.+?)/', re.DOTALL).findall(url)[0]
		else:
			idd = url
		debug("----->")
		debug("(playvideo) IDD : "+idd)
		if COUNTRY=="de":
			SHORTCUTS = ['DE', 'OmU', 'OV', 'VO'] # "DE" = Original deutsch | "OmU" = Original mit deutschen Untertiteln | "OV" = Stumm oder Originalversion
		elif COUNTRY=="fr":
			SHORTCUTS = ['VOF', 'VF', 'VOSTF', 'VO'] # "VOF" = Original französisch | "VF" = französisch vertont | "VOSTF" = Stumm oder Original mit französischen Untertiteln
		content = getUrl("https://api.arte.tv/api/player/v1/config/"+COUNTRY+"/"+idd+"?autostart=0&lifeCycle=1")
		stream = json.loads(content)['videoJsonPlayer']
		stream_offer = stream['VSR']
		for element in stream_offer:
			if int(stream['VSR'][element]['versionProg']) == 1 and stream['VSR'][element]['mediaType'].lower() == "mp4":
				debug("(playvideo) Stream-Element : "+str(stream['VSR'][element]))
				for found in SHORTCUTS:
					if stream['VSR'][element]['versionShortLibelle'] == found and stream['VSR'][element]['height'] == prefQUALITY:
						DATA['media'].append({'streamURL': stream['VSR'][element]['url']})
						finalURL = DATA['media'][0]['streamURL']
				if not finalURL and COUNTRY == "de":  # VA=Voice Allemande
					if "VA" in stream['VSR'][element]['versionCode'] and stream['VSR'][element]['height'] == prefQUALITY:
						finalURL = stream['VSR'][element]['url']
				elif not finalURL and COUNTRY == "fr":  # VF=Voice Francaise
					if "VF" in stream['VSR'][element]['versionCode'] and stream['VSR'][element]['height'] == prefQUALITY:
						finalURL = stream['VSR'][element]['url']
		debug("(playvideo) Quality-Setting : "+str(prefQUALITY))
		log("(playvideo) StreamURL : "+str(finalURL))
		debug("<-----")
		if finalURL:
			listitem = xbmcgui.ListItem(path=finalURL)
			xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
		else: xbmcgui.Dialog().notification(addon.getAddonInfo('id')+" : [COLOR red]!!! STREAM - URL - ERROR !!![/COLOR]", "ERROR = [COLOR red]KEINE passende *Stream-Url* auf ARTE gefunden ![/COLOR]", xbmcgui.NOTIFICATION_ERROR, 6000)
	except: xbmcgui.Dialog().notification(addon.getAddonInfo('id')+" : [COLOR red]!!! VIDEO - URL - ERROR !!![/COLOR]", "ERROR = [COLOR red]Der übertragene *Video-Abspiel-Link* ist FEHLERHAFT ![/COLOR]", xbmcgui.NOTIFICATION_ERROR, 6000)

def liveTV():
	debug("(liveTV) ------------------------------------------------ START = liveTV -----------------------------------------------")
	addLink("Arte HD", "https://artelive-lh.akamaihd.net/i/artelive_de@393591/index_1_av-b.m3u8", "playlive", icon)
	addLink("ARTE Event 1", "https://arteevent01-lh.akamaihd.net/i/arte_event01@395110/index_1_av-b.m3u8", "playlive", icon)
	addLink("ARTE Event 2", "https://arteevent02-lh.akamaihd.net/i/arte_event02@308866/index_1_av-b.m3u8", "playlive", icon)
	addLink("ARTE Event 3", "https://arteevent03-lh.akamaihd.net/i/arte_event03@305298/index_1_av-b.m3u8", "playlive", icon)
	addLink("ARTE Event 4", "https://arteevent04-lh.akamaihd.net/i/arte_event04@308879/index_1_av-b.m3u8", "playlive", icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def playlive(url):
	listitem = xbmcgui.ListItem(path=url)  
	xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def utc_to_local(dt):
	if time.localtime().tm_isdst:
		return dt - datetime.timedelta(seconds=time.altzone)
	else:
		return dt - datetime.timedelta(seconds=time.timezone)

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

if mode == 'listThemes':
	listThemes()
elif mode == 'listSubThemes':
	listSubThemes(url)
elif mode == 'videos_Themes':
	videos_Themes(url, page)
elif mode == 'listDatum':
	listDatum()
elif mode == 'datumSelect':
	datumSelect(url)
elif mode == 'videos_Datum':
	videos_Datum(url)
elif mode == 'listRunTime':
	listRunTime()
elif mode == 'SearchArte':
	SearchArte()
elif mode == 'videos_AbisZ':
	videos_AbisZ(url, page, query)
elif mode == 'playvideo':
	playvideo(url)
elif mode == 'liveTV':
	liveTV()
elif mode == 'playlive':
	playlive(url)
elif mode == 'Settings':
	addon.openSettings()
else:
	index()