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
from bs4 import BeautifulSoup
import io
import gzip


global debuging
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
temp        = xbmc.translatePath(os.path.join(dataPath, 'temp', '')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg')
icon = os.path.join(addonPath, 'icon.png')
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
enableDebug = addon.getSetting("enableDebug") == "true"
enableInputstream = addon.getSetting("inputstream") == "true"
blackLIST = addon.getSetting("blacklist").split(',')
enableAdjustment = addon.getSetting("show_settings") == "true"
baseURL = "https://www.tele5.de/"

xbmcplugin.setContent(pluginhandle, 'movies')

if addon.getSetting("enableTitleOrder") == "true":
	xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)

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

def debug_MS(content):
	if enableDebug:
		log(content, xbmc.LOGNOTICE)

def debug(content):
	log(content, xbmc.LOGDEBUG)

def log(msg, level=xbmc.LOGNOTICE):
	msg = py2_enc(msg)
	xbmc.log("["+addon.getAddonInfo('id')+"-"+addon.getAddonInfo('version')+"]"+msg, level)

def getUrl(url, header=None, referer=None):
	global cj
	#debug_MS("(getUrl) ------------------------------------------------------- START = getUrl ------------------------------------------------------")
	#debug_MS("(getUrl) ### URL = {0} ###".format(url))
	for cook in cj:
		debug_MS("(getUrl) ### COOKIE = {0} ###".format(str(cook)))
	opener = build_opener(HTTPCookieProcessor(cj))
	try:
		if header:
			opener.addheaders = header
		else:
			opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0')]
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
		if hasattr(e, 'code'):
			failing("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
			xbmcgui.Dialog().notification((translation(30521).format('URL')), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 15000)
		elif hasattr(e, 'reason'):
			failing("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
			xbmcgui.Dialog().notification((translation(30521).format('URL')), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 15000)
		content = ""
		return sys.exit(0)
	opener.close()
	try: cj.save(cookie, ignore_discard=True, ignore_expires=True)
	except: pass
	return content

def ADDON_operate(INPUT_STREAM):
	js_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.GetAddonDetails", "params": {"addonid":"'+INPUT_STREAM+'", "properties": ["enabled"]}, "id":1}')
	if '"enabled":false' in js_query:
		try:
			xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": {"addonid":"'+INPUT_STREAM+'", "enabled":true}, "id":1}')
			failing("(ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *inputstream.adaptive* ist NICHT aktiviert !!! #####\n##### Es wird jetzt versucht die Aktivierung durchzuführen !!! #####")
		except: pass
	if '"error":' in js_query:
		xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30501))
		failing("(ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *inputstream.adaptive* ist NICHT installiert !!! #####\n##### Bitte KODI-Krypton (Version 17 oder höher) installieren, Diese enthalten das erforderliche Addon im Setup !!! #####")
		return False
	if '"enabled":true' in js_query:
		return True

def index():
	content = getUrl(baseURL+"mediathek")
	debug_MS("(index) -------------------------------------------------------- START = index -------------------------------------------------------")
	counter = 0
	result = content[content.find('class="filter-element">Dein TELE 5</li>')+1:]
	result = result[:result.find('class="filter-element">')]
	selection = re.findall('<a href="(.+?)">(.+?)</a>', result, re.DOTALL)
	for url, title in selection:
		counter += 1
		if url[:4] != "http" and url[:1] == "/":
			url1 = "https://www.tele5.de"+url
		elif url[:4] != "http" and url[:1] != "/":
			url1 = baseURL+url
		name = cleanTitle(title)
		debug_MS("(index) nr.{0} **** STANDARD ### NAME = {1} ### URL-1 = {2} ### newCODE = otherCATEGORIES||moviesFIRST ###".format(str(counter), name, url1))
		filtered = False
		for word in blackLIST:
			if word and word.strip() == name:
				debug_MS("(index) nr.{0} ––– GEFILTERT ### NAME = {1} ### URL-1 = {2} ### newCODE = otherCATEGORIES||moviesFIRST ###".format(str(counter), name, url1))
				filtered = True
		if filtered:
			continue
		if "filme-online" in url1:
			addDir(name, url1, "listMovies", icon, CODE="moviesFIRST")
		else:
			addDir(name, url1, "listCluster", icon, CODE="otherCATEGORIES", TRANSMIT_URL=url1)
	if enableAdjustment:
		addDir(translation(30607), "", "aSettings", icon)
		if enableInputstream:
			if ADDON_operate('inputstream.adaptive'):
				addDir(translation(30608), "", "iSettings", icon)
			else:
				addon.setSetting("inputstream", "false")
	xbmcplugin.endOfDirectory(pluginhandle)

def listMovies(url, CODE=""):
	startURL = url
	filmList = []
	filmCount = 1
	content = getUrl(url)
	debug_MS("(listMovies) -------------------------------------------------- START = listMovies --------------------------------------------------")
	debug_MS("(listMovies) *[1]* ### URL = {0} ### CODE = {1} ###".format(url, CODE))
	if "ce_teaserelement" in content and "filme-online" in startURL:
		match = re.findall('ce_teaserelement(.*?)<div class="user-overlay">', content, re.DOTALL)
		for chtml in match:
			url1 = re.compile('href="([^"]+?)"', re.DOTALL).findall(chtml)[0]
			if "filme-online/videos" in url1:
				filmList.append(url1)
		if filmList:
			debug_MS("(listMovies) *[2]* ##### filmList = {0} #####".format(str(filmList)))
			if CODE =="no_RESULT_FIRST":
				filmCount += 1
				newCode = "moviesSECOND"
			elif CODE =="no_RESULT_SECOND":
				filmCount += 2
				newCode = "moviesTHIRD"
			else:
				newCode = "moviesFIRST"
			forwardURL = filmList[filmCount]
			debug_MS("(listMovies) *[3]* ### startURL = {0} ### forwardURL = {1} ### newCODE = {2} ###".format(startURL, forwardURL, newCode))
			listEpisodes(url=forwardURL, image=icon, CODE=newCode, TRANSMIT_URL=startURL)
		else:
			failing("(listMovies) ERROR=ERROR=ERROR-FilmList : Konnte KEINE Film-Liste zur Weiterverarbeitung zusammenstellen !")
			return xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30523), icon, 8000)
	xbmcplugin.endOfDirectory(pluginhandle)

def listCluster(url, image, CODE="", TRANSMIT_URL=""):
	debug_MS("(listCluster) -------------------------------------------------- START = listCluster -------------------------------------------------")
	if url[:4] != "http":
		url = baseURL+url
	if TRANSMIT_URL !="" and TRANSMIT_URL[:4] != "http":
		TRANSMIT_URL = baseURL+TRANSMIT_URL
	debug_MS("(listCluster) ### URL = {0} ### TRANSMIT_URL = {1} ###".format(url, TRANSMIT_URL))
	debug_MS("(listCluster) ### CODE = {0} ### THUMB = {1} ###".format(CODE, image))
	html = getUrl(url)
	if not listSeasons(html, image, CODE, TRANSMIT_URL):
		debug_MS("(listCluster) --- noSEASONS --- ### newCODE = no_SEASONS ### newTRANSMIT_URL = {0} ### SEASON = 0 ###".format(url))
		debug_MS("(listCluster) --- noSEASONS --- ### THUMB = {0} ###".format(image))
		listVideos(html, image, SEASON_Number=0, CODE="no_SEASONS", TRANSMIT_URL=url)
	xbmcplugin.endOfDirectory(pluginhandle)

def listSeasons(html, image, CODE, TRANSMIT_URL):
	debug_MS("(listSeasons) ------------------------------------------------ START = listSeasons -----------------------------------------------")
	response = html
	EXCLUSION = ['app', 'tele5.de/app', 'brain-faq', 'darker-net', '.de/detail', '.de/live', 'dein-muenchen', 'europa-ist', 'filmarchiv', 'filme-online', 'filmfreeway', 'hellasfilmbox', 'killerpost', 'lern-woche', 'ostblockbuster', '/quiz', 'schlefaz.de', 'schlefaz.shop', 'schlefaz/staffel', 'serien-online', 'spielfilme', 'trailer', 'vertikale-', 'yeehaw']
	namesENDING = ('ofes-mattscheibe', 'serien', 'serien-online')
	numET =0
	FOUND = 0
	count = 0
	pos1 = 0
	pos2 = 0
	pos3 = 0
	pos4 = 0
	unWANTED_1 = []
	if 'class="secondary-nav__list__item more dropdown' in response or '<h1 class="ce_headline clear first">' in response or 'ce_teaserelement' in response or 'ce_tele5slider' in response:
		if ('class="secondary-nav__list__item more dropdown' in response and any(TRANSMIT_URL.endswith(end) for end in namesENDING) and CODE !="another_selection"):
			result_1 = re.findall('class="secondary-nav__list__item more dropdown(.+?)</ul>', response, re.DOTALL)
			for chtml in result_1:
				if "Ganze Folgen" in chtml or "Specials" in chtml or "Video Clips" in chtml or "Voting" in chtml: # only show items  that contain this words
					FOUND = 1
					selection = re.findall('<a (.+?)</li>', chtml, re.DOTALL)
					for item in selection:
						try:
							url1 = re.compile('href="(.+?)" class=', re.DOTALL).findall(item)[0]
							if not "<span>" in item and ("Ganze Folgen" in item or "Specials" in item or "Video Clips" in item or "Voting" in item):
								if "Ganze Folgen" in item and not "Specials" in item and not "Video Clips" in item and not "Voting" in item:
									if "kalkofes-mattscheibe" in url1:
										addDir("Ganze Folgen - Premiere Klassiker", "tv/kalkofes-mattscheibe/premiere-klassiker", "listEpisodes", image, CODE="one_selection")
										addDir("Ganze Folgen - Kalkofes Mattscheibe", "tv/kalkofes-mattscheibe/videos", "listEpisodes", image, CODE="one_selection")
									else:
										addDir("Ganze Folgen", url1, "listEpisodes", image, CODE="one_selection")
								elif "Specials" in item and not "Ganze Folgen" in item and not "Video Clips" in item and not "Voting" in item:
									addDir("Specials", url1, "listEpisodes", image, CODE="one_selection")
								elif "Video Clips" in item and not "Ganze Folgen" in item and not "Specials" in item and not "Voting" in item:
									addDir("Video Clips", url1, "listEpisodes", image, CODE="one_selection")
								elif "Voting" in item and not "Ganze Folgen" in item and not "Specials" in item and not "Video Clips" in item:
									addDir("Voting", url1, "listEpisodes", image, CODE="one_selection")
								debug_MS("(listSeasons) *[1]* ### URL-1 = {0} ### newCODE = one_selection ### newTRANSMIT_URL = XXX ###".format(url1))
							elif "<span>" in item and ("Ganze Folgen" in item or "Specials" in item or "Video Clips" in item or "Voting" in item):
								if "Ganze Folgen" in item and not "Specials" in item and not "Video Clips" in item and not "Voting" in item:
									if "kalkofes-mattscheibe" in url1:
										addDir("Ganze Folgen - Premiere Klassiker", "tv/kalkofes-mattscheibe/premiere-klassiker", "listCluster", image, CODE="another_selection", TRANSMIT_URL="tv/kalkofes-mattscheibe/premiere-klassiker")
										addDir("Ganze Folgen - Kalkofes Mattscheibe", "tv/kalkofes-mattscheibe/videos", "listCluster", image, CODE="another_selection", TRANSMIT_URL="tv/kalkofes-mattscheibe/videos")
									else:
										addDir("Ganze Folgen", url1, "listCluster", image, CODE="another_selection", TRANSMIT_URL=url1)
								elif "Specials" in item and not "Ganze Folgen" in item and not "Video Clips" in item and not "Voting" in item:
									addDir("Specials", url1, "listCluster", image, CODE="another_selection", TRANSMIT_URL=url1)
								elif "Video Clips" in item and not "Ganze Folgen" in item and not "Specials" in item and not "Voting" in item:
									addDir("Video Clips", url1, "listCluster", image, CODE="another_selection", TRANSMIT_URL=url1)
								elif "Voting" in item and not "Ganze Folgen" in item and not "Specials" in item and not "Video Clips" in item:
									addDir("Voting", url1, "listCluster", image, CODE="another_selection", TRANSMIT_URL=url1)
								debug_MS("(listSeasons) *[1+1]* ### URL-11 = {0} ### newCODE = another_selection ### newTRANSMIT_URL = {1} ###".format(url1, url1))
						except:
							pos1 += 1
							failing("(listSeasons) Fehler-Eintrag-01 : {0}".format(str(item)))
							if pos1 > 1 and count == 0:
								count += 1
								xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30523), icon, 8000)
			debug_MS("(listSeasons) ++++ Zusammenfassung der Seasonliste +++ GEFUNDEN in Rubrik-Nummer = {0} +++".format(FOUND))
		if '<h1 class="ce_headline clear first">' and 'Alle Specials</h1>' in response and FOUND == 0:
			result_2 = re.findall('<div class="ce_text block">(.*?)class="dividerElement">', response, re.DOTALL)
			for chtml in result_2:
				if not '<span class="broadcast"' in chtml: # dont show items = Empfehlungen
					FOUND = 2
					try:
						matchUT = re.compile('href="([^"]+?)">([^<]+?)</a>', re.DOTALL).findall(chtml)
						for url2, title in matchUT:
							name1 = cleanTitle(title)
							name2 = "[COLOR lime]* [/COLOR]"+cleanTitle(title)
							if not any(x in url2 for x in EXCLUSION):
								debug_MS("(listSeasons) *[2]* ### NAME = {0} ### URL-2 = {1} ###".format(name1, url2))
								debug_MS("(listSeasons) *[2]* ### oldCODE = {0} ### TRANSMIT_URL = {1} ###".format(CODE, TRANSMIT_URL))
								addDir(name2, url2, "listCluster", icon, CODE="more_selection", TRANSMIT_URL=TRANSMIT_URL)
					except:
						pos2 += 1
						failing("(listSeasons) Fehler-Eintrag-02 : {0}".format(str(chtml)))
						if pos2 > 1 and count == 0:
							count += 1
							xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30523), icon, 8000)
			debug_MS("(listSeasons) ++++ Zusammenfassung der Seasonliste +++ GEFUNDEN in Rubrik-Nummer = {0} +++".format(FOUND))
		if ('ce_teaserelement' in response or 'ce_tele5slider' in response) and not '<a class="ce_videoelementnexx-related__container__video"' in response and FOUND == 0:
			if 'ce_teaserelement' in response:
				result_3 = re.findall('ce_teaserelement(.*?)<div class="user-overlay">', response, re.DOTALL)
				for chtml in result_3:
					if not '<span class="broadcast"' in chtml: # dont show items = Empfehlungen
						numET +=1
						FOUND = 3
						try:
							url3 = re.compile('href="([^"]+?)"', re.DOTALL).findall(chtml)[0]
							if url3[:4] != "http":
								url3 = baseURL+url3
							if not any(x in url3.lower() for x in EXCLUSION) and url3[-9:].lower() != "mediathek":
								if ".de/videos/" in url3.lower() and not "eigenproduktionen/" in url3.lower() and not "star-trek-vlog" in url3.lower():
									url3 = url3.replace('.de/videos/boomarama', '.de/tv/boomarama-3000').replace('.de/videos/knicksfuerknigge', '.de/tv/knicks-fuer-knigge').replace('.de/videos/Playlist/soundofmylife', '.de/tv/playlist-sound-of-my-life').replace('.de/videos/star-trek-', '.de/tv/star-trek/').replace('eigenproduktionen/metaboheme', 'metaboheme').replace('.de/videos/', '.de/tv/').replace('serien/', '')+"/videos"
								unWANTED_1.append(url3) # make a List of "unWANTED_1(url1s)" to hide the same URL in next Level
								try:
									title = re.compile('<h2>(.+?)</h2>', re.DOTALL).findall(chtml)[0]
									title = cleanTitle(title)
								except: title =""
								try:
									subtitle = re.compile('<span class="shortdesc">(.+?)</span>', re.DOTALL).findall(chtml)[0]
									subtitle = cleanTitle(subtitle)
								except: subtitle =""
								if title == "" and subtitle == "" and url3 != "":
									title = url3.split('/')[-1].split('-')[0].title()+" - No."+str(numET)
								if title == "" and subtitle != "" :
									title = subtitle
								if subtitle !="" and subtitle != title:
									title = title+" - "+subtitle
								try:
									thumb = re.compile(r'source srcset="(?:.+?w, )?(.+?(?:\.jpg [0-9]+w|\.jpeg [0-9]+w|\.png [0-9]+w))', re.DOTALL).findall(chtml)[0].split('g ')[0].strip()+"g"
								except:
									try: thumb = re.compile('<img src="([^"]+?)"', re.DOTALL).findall(chtml)[0]
									except: thumb = ""
								if thumb != "" and thumb[:4] != "http":
									thumb = baseURL+thumb
								if "making of " in title.lower() or "/videos?ve_" in url3.lower():
									continue
								debug_MS("(listSeasons) *[3]* ### NAME = {0} ### URL-3 = {1} ###".format(title, url3))
								debug_MS("(listSeasons) *[3]* ### oldCODE = {0} ### TRANSMIT_URL = {1} ###".format(CODE, TRANSMIT_URL))
								debug_MS("(listSeasons) *[3]* ### THUMB = {0} ###".format(thumb))
								addDir(title, url3, "listCluster", thumb, CODE="more_selection", TRANSMIT_URL=TRANSMIT_URL)
						except:
							pos3 += 1
							failing("(listSeasons) Fehler-Eintrag-03 : {0}".format(str(chtml)))
							if pos3 > 1 and count == 0:
								count += 1
								xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30523), icon, 8000)
				debug_MS("(listSeasons) ++++ Zusammenfassung der Seasonliste +++ GEFUNDEN in Rubrik-Nummer = {0} +++".format(FOUND))
			if 'ce_tele5slider' in response:
				result_4 = re.findall('ce_tele5slider(.*?)</ul>', response, re.DOTALL)
				for entries in result_4:
					part = entries.split('data-frame=')
					for i in range(1, len(part), 1):
						element = part[i]
						if not '<span class="broadcast"' in element: # dont show items = Empfehlungen
							FOUND = 4
							try:
								url4 = re.compile('href="([^"]+?)"', re.DOTALL).findall(element)[0]
								if url4[:4] != "http":
									url4 = baseURL+url4
								if not any(x in url4.lower() for x in EXCLUSION) and url4.lower()[-9:].lower() != "mediathek":
									if ".de/videos/" in url4.lower() and not "eigenproduktionen/" in url4.lower() and not "star-trek-vlog" in url4.lower():
										url4 = url4.replace('.de/videos/boomarama', '.de/tv/boomarama-3000').replace('.de/videos/knicksfuerknigge', '.de/tv/knicks-fuer-knigge').replace('.de/videos/Playlist/soundofmylife', '.de/tv/playlist-sound-of-my-life').replace('.de/videos/star-trek-', '.de/tv/star-trek/').replace('.de/videos/', '.de/tv/').replace('serien/', '')+"/videos"
									unWANTED_2 = url4 # hide the same URL - if formally found in List of "unWANTED_1(url1s)"
									title = re.compile('<h3.+?(>.+?)</h3>', re.DOTALL).findall(element)[0].split('>')[1]
									title = cleanTitle(title)
									try:
										subtitle = re.compile('<h4.+?(>.+?)</h4>', re.DOTALL).findall(element)[0].split('>')[1]
										subtitle = cleanTitle(subtitle)
									except: subtitle =""
									if subtitle !="" and subtitle != title:
										title = title+" - "+subtitle
									try: thumb = re.compile('<img src="([^"]+?)"', re.DOTALL).findall(element)[0]
									except: thumb = ""
									if thumb != "" and thumb[:4] != "http":
										thumb = baseURL+thumb
									if not any(x in unWANTED_2 for x in unWANTED_1):
										if "making of " in title.lower() or "/videos?ve_" in url4.lower():
											continue
										debug_MS("(listSeasons) *[4]* ### NAME = {0} ### URL-4 = {1} ###".format(title, url4))
										debug_MS("(listSeasons) *[4]* ### oldCODE = {0} ### TRANSMIT_URL = {1} ###".format(CODE, TRANSMIT_URL))
										debug_MS("(listSeasons) *[4]* ### THUMB = {0} ###".format(thumb))
										addDir(title, url4, "listCluster", thumb, CODE="more_selection", TRANSMIT_URL=TRANSMIT_URL)
							except:
								pos4 += 1
								failing("(listSeasons) Fehler-Eintrag-04 : {0}".format(str(element)))
								if pos4 > 1 and count == 0:
									count += 1
									xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30523), icon, 8000)
				debug_MS("(listSeasons) ++++ Zusammenfassung der Seasonliste +++ GEFUNDEN in Rubrik-Nummer = {0} +++".format(FOUND))
		if 'class="ce_videoelementnexx-video__player"' in response and not '<a class="ce_videoelementnexx-related__container__video"' in response:
			if not any(x in TRANSMIT_URL.lower() for x in EXCLUSION) and TRANSMIT_URL[-9:].lower() != "mediathek" and FOUND > 0:
				debug_MS("(listSeasons) *[5]* ### newCODE = only_one ### TRANSMIT_URL = {0} ### SEASON = 0 ###".format(TRANSMIT_URL))
				listVideos(html, image=icon, SEASON_Number=0, CODE="only_one", TRANSMIT_URL=TRANSMIT_URL)
		if FOUND < 1:
			return False
		return True
	return False

def listEpisodes(url, image, SEASON_Number=0, CODE="", TRANSMIT_URL=""):
	debug_MS("(listEpisodes) ----------------------------------------------- START = listEpisodes ----------------------------------------------")
	if url[:4] != "http":
		url = baseURL+url
	if TRANSMIT_URL !="" and TRANSMIT_URL[:4] != "http":
		TRANSMIT_URL = baseURL+TRANSMIT_URL
	debug_MS("(listEpisodes) ### URL = {0} ### TRANSMIT_URL = {1} ###".format(url, TRANSMIT_URL))
	debug_MS("(listEpisodes) ### CODE = {0} ### SEASON_Number = {1} ### THUMB = {2} ###".format(CODE, SEASON_Number, image))
	html = getUrl(url)
	listVideos(html, image, SEASON_Number, CODE, TRANSMIT_URL)
	xbmcplugin.endOfDirectory(pluginhandle)

def listVideos(html, image, SEASON_Number, CODE, TRANSMIT_URL):
	debug_MS("(listVideos) -------------------------------------------------- START = listVideos --------------------------------------------------")
	response = html
	EXCLUSION = ['Kalkofes MATTsommer -', 'KALKOFES MATTSOMMER -', 'Kalkofes Wählscheibe -', 'KALKOFES WÄHLSCHEIBE -', 'Star Trek VLOG -', 'STAR TREK VLOG -'] # hide Episodetitle that are the same as Seriesname
	EP1_unwanted = ['best of', 'jahre', 'tele 5', 'teil '] # hide title with number in Episode-Numbers
	EP2_unwanted = ['2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020'] # hide number in Episode-Numbers
	title_ENTRY = 0
	FOUND = 0
	count = 0
	pos1 = 0
	pos2 = 0
	unWANTED_1 = []
	SeasonLIST = []
	if ('class="ce_videoelementnexx-video__player"' in response or '<a class="ce_videoelementnexx-related__container__video"' in response):
		if '<a class="ce_videoelementnexx-related__container__video"' in response:
			result_1 = re.findall('<a class="ce_videoelementnexx-related__container__video"(.+?)</a>', response, re.DOTALL)
			for chtml in result_1:
				if not 'data-type="Most Active"' in chtml: # dont show items = Besonders beliebt
					FOUND = 1
					try:
						try:
							duration = re.compile(r'''data-runtime=(?:'|")?(.+?)\s+data-''', re.DOTALL).findall(chtml)[0].replace('"', '').replace("'", "")
							context = duration.strip()
							if duration !="" and "min" in duration and not "sek" in duration:
								duration = duration.rstrip('min').strip() # von hinten entfernen = s.rstrip("min")
								duration = int(duration)*60
							elif duration !="" and not "min" in duration and "sek" in duration:
								duration = duration.rstrip('sek').strip() # von hinten entfernen = s.rstrip("sek")
						except:
							duration = ""
							context = ""
						videoID_1 = re.compile(r'''data-id=(?:'|")?(.+?)\s+data-''', re.DOTALL).findall(chtml)[0].replace('"', '').replace("'", "").strip()
						unWANTED_1.append(videoID_1) # make a List of "unWANTED_1(VideoIDs)" to hide the same VideoID in next Level
						try:
							normalPlot = re.compile(r'''data-description=(?:'|")?(.+?)\s*data-''', re.DOTALL).findall(chtml)[0]
							normalPlot = normalPlot[0:-1]
							plot = cleanTitle(normalPlot).replace('"', '“')
						except: plot = ""
						try:
							season = re.compile(r'''data-season=(?:'|")?(.+?)\s+data-''', re.DOTALL).findall(chtml)[0].replace('"', '').replace("'", "").strip()
							if str(season)[:1] == "0": # von vorne entfernen = s.lstrip("0")
								season = str(season).lstrip('0')
						except: season = ""
						if season !="" and season not in SeasonLIST and CODE !="moviesFIRST" and CODE !="moviesSECOND" and CODE !="moviesTHIRD":
							SeasonLIST.append(season)
						try: thumb = re.compile(r'ce_videoelementnexx-related__container__video-thumbnail__image.+?(http.+?(?:\.jpg|\.jpeg|\.png))', re.DOTALL).findall(chtml)[-1].replace('\/', '/')
						except: thumb = ""
						title = re.compile('ce_videoelementnexx-related__container__video-title.*?">(.+?)</div>', re.DOTALL).findall(chtml)[0]
						title_ORIGINAL = cleanTitle(title)
						title_COPY = title_ORIGINAL
						episode = ""
						try:
							title_COPY2 = title.replace('Staffel '+str(season), '').strip()
							if not any(x in title_COPY2.lower() for x in EP1_unwanted) and CODE !="moviesFIRST" and CODE !="moviesSECOND" and CODE !="moviesTHIRD":
								matchEP = re.compile('([0-9]+)', re.DOTALL).findall(title_COPY2)
								if not any(x in matchEP[0] for x in EP2_unwanted) and season !="":
									episode = int(matchEP[0])
						except: pass
						if title_COPY != "" and any(x in title_COPY for x in EXCLUSION):
							for item in EXCLUSION:
								if item in title_COPY:
									title_COPY = title_COPY.replace(item, '').strip()
						try:
							seriesname = re.compile('class="ce_videoelementnexx-related__container__video-runtime">(.+?)</div>', re.DOTALL).findall(chtml)[0].replace('- Ganze Folge', '').replace('n online schauen', '')
							seriesname = cleanTitle(seriesname)
						except: seriesname = ""
						if seriesname != "" and context in seriesname: # dont show Minutes in Title = Hausgemachtes | 4 min
							seriesname = ""
						if seriesname == "":
							try:
								seriesname = re.compile(r'class="ce_serieselementnexxtv-(?:series|playlist)__title">(.+?)<div class=', re.DOTALL).findall(response)[0].replace('- Ganze Folge', '').replace('n online schauen', '')
								seriesname = cleanTitle(seriesname)
							except: seriesname = ""
						extraPlot = re.compile('class="ce_videoelementnexx-related__container__video-description">(.+?)</div>', re.DOTALL).findall(chtml)[0]
						extraPlot_ORIGINAL = cleanTitle(extraPlot).replace('"', '“')
						extraPlot_COPY = extraPlot_ORIGINAL[0:-4] # replace the last three points in Text ( ...)
						if extraPlot_COPY != "" and extraPlot_COPY.lower() not in plot.lower():
							plot = "[COLOR lime]* [/COLOR]"+extraPlot_ORIGINAL+"[COLOR lime] *[/COLOR]"+"\n\n"+plot
						if title_COPY != "" and season != "" and int(SEASON_Number) !=0 and season == SEASON_Number:
							title_ENTRY += 1
							if "staffel" in title_ORIGINAL.lower() and "folge" in title_ORIGINAL.lower():
								name = title_COPY.lower().replace('folge 35: die letzte folge der staffel - happy hour', '').split('staffel')[0]+"Folge "+title_COPY.split('Folge')[1].strip()
							else:
								name = title_COPY.replace('- Clips -', '-').replace('Clips -', '').strip()
							debug_MS("(listVideos) *[1]* ### NAME = {0} ### videoID_1 = {1} ### DURATION = {2} ###".format(name, videoID_1, duration))
							debug_MS("(listVideos) *[1]* ### SERIE = {0} ### SEASON = {1} ### EPISODE = {2} ###".format(seriesname, season, episode))
							debug_MS("(listVideos) *[1]* ### THUMB = {0} ###".format(thumb))
							addLink(name, str(videoID_1), 'playVideo', thumb, plot, duration, season, episode, seriesname)
						elif title_COPY != "" and season == "":
							title_ENTRY += 1
							name = title_COPY.replace('- Clips -', '-').replace('Clips -', '').strip()
							debug_MS("(listVideos) *[1+1]* ### NAME = {0} ### videoID_1 = {1} ### DURATION = {2} ###".format(name, videoID_1, duration))
							debug_MS("(listVideos) *[1+1]* ### SERIE = {0} ### SEASON = {1} ### EPISODE = {2} ###".format(seriesname, season, episode))
							debug_MS("(listVideos) *[1+1]* ### THUMB = {0} ###".format(thumb))
							addLink(name, str(videoID_1), 'playVideo', thumb, plot, duration, season, episode, seriesname)
					except:
						pos1 += 1
						failing("(listVideos) Fehler-Eintrag-01 : {0}".format(str(chtml)))
						if pos1 > 1 and count == 0:
							count += 1
							xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30523), icon, 8000)
			debug_MS("(listVideos) ++++ Zusammenfassung der Videoliste +++ GEFUNDEN in Rubrik-Nummer = {0} +++".format(FOUND))
		if 'class="ce_videoelementnexx-video__player"' in response:
			result_2 = re.findall(r'class="ce_videoelementnexx-video__player"(.+?)(?:class="ce_videoelementnexx-related__container__video"|class="dividerElement">|<footer id="footer">)', response, re.DOTALL)
			for chtml in result_2:
				if 'id="video-player"' in chtml:
					FOUND = 2
					try:
						videoID_2 = re.compile(r'''data-id=(?:'|")?(.+?)\s+data-''', re.DOTALL).findall(chtml)[0].replace('"', '').replace("'", "").strip()
						unWANTED_2 = videoID_2 # hide the same VideoID - if formally found in List of "unWANTED_1(VideoIDs)"
						try:
							duration = re.compile(r'''data-runtime=(?:'|")?(.+?)\s+data-''', re.DOTALL).findall(chtml)[0].replace('"', '').replace("'", "")
							if duration !="" and "min" in duration and not "sek" in duration:
								duration = duration.rstrip('min').strip() # von hinten entfernen = s.rstrip("min")
								duration = int(duration)*60
							elif duration !="" and not "min" in duration and "sek" in duration:
								duration = duration.rstrip('sek').strip() # von hinten entfernen = s.rstrip("sek")
						except: duration = ""
						title = re.compile('class="ce_videoelementnexx-video__title">(.+?)<div class', re.DOTALL).findall(chtml)[0]
						name = cleanTitle(title)
						try:
							seriesname = re.compile(r'class="ce_serieselementnexxtv-(?:series|playlist)__title">(.+?)<div class=', re.DOTALL).findall(response)[0].replace('- Ganze Folge', '').replace('n online schauen', '')
							seriesname = cleanTitle(seriesname)
						except: seriesname = ""
						try: # grap - Plot-1
							desc = re.compile('ce_videoelementnexx-video__description">(.+?)\s*</div>', re.DOTALL).findall(chtml)[0]
							plot = re.sub(r'\<.*?\>', '', desc)
							plot = cleanTitle(plot)
						except: plot = ""
						if plot == "":
							try: # grap - Plot-2
								desc = re.compile('<div class="ce_text block">(.+?)\s*<tbody>', re.DOTALL).findall(chtml)[0]
								desc = desc.replace('</p>', '\n')
								plot = re.sub(r'\<.*?\>', '', desc)
								plot = cleanTitle(plot)
							except: plot = ""
						try: # grap - Director and Author
							resultDW = chtml[chtml.find('<tbody>')+1:]
							resultDW = resultDW[:resultDW.find('</tr>')]
							matchD = re.compile(r'Regie:?</span>:?([^<]+?)</p>', re.DOTALL).findall(resultDW)[0]
							director = cleanTitle(matchD)
							matchW = re.compile(r'Drehbuch:?</span>:?([^<]+?)</p>', re.DOTALL).findall(resultDW)[0]
							writer = cleanTitle(matchW)
						except:
							director =""
							writer =""
						try: thumb = re.compile(r'property="og:image" content="(http.+?(?:\.jpg|\.jpeg|\.png))', re.DOTALL).findall(response)[0].replace('\/', '/')
						except: thumb = ""
						if not any(x in unWANTED_2 for x in unWANTED_1):
							debug_MS("(listVideos) *[2]* ### NAME = {0} ### videoID_2 = {1} ### DURATION = {2} ###".format(name, videoID_2, duration))
							debug_MS("(listVideos) *[2]* ### SERIE = {0} ### DIRECTOR = {1} ### WRITER = {2} ###".format(seriesname, director, writer))
							debug_MS("(listVideos) *[2]* ### THUMB = {0} ###".format(thumb))
							addLink(name, str(videoID_2), 'playVideo', thumb, plot, duration, seriesname=seriesname, director=director, writer=writer)
						elif any(x in unWANTED_2 for x in unWANTED_1):
							debug_MS("(listVideos) ~[2+2]~ AUSGEFILTERT ~~ NAME = {0} ~~~ videoID_2 = {1} ~~~ DURATION = {2} ~~~".format(name, videoID_2, duration))
							debug_MS("(listVideos) ~[2+2]~ AUSGEFILTERT ~~ SERIE = {0} ~~~ DIRECTOR = {1} ~~~ WRITER = {2} ~~~".format(seriesname, director, writer))
							debug_MS("(listVideos) ~[2+2]~ AUSGEFILTERT ~~ THUMB = {0} ~~~".format(thumb))
					except:
						pos2 += 1
						failing("(listVideos) Fehler-Eintrag-02 : {0}".format(str(chtml)))
						if pos2 > 1 and count == 0:
							count += 1
							xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30523), icon, 8000)
			debug_MS("(listVideos) ++++ Zusammenfassung der Videoliste +++ GEFUNDEN in Rubrik-Nummer = {0} +++".format(FOUND))
		if (CODE =="one_selection" or CODE =="no_SEASONS") and SeasonLIST and title_ENTRY == 0:
			FOUND = 3
			url3 = TRANSMIT_URL
			newCode = "staffel_selection"
			try:
				desc = re.compile('<meta name="description" content="(.+?)">', re.DOTALL).findall(response)[0]
				plot = cleanTitle(desc)
			except: plot = ""
			for season in SeasonLIST:
				debug_MS("(listVideos) *[3]* ### NAME = {0} ### URL-3 = {1} ### SEASON_Number = {2} ###".format("Staffel "+str(season), url3, season))
				debug_MS("(listVideos) *[3]* ### newCODE = {0} ### newTRANSMIT_URL = XXX ### THUMB = {1} ###".format(newCode, image))
				addDir("[B][COLOR lime]Staffel "+str(season)+"[/COLOR][/B]", url3, "listEpisodes", image, plot, SEASON_Number=season, CODE=newCode)
			debug_MS("(listVideos) ++++ Zusammenfassung der Videoliste +++ GEFUNDEN in Rubrik-Nummer = {0} +++".format(FOUND))
	else:
		if (CODE =="moviesFIRST" or CODE =="moviesSECOND") and FOUND == 0:
			FOUND = 4
			url4 = TRANSMIT_URL
			if CODE =="moviesFIRST":
				newCode = "no_RESULT_FIRST"
			elif CODE =="moviesSECOND":
				newCode = "no_RESULT_SECOND"
			debug_MS("(listVideos) *[4]* ### URL-4 = {0} ### newCODE = {1} ###".format(url4, newCode))
			debug_MS("(listVideos) ++++ Zusammenfassung der Videoliste +++ GEFUNDEN in Rubrik-Nummer = {0} +++".format(FOUND))
			return listMovies(url4, CODE=newCode)
	if FOUND < 1:
		failing("(listVideos) ??? Evtl. ERROR ??? - Einträge-ALLE : Konnte die abgefragten Einträge NICHT auf der Webseite finden !")
		xbmcgui.Dialog().notification((translation(30522).format('Einträge')), translation(30524), icon, 8000)
		return sys.exit(0)

def playVideo(url):
	debug_MS("(playVideo) -------------------------------------------------- START = playVideo --------------------------------------------------")
	#POST https://api.nexx.cloud/v3/759/playlists/byid/4574 additionalfields=language%2Cchannel%2Cactors%2Cstudio%2Clicenseby%2Cslug%2Cfileversion&addInteractionOptions=1&addStatusDetails=1&addStreamDetails=1&addFeatures=1&addCaptions=1&addScenes=1&addHotSpots=1&addBumpers=0&captionFormat=data&addItemData=1&includeEpisodes=1
	debug_MS("(playVideo) ### URL = {0} ###".format(url))
	stream_url = False
	headerfields = "User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0"
	try:
		content = getUrl('https://arc.nexx.cloud/api/video/'+url+'.json')
		debug_MS("(playVideo) *[1]* ##### URL-CONTENT-NeXX-1 = {0} #####".format(content))
		result = json.loads(content)
		secret = ""
		if "token" in result['result']['protectiondata'] and result['result']['protectiondata']['token'] != "":
			secret = "?hdnts="+result['result']['protectiondata']['token']
		if "tokenHLS" in result['result']['protectiondata'] and result['result']['protectiondata']['tokenHLS'] != "":
			secretHLS = "?hdnts="+result['result']['protectiondata']['tokenHLS']
		else:
			secretHLS = secret
		HLS = "https://"+result['result']['streamdata']['cdnShieldHTTP']+result['result']['streamdata']['azureLocator']+"/"+str(result['result']['general']['ID'])+"_src.ism/Manifest(format=m3u8-aapl)"+secretHLS
		# HLS-Url = https://tele5nexx.akamaized.net/a4eebb35-4bea-4801-8560-f92585bf6565/1547335_src.ism/Manifest(format=m3u8-aapl)
		stream_url = HLS
		log("(playVideo) HLS-stream : {0}".format(stream_url))
		listitem = xbmcgui.ListItem(path=stream_url)
		if enableInputstream:
			if ADDON_operate('inputstream.adaptive'):
				listitem.setMimeType('application/vnd.apple.mpegurl')
				listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
				listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
			else:
				addon.setSetting("inputstream", "false")
	except:
		failing("(playVideo) ##### Abspielen des Videos NICHT möglich - VideoCode : {0} - #####\n    ########## KEINEN Eintrag für NeXX- Player gefunden !!! ##########".format(url))
		xbmcgui.Dialog().notification((translation(30521).format('PLAY')), translation(30523), icon, 8000)
	if stream_url:
		listitem.setContentLookup(False)
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def cleanTitle(title):
	title = py2_enc(title)
	title = title.replace('\\', '').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&nbsp;', ' ').replace('&#34;', '"').replace('&#39;', '\'').replace('&#039;', '\'').replace('&quot;', '"').replace('&szlig;', 'ß').replace('&ndash;', '-').replace(' //', '.').replace('	', ' ')
	title = title.replace('&Auml;', 'Ä').replace('Ä', 'Ä').replace('&auml;', 'ä').replace('ä', 'ä').replace('&Ouml;', 'Ö').replace('Ö', 'Ö').replace('&ouml;', 'ö').replace('ö', 'ö').replace('&Uuml;', 'Ü').replace('Ü', 'Ü').replace('&uuml;', 'ü').replace('ü', 'ü')
	title = title.replace('u00C4', 'Ä').replace('u00c4', 'Ä').replace('u00E4', 'ä').replace('u00e4', 'ä').replace('u00D6', 'Ö').replace('u00d6', 'Ö').replace('u00F6', 'ö').replace('u00f6', 'ö')
	title = title.replace('u00DC', 'Ü').replace('u00dc', 'Ü').replace('u00FC', 'ü').replace('u00fc', 'ü').replace('u00DF', 'ß').replace('u00df', 'ß').replace('u0026', '&')
	title = title.replace("u00A0", "' '").replace("u00a0", "' '").replace('u003C', '<').replace('u003c', '<').replace('u003E', '>').replace('u003e', '>')
	title = title.replace('u20AC', '€').replace('u20ac', '€').replace('u0024', '$').replace('u00A3', '£').replace('u00a3', '£').replace('</h1>', '').replace('</h2>', '').replace('<div', '').replace('<br />', '')
	title = title.strip()
	return title

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def addVideoList(url, name, image):
	PL = xbmc.PlayList(1)
	listitem = xbmcgui.ListItem(name, thumbnailImage=image)
	listitem.setInfo(type="Video", infoLabels={"Title": name, "Studio": "Tele5", "mediatype": "video"})
	if useThumbAsFanart and image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	listitem.setProperty('IsPlayable', 'true')
	listitem.setContentLookup(False)
	PL.add(url, listitem)

def addLink(name, url, mode, image, plot=None, duration=None, season=None, episode=None, seriesname=None, genre=None, director=None, writer=None):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"TvShowtitle": seriesname, "Title": name, "Plot": plot, "Duration": duration, "Season": season, "Episode": episode, "Genre": genre, "Director": director, "Writer": writer, "Studio": "Tele5", "mediatype": "episode"})
	liz.setArt({'poster': image})
	if useThumbAsFanart and image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.addContextMenuItems([(translation(30654), 'RunPlugin(plugin://{0}?mode=addVideoList&url={1}&name={2}&image={3})'.format(addon.getAddonInfo('id'), quote_plus(u), quote_plus(name), quote_plus(image)))])
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

def addDir(name, url, mode, image, plot=None, SEASON_Number=0, CODE="", TRANSMIT_URL=""):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&image="+quote_plus(image)+"&SEASON_Number="+str(SEASON_Number)+"&CODE="+quote_plus(CODE)+"&TRANSMIT_URL="+quote_plus(TRANSMIT_URL)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
	liz.setArt({'poster': image})
	if useThumbAsFanart and image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
image = unquote_plus(params.get('image', ''))
SEASON_Number = unquote_plus(params.get('SEASON_Number', ''))
CODE = unquote_plus(params.get('CODE', ''))
TRANSMIT_URL = unquote_plus(params.get('TRANSMIT_URL', ''))
referer = unquote_plus(params.get('referer', ''))

if mode == 'aSettings':
	addon.openSettings()
elif mode == 'iSettings':
	xbmcaddon.Addon('inputstream.adaptive').openSettings()
elif mode == 'listMovies':
	listMovies(url, CODE)
elif mode == 'listCluster':
	listCluster(url, image, CODE, TRANSMIT_URL)
elif mode == 'listEpisodes':
	listEpisodes(url, image, SEASON_Number, CODE, TRANSMIT_URL)
elif mode == 'playVideo':
	playVideo(url)
elif mode == 'addVideoList':
	addVideoList(url, name, image)
else:
	index()