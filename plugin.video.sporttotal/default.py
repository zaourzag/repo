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
import datetime
from bs4 import BeautifulSoup
import io
import gzip


global debuging
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
socket.setdefaulttimeout(40)
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath     = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
temp            = xbmc.translatePath(os.path.join(dataPath, 'temp', '')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg')
icon = os.path.join(addonPath, 'icon.png')
if PY2:
	cachePERIOD = int(addon.getSetting("cacheTime"))
	cache = StorageServer.StorageServer(addon.getAddonInfo('id'), cachePERIOD) # (Your plugin name, Cache time in hours)
baseURL = "https://www.sporttotal.tv"

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
		debug("(getUrl) Cookie : {0}".format(str(cook)))
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
		response = opener.open(url, timeout=40)
		if response.info().get('Content-Encoding') == 'gzip':
			content = py3_dec(gzip.GzipFile(fileobj=io.BytesIO(response.read())).read())
		else:
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

def index():
	addDir(translation(30601), "", 'Allsportarts_Overview', icon, ffilter="Uebertragungen")
	addDir(translation(30602), "", 'Allsportarts_Overview', icon, ffilter="Anderes")
	addDir(translation(30603), baseURL+"/highlights", 'selection_Archiv_Highlights', icon, ffilter="")
	addDir(translation(30604), baseURL+"/topclips/", 'Topclips_Categories', icon, category="Top Clips")
	addDir(translation(30605), baseURL+"/ligen/", 'Ligen_Overview', icon)
	addDir(translation(30606), baseURL+"/archiv", 'selection_Archiv_Highlights', icon, ffilter="")
	addDir(translation(30607), baseURL+"/highlights?saison=&liga=&verein=", 'Archiv_Highlights_Ligen_Videos', icon, ffilter="Spielzusammenfassungen")
	addDir(translation(30608), baseURL+"/archiv?saison=&liga=&verein=", 'Archiv_Highlights_Ligen_Videos', icon, ffilter="Wiederholungen")
	addDir(translation(30609), "", "aSettings", icon)
	xbmcplugin.endOfDirectory(pluginhandle) 

def Allsportarts_Overview(ffilter=""):
	debug("(Allsportarts_Overview) ##### URL={0} #####".format(baseURL))
	content = makeREQUEST(baseURL)
	result = content[content.find('Alle Sportarten')+1:]
	result = result[:result.find('</li>')]
	selection = re.findall('class="dropdown-item" href="(.+?)">(.+?)</a>', result, re.DOTALL)
	for url2, title in selection:
		if title != "":
			if url2[:4] != "http" and url2 != "/":
				url2 = baseURL+url2
			name = cleanTitle(title)
			if ffilter == 'Uebertragungen':
				if name !="" and name.lower() != 'fußball':
					addDir(name, url2, 'Livegames_Videos', icon, category=name)
				else:
					addDir("Fußball", baseURL+"/live/", 'Livegames_Videos', icon, category="Fußball")
			elif ffilter == 'Anderes':
				if name !="" and name.lower() != 'fußball':
					addDir(name, url2, 'Topclips_Categories', icon, category=name)
				else:
					addDir("Fußball", baseURL+"/topclips/", 'Topclips_Categories', icon, category="Fußball")
	xbmcplugin.endOfDirectory(pluginhandle)

def Livegames_Videos(url, category=""):
	log("(Livegames_Videos) ##### URL={0} #####".format(url))
	SPORTSNAME = unquote_plus(category)
	content = getUrl(url)
	COMBINATION1 = []
	COMBINATION2 = []
	videoIsolated_List = set()
	count = 0
	pos1 = 0
	if '<div id="livegames' and 'class="livegame-table">' in content:
		result = content[content.find('<section class="container home-tile">')+1:]
		result = result[:result.find('</section>')]
		part = result.split('class="table-link"')
		for i in range(1, len(part), 1):
			element = part[i]
			try:
				vidURL = re.compile('href="(.+?)">', re.DOTALL).findall(element)[0]
				if vidURL[:4] != "http":
					vidURL = baseURL+vidURL
				try: division = re.compile('class="Division">(.+?)</td>', re.DOTALL).findall(element)[0].strip()
				except: division = re.compile('class="staffelname">(.+?)</td>', re.DOTALL).findall(element)[0].strip()
				division = cleanTitle(division)
				teams = re.compile('class="teams">(.+?)</td>', re.DOTALL).findall(element)[0]
				teams = cleanTitle(teams)
				if teams =="":
					continue
				relevance = re.compile('class="date">(.+?)</td>', re.DOTALL).findall(element)[0].strip()
				try:
					datetime_object = datetime.datetime.strptime(relevance, '%d.%m.%Y %H:%M')
				except TypeError:
					datetime_object = datetime.datetime(*(time.strptime(relevance, '%d.%m.%Y %H:%M')[0:6]))
				actualTIME = datetime_object.strftime("%H:%M")
				title = relevance+" - "+teams
				if title in videoIsolated_List:
					continue
				videoIsolated_List.add(title)
				try:
					photo = re.compile('<img.+?src="([^"]+?)"', re.DOTALL).findall(element)[0]
				except: photo = ""
				if photo != "" and photo[:4] != "http":
					photo = baseURL+photo
				if photo != "" and "?w=" in photo:
					photo = photo.split('?w=')[0]+"?w=300"
				if 'class="badge badge-danger">' in element:
					name = "[COLOR chartreuse][B]~ ~ ~  ( LIVE )[/B][/COLOR]  ["+actualTIME+"]  "+teams+"  [COLOR chartreuse][B]~ ~ ~[/B][/COLOR]"
					COMBINATION1.append([datetime_object, name, vidURL, photo])
				else:
					name = relevance+" - "+teams+"  ("+division+")"
					COMBINATION2.append([datetime_object, name, vidURL, photo])
			except:
				pos1 += 1
				failing("(Live_Games) Fehler-Eintrag-01 : {0}".format(str(element)))
				if pos1 > 1 and count == 0:
					count += 1
					xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30522), icon, 8000)
		if COMBINATION1:
			addDir(translation(30610), "", "Livegames_Videos", icon)
			for datetime_object, name, vidURL, photo in sorted(COMBINATION1, key=lambda item:item[0], reverse=False):
				addLink(name, vidURL, "playVideo", photo, background="KEIN HINTERGRUND")
		if COMBINATION2:
			addDir(translation(30611), "", "Livegames_Videos", icon)
			for datetime_object, name, vidURL, photo in sorted(COMBINATION2, key=lambda item:item[0], reverse=False):
				addLink(name, vidURL, "playVideo", photo, background="KEIN HINTERGRUND")
	else:
		return xbmcgui.Dialog().notification(translation(30525), (translation(30526).format(SPORTSNAME.upper()+' - LIVE')), icon, 8000)
	xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=False)

def list_Archiv_Highlights(url, ffilter="", category=""):
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_TITLE)
	debug("(list_Archiv_Highlights) ##### URL={0} ##### FFILTER={1} ##### CATEGORY={2} #####".format(url, ffilter, category))
	content = makeREQUEST(url)
	# <select name="liga" class="form-control">
	result = content[content.find('<select name="'+category+'" class="form-control">'):]
	result = result[:result.find('</select>')]
	selection = re.findall('<option.*?>(.*?)</option>', result, re.DOTALL)
	for title in selection:
		if title != "":
			name = cleanTitle(title)
			if name == "Alle Ligen":
				name = "-- Alle Ligen --"
			addDir(name, url, 'selection_Archiv_Highlights', icon, ffilter=ffilter+"&"+category+"="+name)
	xbmcplugin.endOfDirectory(pluginhandle)

def selection_Archiv_Highlights(url, ffilter=""):
	# Zuordnung = ARCHIV: saison=&liga=&verein= / HIGHLIGHTS: liga=&verein=&saison=
	debug("(selection_Archiv_Highlights) no.1 ##### URL : {0} #####".format(url))
	params = parameters_string_to_dict(ffilter)
	saison = unquote_plus(params.get('saison', '')) 
	liga = unquote_plus(params.get('liga', ''))
	verein = unquote_plus(params.get('verein', ''))
	debug("(selection_Archiv_Highlights) no.2 ##### SAISON={0} ##### LIGA={1} ##### VEREIN={2} #####".format(saison, liga, verein))
	saisonfilter =""
	ligafilter =""
	vereinfilter =""
	if saison !="" and saison !="-- Saison --":
		saisonfilter="&saison="+saison.replace(" ","+")
	if liga !="" and liga !="-- Alle Ligen --":
		ligafilter="&liga="+liga.replace(" ","+")
	if verein !="" and verein !="-- Verein --":
		vereinfilter="&verein="+verein.replace(" ","+")
	if saisonfilter =="":
		addDir(translation(30612), url, 'list_Archiv_Highlights', icon, ffilter=saisonfilter+ligafilter+vereinfilter, category="saison")
		saisonfilter = "saison="
	if ligafilter =="":
		addDir(translation(30613), url, 'list_Archiv_Highlights', icon, ffilter=saisonfilter+ligafilter+vereinfilter, category="liga")
		ligafilter = "&liga="
	if vereinfilter =="":
		addDir(translation(30614), url, 'list_Archiv_Highlights', icon, ffilter=saisonfilter+ligafilter+vereinfilter, category="verein")
		vereinfilter = "&verein="
	addDir(translation(30615), url, 'result_Archiv_Highlights_Ligen', icon, ffilter=saisonfilter+ligafilter+vereinfilter)
	debug("(selection_Archiv_Highlights) no.3 ##### SAISONfilter={0} ##### LIGAfilter={1} ##### VEREINfilter={2} #####".format(saisonfilter, ligafilter, vereinfilter))
	xbmcplugin.endOfDirectory(pluginhandle)

def result_Archiv_Highlights_Ligen(url, ffilter=""):
	debug("(result_Archiv_Highlights_Ligen) no.1 ##### URL={0} ##### FFILTER={1} #####".format(url, ffilter))
	if ('/archiv' in url and not url.endswith('archiv?')) or ('/highlights' in url and not url.endswith('highlights?')):
		url = url+"?"
	if '/archiv' in url or '/highlights' in url:
		fullURL = url+ffilter
	else:
		fullURL = url
	content = makeREQUEST(fullURL)
	debug("(result_Archiv_Highlights_Ligen) no.2 ##### URL={0} ##### FFILTER={1} #####".format(url, ffilter))
	home = re.findall('<section class="container home-tile">(.*?)</section>', content, re.DOTALL)
	if home and not 'Leider gibt es keine Ergebnisse' in home[0]:
		for chtml in home:
			section = re.compile('<h2 class="section-title">(.+?)</h2>', re.DOTALL).findall(chtml)
			for title in section:
				if title != "":
					name = cleanTitle(title)
					if name == "Teams":
						addDir(name, fullURL, 'selection_Ligen_Teams', icon, ffilter=name)
					else:
						addDir(name, fullURL, 'Archiv_Highlights_Ligen_Videos', icon, ffilter=name)
	else:
		return xbmcgui.Dialog().notification(translation(30523), translation(30524), icon, 8000)
	xbmcplugin.endOfDirectory(pluginhandle)

def Archiv_Highlights_Ligen_Videos(url, ffilter=""):
	debug("(Archiv_Highlights_Ligen_Videos) no.1 ##### URL={0} ##### FFILTER={1} #####".format(url, ffilter))
	COMBINATION = []
	CHOICE = unquote_plus(ffilter)
	content = makeREQUEST(url)
	match = re.findall('<section class="container home-tile">(.*?)</section>', content, re.DOTALL)
	count = 0
	pos1 = 0
	for chtml in match:
		section = re.compile('class="section-title">(.+?)</h2>', re.DOTALL).findall(chtml)
		debug("(Archiv_Highlights_Ligen_Videos) no.2 ##### SECTION={0} ##### CHOICE={1} #####".format(section, CHOICE))
		for RUBRIK in section:
			correctRUBRIK = cleanTitle(RUBRIK)
			if correctRUBRIK == CHOICE:
				debug("(Archiv_Highlights_Ligen_Videos) no.3 ##### RUBRIK={0} ##### CHOICE={1} #####".format(RUBRIK, CHOICE))
				result = chtml[chtml.find('class="section-title">'+RUBRIK+'</h2>')+6:]
				result = result[:result.find('class="section-title">')]
				videos = re.compile('class="col-sm-4(.+?)</a>', re.DOTALL).findall(result)
				for video in videos:
					try:
						vidURL = re.compile('href="(.+?)" class=', re.DOTALL).findall(video)[0]
						if vidURL[:4] != "http":
							vidURL = baseURL+vidURL
						try:
							photo = re.compile(r'style="background-image.+?(?:\(|\")([^)"]+?)(?:\)|\")', re.DOTALL).findall(video)[0]
						except: photo = ""
						if photo != "" and photo[:4] != "http":
							photo = baseURL+photo
						if photo != "" and "?w=" in photo:
							photo = photo.split('?w=')[0]+"?w=1280"
						title = re.compile('class="caption">(.+?)<', re.DOTALL).findall(video)[0].replace('Highlights', '').replace('Zusammenfassung', '')
						title = cleanTitle(title)
						if title =="":
							continue
						relevance = re.compile('class="date">(.+?)<', re.DOTALL).findall(video)[0].strip()
						try:
							datetime_object = datetime.datetime.strptime(relevance, '%d.%m.%Y')
						except TypeError:
							datetime_object = datetime.datetime(*(time.strptime(relevance, '%d.%m.%Y')[0:6]))
						division = re.compile('class="caption league">(.+?)<', re.DOTALL).findall(video)[0]
						division = cleanTitle(division)
						COMBINATION.append([datetime_object, relevance, title, division, vidURL, photo])
					except:
						pos1 += 1
						failing("(Archiv_Highlights_Ligen_Videos) Fehler-Eintrag-01 : {0}".format(str(video)))
						if pos1 > 1 and count == 0:
							count += 1
							xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30522), icon, 8000)
		for datetime_object, relevance, title, division, vidURL, photo in sorted(COMBINATION, key=lambda item:item[0], reverse=True):
			name = relevance+" - "+title+"  ("+division+")"
			addLink(name, vidURL, "playVideo", photo)
	xbmcplugin.endOfDirectory(pluginhandle)

def Topclips_Categories(url, category=""):
	debug("(Topclips_Categories) ##### URL={0} #####".format(url))
	UN_Supported = ['übertragungen', 'Übertragungen']
	SPORTSNAME = unquote_plus(category)
	content = makeREQUEST(url)
	result = content[content.find('<ul class="nav">')+1:]
	result = result[:result.find('</ul>')]
	if '<li class="nav-item">' in result:
		part = result.split('<li class="nav-item">')
		for i in range(1, len(part), 1):
			element = part[i]
			title = re.compile('<a class="nav-link.+?">(.+?)</a>', re.DOTALL).findall(element)[0]
			name = cleanTitle(title)
			if name !="" and not any(x in name for x in UN_Supported):
				addDir(name, url, 'Topclips_Videos', icon, ffilter=name)
	else:
		return xbmcgui.Dialog().notification(translation(30525), (translation(30526).format(SPORTSNAME.upper())), icon, 8000)
	xbmcplugin.endOfDirectory(pluginhandle)

def Topclips_Videos(url, ffilter=""):
	debug("(Topclips_Videos) no.1 ##### URL={0} ##### FFILTER={1} #####".format(url, ffilter))
	COMBINATION = []
	sortedArray = []
	CHOICE = unquote_plus(ffilter)
	content = makeREQUEST(url)
	match = re.findall('<section class="container home-tile">(.*?)</section>', content, re.DOTALL)
	count = 0
	pos1 = 0
	for chtml in match:
		section = re.compile('class="section-title">(.+?)</h2>', re.DOTALL).findall(chtml)
		debug("(Topclips_Videos) no.2 ##### SECTION={0} ##### CHOICE={1} #####".format(section, CHOICE))
		for RUBRIK in section:
			correctRUBRIK = cleanTitle(RUBRIK)
			if correctRUBRIK == CHOICE:
				debug("(Topclips_Videos) no.3 ##### RUBRIK={0} ##### CHOICE={1} #####".format(RUBRIK, CHOICE))
				result = chtml[chtml.find('class="section-title">'+RUBRIK+'</h2>')+6:]
				result = result[:result.find('class="section-title">')]
				videos = re.compile('class="col-sm-4(.+?)</a>', re.DOTALL).findall(result)
				for video in videos:
					try:
						vidURL = re.compile('href="(.+?)" class=', re.DOTALL).findall(video)[0]
						if vidURL[:4] != "http":
							vidURL = baseURL+vidURL
						try:
							photo = re.compile(r'style="background-image.+?(?:\(|\")([^)"]+?)(?:\)|\")', re.DOTALL).findall(video)[0]
						except: photo = ""
						if photo != "" and photo[:4] != "http":
							photo = baseURL+photo
						if photo != "" and "?w=" in photo:
							photo = photo.split('?w=')[0]+"?w=1280"
						title = re.compile('class="caption">(.+?)<', re.DOTALL).findall(video)[0]
						title = cleanTitle(title)
						if title =="":
							continue
						relevance = re.compile('class="date">(.+?)<', re.DOTALL).findall(video)[0].strip()
						division = re.compile('class="caption league">(.+?)<', re.DOTALL).findall(video)[0]
						division = cleanTitle(division)
						if division != "":
							name = relevance+" - "+title+"  ("+division+")"
						elif division == "":
							name = relevance+" - "+title
						addLink(name, vidURL, "playVideo", photo)
					except:
						pos1 += 1
						failing("(Topclips_Videos) Fehler-Eintrag-01 : {0}".format(str(video)))
						if pos1 > 1 and count == 0:
							count += 1
							xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30522), icon, 8000)
	xbmcplugin.endOfDirectory(pluginhandle)

def Ligen_Overview(url):
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_TITLE)
	debug("(Ligen_Overview) ##### URL={0} #####".format(url))
	content = makeREQUEST(url)
	result = content[content.find('<section class="container home-tile league-selector">'):]
	result = result[:result.find('</ul>')]
	selection = re.findall('href="(.*?)">.+?<h4>(.*?)</h4>.+?<h3>(.*?)</h3>', result, re.DOTALL)
	for url2, title, counter in selection:
		if title != "":
			if url2[:4] != "http":
				url2 = baseURL+url2
			name = cleanTitle(title)
			number = re.compile('([0-9]+)', re.DOTALL).findall(counter)[0].strip()
			addDir(name+"  [COLOR chartreuse]("+number+")[/COLOR]", url2, 'selection_Ligen_Other', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def selection_Ligen_Other(url):
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_TITLE)
	debug("(selection_Ligen_Other) ##### URL={0} #####".format(url))
	content = makeREQUEST(url)
	result = content[content.find('<ul class="slider-leagues">'):]
	result = result[:result.find('</ul>')]
	match = re.findall('class="league-item">(.*?)</li>', result, re.DOTALL)
	count = 0
	pos1 = 0
	for league in match:
		try:
			url2 = re.compile('href="(.+?)">', re.DOTALL).findall(league)[0]
			if url2[:4] != "http":
				url2 = baseURL+url2
			title = re.compile('<h4>(.+?)<', re.DOTALL).findall(league)[0]
			name = cleanTitle(title)
			if name !="":
				addDir(name, url2, 'result_Archiv_Highlights_Ligen', icon)
		except:
			pos1 += 1
			failing("(selection_Ligen_Other) Fehler-Eintrag-01 : {0}".format(str(league)))
			if pos1 > 1 and count == 0:
				count += 1
				xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30522), icon, 8000)
	xbmcplugin.endOfDirectory(pluginhandle)

def selection_Ligen_Teams(url, ffilter=""):
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_TITLE)
	debug("(selection_Ligen_Teams) ##### URL={0} ##### FFILTER={1} #####".format(url, ffilter))
	rubrik = unquote_plus(ffilter)
	content = makeREQUEST(url)
	result = content[content.find('class="teams-grid">'):]
	result = result[:result.find('</ul>')]
	match = re.findall('<li>(.*?)</li>', result, re.DOTALL)
	count = 0
	pos1 = 0
	for team in match:
		try:
			url2 = re.compile('href="(.+?)">', re.DOTALL).findall(team)[0]
			if url2[:4] != "http":
				url2 = baseURL+url2
			try:
				photo = re.compile('<img.+?src="([^"]+?)"', re.DOTALL).findall(team)[0]
			except: photo = ""
			if photo != "" and photo[:4] != "http":
				photo = baseURL+photo
			if photo != "" and "?w=" in photo:
				photo = photo.split('?w=')[0]+"?w=300"
			title = re.compile('<h4>(.+?)<', re.DOTALL).findall(team)[0]
			name = cleanTitle(title)
			if name !="":
				addDir(name, url2, 'result_Archiv_Highlights_Ligen', photo, ffilter=rubrik, background="KEIN HINTERGRUND")
		except:
			pos1 += 1
			failing("(selection_Ligen_Teams) Fehler-Eintrag-01 : {0}".format(str(team)))
			if pos1 > 1 and count == 0:
				count += 1
				xbmcgui.Dialog().notification((translation(30521).format('DISPLAY')), translation(30522), icon, 8000)
	xbmcplugin.endOfDirectory(pluginhandle)

def playVideo(url):
	debug("(playVideo) no.1 ##### URL={0} #####".format(url))
	fileURL = False
	testURL = False
	content = getUrl(url)
	try:
		stream = re.compile('file: "(https?://[^"]+?)"', re.DOTALL|re.UNICODE).findall(content)[0].replace('\n', '')
		fileURL = True
	except: 
		failing("(playVideo) ##### Abspielen des Streams NICHT möglich ##### URL : {0} #####\n   ########## KEINEN Stream-Eintrag auf der Webseite von *sporttotal.tv* gefunden !!! ##########".format(url))
		xbmcgui.Dialog().notification((translation(30521).format('URL 1')), translation(30527), icon, 8000)
		return
	standardSTREAM = re.compile(r'(?:/[^/]+?\.mp4|/[^/]+?\.m3u8)', re.DOTALL).findall(stream)[0]
	correctSTREAM = quote(standardSTREAM)
	debug("(playVideo) no.2 ##### standardSTREAM={0} ##### correctSTREAM={1} #####".format(standardSTREAM, correctSTREAM))
	finalURL = stream.replace(standardSTREAM, correctSTREAM)
	try:
		code = urlopen(finalURL).getcode()
		if str(code) == "200":
			testURL = True
	except: pass
	if fileURL and testURL:
		log("(playVideo) StreamURL : {0}".format(finalURL))
		listitem = xbmcgui.ListItem(path=finalURL)
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	else:
		failing("(playVideo) ##### Abspielen des Streams NICHT möglich ##### URL : {0} #####\n   ########## Die Stream-Url auf der Webseite von *sporttotal.tv* ist OFFLINE !!! ##########".format(finalURL))
		xbmcgui.Dialog().notification((translation(30521).format('URL 2')), translation(30528), icon, 8000)

def cleanTitle(title):
	title = py2_enc(title)
	title = title.replace('&#196;', 'Ä').replace('&#214;', 'Ö').replace('&#220;', 'Ü').replace('&#228;', 'ä').replace('&#246;', 'ö').replace('&#252;', 'ü').replace('&#223;', 'ß').replace('&#160;', ' ')
	title = title.replace('&#192;', 'À').replace('&#193;', 'Á').replace('&#194;', 'Â').replace('&#195;', 'Ã').replace('&#197;', 'Å').replace('&#199;', 'Ç').replace('&#200;', 'È').replace('&#201;', 'É').replace('&#202;', 'Ê')
	title = title.replace('&#203;', 'Ë').replace('&#204;', 'Ì').replace('&#205;', 'Í').replace('&#206;', 'Î').replace('&#207;', 'Ï').replace('&#209;', 'Ñ').replace('&#210;', 'Ò').replace('&#211;', 'Ó').replace('&#212;', 'Ô')
	title = title.replace('&#213;', 'Õ').replace('&#215;', '×').replace('&#216;', 'Ø').replace('&#217;', 'Ù').replace('&#218;', 'Ú').replace('&#219;', 'Û').replace('&#221;', 'Ý').replace('&#222;', 'Þ').replace('&#224;', 'à')
	title = title.replace('&#225;', 'á').replace('&#226;', 'â').replace('&#227;', 'ã').replace('&#229;', 'å').replace('&#231;', 'ç').replace('&#232;', 'è').replace('&#233;', 'é').replace('&#234;', 'ê').replace('&#235;', 'ë')
	title = title.replace('&#236;', 'ì').replace('&#237;', 'í').replace('&#238;', 'î').replace('&#239;', 'ï').replace('&#240;', 'ð').replace('&#241;', 'ñ').replace('&#242;', 'ò').replace('&#243;', 'ó').replace('&#244;', 'ô')
	title = title.replace('&#245;', 'õ').replace('&#247;', '÷').replace('&#248;', 'ø').replace('&#249;', 'ù').replace('&#250;', 'ú').replace('&#251;', 'û').replace('&#253;', 'ý').replace('&#254;', 'þ').replace('&#255;', 'ÿ')
	title = title.replace('&#352;', 'Š').replace('&#353;', 'š').replace('&#376;', 'Ÿ').replace('&#402;', 'ƒ')
	title = title.replace('&#8211;', '–').replace('&#8212;', '—').replace('&#8226;', '•').replace('&#8230;', '…').replace('&#8240;', '‰').replace('&#8364;', '€').replace('&#8482;', '™').replace('&#169;', '©').replace('&#174;', '®')
	title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö").replace('&quot;', '"').replace('&szlig;', 'ß').replace('&ndash;', '-')
	title = title.replace("HIGHLIGHTS", "").replace("Highlights", "").replace("HIGHLIGHT", "").replace("Highlight", "")
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

def addDir(name, url, mode, iconimage, desc="", ffilter="", category="", background=""):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&ffilter="+quote_plus(ffilter)+"&category="+quote_plus(category)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	if iconimage != icon and background != "KEIN HINTERGRUND":
		liz.setArt({'fanart': iconimage})
	else:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  
def addLink(name, url, mode, iconimage, desc="", duration="", background=""):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration, 'mediatype': 'video'})
	if iconimage != icon and background != "KEIN HINTERGRUND":
		liz.setArt({'fanart': iconimage})
	else:
		liz.setArt({'fanart': defaultFanart})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

params = parameters_string_to_dict(sys.argv[2])
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
iconimage = unquote_plus(params.get('iconimage', ''))
ffilter = unquote_plus(params.get('ffilter', ''))
category = unquote_plus(params.get('category', ''))
background = unquote_plus(params.get('background', ''))
referer = unquote_plus(params.get('referer', ''))

if mode == 'aSettings':
	addon.openSettings()
elif mode == 'clearCache':
	clearCache()
elif mode == 'Allsportarts_Overview':
	Allsportarts_Overview(ffilter)
elif mode == 'Livegames_Videos':
	Livegames_Videos(url, category)
elif mode == 'list_Archiv_Highlights':
	list_Archiv_Highlights(url, ffilter, category)
elif mode == 'selection_Archiv_Highlights':
	selection_Archiv_Highlights(url, ffilter)
elif mode == 'result_Archiv_Highlights_Ligen':
	result_Archiv_Highlights_Ligen(url, ffilter)
elif mode == 'Archiv_Highlights_Ligen_Videos':
	Archiv_Highlights_Ligen_Videos(url, ffilter)
elif mode == 'Topclips_Categories':
	Topclips_Categories(url, category)
elif mode == 'Topclips_Videos':
	Topclips_Videos(url, ffilter)
elif mode == 'Ligen_Overview':
	Ligen_Overview(url)
elif mode == 'selection_Ligen_Other':
	selection_Ligen_Other(url)
elif mode == 'selection_Ligen_Teams':
	selection_Ligen_Teams(url, ffilter)
elif mode == 'playVideo':
	playVideo(url)
else:
	index()