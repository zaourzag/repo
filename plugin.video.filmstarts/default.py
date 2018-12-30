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
import base64
from datetime import datetime, timedelta
import io
import gzip
import ssl

global debuging
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
#socket.setdefaulttimeout(40)
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath    = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
temp           = xbmc.translatePath(os.path.join(dataPath, 'temp', '')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg')
icon = os.path.join(addonPath, 'icon.png')
pic = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
NEXT_BEFORE_PAGE = addon.getSetting("NEXT_BEFORE") == 'true'
enableDebug = addon.getSetting("enableDebug") == 'true'
Zertifikat = addon.getSetting("inetCert")
baseURL="http://www.filmstarts.de"

xbmcplugin.setContent(pluginhandle, 'movies')

xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)

if Zertifikat == "false":
	try:
		_create_unverified_https_context = ssl._create_unverified_context
	except AttributeError:
		pass
	else:
		ssl._create_default_https_context = _create_unverified_https_context

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
	debug("Get Url : "+url)
	for cook in cj:
		debug("Cookie : "+str(cook))
	opener = build_opener(HTTPCookieProcessor(cj))
	try:
		if header:
			opener.addheaders = header
		else:
			opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36')]
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
	cj.save(cookie, ignore_discard=True, ignore_expires=True)
	return content

def index():
	addDir(translation(30601), "", 'trailer', icon)
	addDir(translation(30602), "", 'kino', icon)
	addDir(translation(30603), "", 'series', icon)
	addDir(translation(30604), "", 'news', icon)
	addDir(translation(30608), "", 'aSettings', pic+'settings.png')
	xbmcplugin.endOfDirectory(pluginhandle)

def trailer():
	addDir(translation(30609), baseURL+"/trailer/beliebteste.html", 'listTrailer', icon)
	addDir(translation(30610), baseURL+"/trailer/imkino/", 'listTrailer', icon)
	addDir(translation(30611), baseURL+"/trailer/bald/", 'listTrailer', icon)
	addDir(translation(30612), baseURL+"/trailer/neu/", 'listTrailer', icon)
	addDir(translation(30613), baseURL+"/trailer/archiv/", 'filtertrailer', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def kino():
	addDir(translation(30614), baseURL+"/filme-imkino/vorpremiere/", 'listKino_small', icon)
	addDir(translation(30615), baseURL+"/filme-imkino/kinostart/", 'listKino_big', icon, datum="N")
	addDir(translation(30616), baseURL+"/filme-imkino/neu/", 'listKino_big', icon, datum="J")
	addDir(translation(30617), baseURL+"/filme-imkino/besten-filme/user-wertung/", 'listKino_big', icon, datum="N")
	#addDir(translation(30618), baseURL+"/filme-imkino/kinderfilme/", 'listKino_small', icon)
	addDir(translation(30619), baseURL+"/filme-vorschau/de/", 'selectionWeek', icon)
	addDir(translation(30620), baseURL+"/filme/besten/user-wertung/", 'filterkino', icon)
	addDir(translation(30621), baseURL+"/filme/schlechtesten/user-wertung/", 'filterkino', icon)
	addDir(translation(30622), baseURL+"/filme/kinderfilme/", 'filterkino', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def series():
	addDir(translation(30623), baseURL+"/serien/top/", 'listSeries_big', icon, datum="N")
	addDir(translation(30624), baseURL+"/serien/beste/", 'filterserien', icon)
	addDir(translation(30625), baseURL+"/serien/top/populaerste/", 'listSeries_small', icon)
	addDir(translation(30626), baseURL+"/serien/kommende-staffeln/meisterwartete/", 'listSeries_small', icon)
	addDir(translation(30627), baseURL+"/serien/kommende-staffeln/deutschland/", 'listSeries_small', icon)
	addDir(translation(30628), baseURL+"/serien/kommende-staffeln/demnaechst/deutschland/", 'listSeries_small', icon)
	addDir(translation(30629), baseURL+"/serien/neue/", 'listSeries_big', icon, datum="N")
	addDir(translation(30630), baseURL+"/serien/videos/neueste/", 'listSpecial_Series_Trailer', icon)
	addDir(translation(30631), baseURL+"/serien-archiv/", 'filterserien', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def news():
	addDir(translation(30632), baseURL+"/videos/shows/funf-sterne/", 'listNews', icon)
	addDir(translation(30633), baseURL+"/videos/shows/filmstarts-fehlerteufel/", 'listNews', icon)
	addDir(translation(30634), baseURL+"/trailer/interviews/", 'listNews', icon)
	addDir(translation(30635), baseURL+"/videos/shows/meine-lieblings-filmszene/", 'listNews', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def filtertrailer(url):
	debug_MS("(filtertrailer) -------------------------------------------------- START = filtertrailer --------------------------------------------------")
	debug_MS("(filtertrailer) ##### URL={0} #####".format(url))
	if not "genre-" in url:
		addDir(translation(30661), url, 'selectionCategories', icon, type="filtertrailer", CAT_text="Alle Genres")
	if not "sprache-" in url:
		addDir(translation(30662), url, 'selectionCategories', icon, type="filtertrailer", CAT_text="Alle Sprachen")
	if not "format-" in url:
		addDir(translation(30663), url, 'selectionCategories', icon, type="filtertrailer", CAT_text="Alle Formate")
	addDir(translation(30670), url, 'listSpecial_Series_Trailer', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def filterkino(url):
	debug_MS("(filterkino) -------------------------------------------------- START = filterkino --------------------------------------------------")
	debug_MS("(filterkino) ##### URL={0} #####".format(url))
	if not "genre-" in url:
		addDir(translation(30661), url, 'selectionCategories', icon, type="filterkino", CAT_text="Alle Genres")
	if not "jahrzehnt" in url:
		addDir(translation(30664), url, 'selectionCategories', icon, type="filterkino", CAT_text="Alle Jahre")
	if not "produktionsland-" in url:
		addDir(translation(30665), url, 'selectionCategories', icon, type="filterkino", CAT_text="Alle Länder")
	addDir(translation(30670), url, 'listKino_small', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def filterserien(url):
	debug_MS("(filterserien) -------------------------------------------------- START = filterserien --------------------------------------------------")
	debug_MS("(filterserien) ##### URL={0} #####".format(url))
	if not "genre-" in url:
		if "serien-archiv" in url: CAT_text = "Nach Genre"
		else: CAT_text="Alle Genres"
		addDir(translation(30661), url, 'selectionCategories', icon, type="filterserien", CAT_text=CAT_text)
	if not "jahrzehnt" in url:
		if "serien-archiv" in url: CAT_text = "Nach Produktionsjahr"
		else: CAT_text="Alle Jahre"
		addDir(translation(30664), url, 'selectionCategories', icon, type="filterserien", CAT_text=CAT_text)
	if not "produktionsland-" in url:
		if "serien-archiv" in url: CAT_text = "Nach Land"
		else: CAT_text="Alle Länder"
		addDir(translation(30665), url, 'selectionCategories', icon, type="filterserien", CAT_text=CAT_text)
	if "serien-archiv" in url:
		addDir(translation(30670), url, 'listSeries_big', icon, datum="N")
	else:
		addDir(translation(30670), url, 'listSeries_small', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def selectionCategories(url, type="", CAT_text=""):
	debug_MS("(selectionCategories) -------------------------------------------------- START = selectionCategories --------------------------------------------------")
	debug_MS("(selectionCategories) ##### URL={0} ##### TYPE={1} ##### TEXT={2} #####".format(url, type, CAT_text))
	content = getUrl(url)
	if "serien-archiv" in url:
		result = content[content.find('data-name="'+CAT_text+'"')+1:]
		result = result[:result.find('</ul>')]
		part = result.split('class="filter-entity-item"')
	else:
		result = content[content.find(CAT_text+'</span>')+1:]
		result = result[:result.find('</li></ul>')]
		part = result.split('</li><li')
	for i in range(1,len(part),1):  
		element=part[i]
		element = element.replace("<strong>", "").replace("</strong>", "")
		try:
			if "serien-archiv" in url:
				try: number = re.compile('<span class=["\']light["\']>\(([^<]+?)\)</span>', re.DOTALL).findall(element)[0].strip() 
				except: number = ""
				try:
					matchUN = re.compile('href=["\']([^"]+)["\'] title=.+?["\']>([^<]+?)</a>', re.DOTALL).findall(element)
					link = matchUN[0][0]
					name = matchUN[0][1].strip()
				except:
					matchUN = re.compile('class=["\']([^ "]+) item-content["\'] title=.+?["\']>([^<]+?)</span>', re.DOTALL).findall(element)
					oldURL = matchUN[0][0]
					link = oldURL.replace("ACr", "")
					link = base64.b64decode(link).decode("utf-8", "ignore")
					name = matchUN[0][1].strip()
				if number != "": name += "   ("+str(number)+")"
				addDir(name, baseURL+link, type, icon)
			else:
				try: number = re.compile('<span class=["\']lighten["\']>\(([^<]+?)\)</span>', re.DOTALL).findall(element)[0].strip() 
				except: number = ""
				try:
					matchUN = re.compile('<span class=["\']acLnk ([^"]+)">([^<]+?)</span>', re.DOTALL).findall(element)  
					link = decodeURL(matchUN[0][0])
					name = matchUN[0][1].strip()
				except:
					matchUN = re.compile('<a href=["\']([^"]+)["\']>([^<]+)</a>', re.DOTALL).findall(element)   
					link = matchUN[0][0]
					name = matchUN[0][1].strip()
				if number != "": name += "   ("+str(number)+")"
				addDir(name, baseURL+link, type, icon)
			debug_MS("(selectionCategories) Name : "+name)
			debug_MS("(selectionCategories) Link : "+baseURL+link)
		except:
			failing("..... exception .....")
			failing("(selectionCategories) Fehler-Eintrag : {0} #####".format(str(element)))
	xbmcplugin.endOfDirectory(pluginhandle)

def selectionWeek(url):
	debug_MS("(selectionWeek) -------------------------------------------------- START = selectionWeek --------------------------------------------------")
	debug_MS("(selectionWeek) ##### URL={0} #####".format(url))
	content=getUrl(url)
	result = content[content.find('<div class="pagination pagination-select">')+1:]
	result = result[:result.find('<span class="txt">Nächste</span><i class="icon icon-right icon-arrow-right-a">')]
	part = result.split('eventCategory":"release_calendar_page"')
	for i in range(1,len(part),1):
		element=part[i]
		try:
			datum = re.compile('eventLabel["\']:["\'](.+?)["\'],', re.DOTALL).findall(element)[0]
			title = re.compile('value=["\']ACr.*?(?:["\'] >|["\'] selected>)([^<]+)</option>', re.DOTALL).findall(element)[0]
			name = cleanTitle(title)
			debug_MS("(selectionWeek) Name : "+name)
			debug_MS("(selectionWeek) Datum : "+datum)
			addDir(name, baseURL+"/filme-vorschau/de/week-", 'listKino_big', icon, datum=datum)
		except:
			failing("..... exception .....")
			failing("(selectionWeek) Fehler-Eintrag : {0} #####".format(str(element)))
	xbmcplugin.endOfDirectory(pluginhandle)

def listTrailer(url, page=1):
	debug_MS("(listTrailer) -------------------------------------------------- START = listTrailer --------------------------------------------------")
	page = int(page)
	if page > 1:
		PGurl = url+"?page="+str(page)
	else:
		PGurl = url
	debug_MS("(listTrailer) ##### URL={0} ##### PAGE={1} #####".format(PGurl, str(page)))
	content = getUrl(PGurl)
	selection = re.findall('<div class="card card-video-traile(.+?)<span class="thumbnail-count">', content, re.DOTALL)
	for chtml in selection:
		try:
			image = re.compile(r'src=["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.DOTALL|re.IGNORECASE).findall(chtml)[0]
			photo = enlargeIMG(image)
			matchUN = re.compile('<a href=["\']([^"]+)["\'] class=["\']layer-link["\']>([^<]+)</a>', re.DOTALL).findall(chtml)
			link = matchUN[0][0]
			title = matchUN[0][1]
			name = cleanTitle(title)
			debug_MS("(listTrailer) Name : "+name)
			debug_MS("(listTrailer) Link : "+baseURL+link)
			debug_MS("(listTrailer) Icon : "+photo)
			addLink(name, baseURL+link, 'playVideo', photo, extraURL=url)
		except:
			failing("..... exception .....")
			failing("(listTrailer) Fehler-Eintrag : {0} #####".format(str(chtml)))
	if '<span class="txt">Nächste</span><i class="icon icon-right icon-arrow-right-a">' in content:
		addDir(translation(30685), url, 'listTrailer', pic+"nextpage.png", page=page+1)
	xbmcplugin.endOfDirectory(pluginhandle)

def listSpecial_Series_Trailer(url, page=1):
	debug_MS("(listTrailer) -------------------------------------------------- START = listSpecial_Series_Trailer --------------------------------------------------")
	page = int(page)
	if page > 1:
		PGurl = url+"?page="+str(page)
	else:
		PGurl = url
	debug_MS("(listSpecial_Series_Trailer) ##### URL={0} ##### PAGE={1} #####".format(PGurl, str(page)))
	content = getUrl(PGurl)
	if "/serien" in PGurl:
		result = content[content.find('<div class="tabs_main">')+1:]
		result = result[:result.find('<i class="icon-arrow-left">')]
		part = result.split('<article data-block')
	else:
		if 'fr">Nächste<i class="icon-arrow-right">' in content:
			result = content[:content.find('<i class="icon-arrow-left">')]
		else:
			result = content[:content.find("<div id='ad-rectangle1-outer'>")]
		part = result.split('<article class="media-meta')
	for i in range(1,len(part),1): 
		element = part[i]
		element = element.replace("<strong>", "").replace("</strong>", "")
		if "<a href=" in element:
			try:
				try:
					image = re.compile(r'src=["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.DOTALL|re.IGNORECASE).findall(element)[0]
				except:
					image = re.compile(r'["\']src["\']:["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.DOTALL|re.IGNORECASE).findall(element)[0]
				photo = enlargeIMG(image)
				try:
					RuTi = re.compile('class=["\']icon icon-timer["\']>(.+?)</time>', re.DOTALL).findall(element)[0].replace("</i>", "").strip()
					if ":" in RuTi:
						running = re.compile('([0-9]+):([0-9]+)', re.DOTALL).findall(RuTi)
						duration = int(running[0][0])*60+int(running[0][1])
					elif not ":" in RuTi:
						duration = int(RuTi)
				except: duration =""
				match = re.compile('<a href=["\']([^"]+?)["\']>([^<]+)</a>', re.DOTALL).findall(element)
				link = match[0][0]
				name = match[0][1]
				name = cleanTitle(name)
				debug_MS("(listSpecial_Series_Trailer) Name : "+name)
				debug_MS("(listSpecial_Series_Trailer) Link : "+baseURL+link)
				debug_MS("(listSpecial_Series_Trailer) Icon : "+photo)
				if link !="" and not "En savoir plus" in name:
					addLink(name, baseURL+link, 'playVideo', photo, duration=duration, extraURL=url)
			except:
				failing("..... exception .....")
				failing("(listSpecial_Series_Trailer) Fehler-Eintrag : {0} #####".format(str(element)))
	if 'fr">Nächste<i class="icon-arrow-right">' in content:
		addDir(translation(30685), url, 'listSpecial_Series_Trailer', pic+"nextpage.png", page=page+1)
	xbmcplugin.endOfDirectory(pluginhandle)

def listKino_big(url, page=1, datum="N", position=0):
	debug_MS("(listKino_small) -------------------------------------------------- START = listKino_big --------------------------------------------------")
	page = int(page)
	FOUND = False
	NEPVurl = url
	if page > 1:
		PGurl = url+"?page="+str(page)
	else:
		PGurl = url
	if datum !="" and datum !="J" and datum !="N":
		url = url+datum+"/"
		PGurl = PGurl+datum+"/"
	debug_MS("(listKino_big) ##### URL={0} ##### PAGE={1} #####".format(PGurl, str(page)))
	content = getUrl(PGurl)
	if int(position) == 0:
		try:
			position = re.compile('<a class=["\']button button-md item["\'] href=["\'].+?page=[0-9]+["\']>([0-9]+)</a></div></nav>', re.DOTALL).findall(content)[0]
			debug_MS("(listKino_big) *FOUND-1* Pages-Maximum : {0}".format(str(position)))
		except:
			try:
				position = re.compile('<span class=["\'].*?button-md item["\']>([0-9]+)</span></div></nav>', re.DOTALL).findall(content)[0]
				debug_MS("(listKino_big) *FOUND-2* Pages-Maximum : {0}".format(str(position)))
			except: pass
	result = content[content.find('class="card card-entity card-entity-list cf"')+1:]
	result = result[:result.find('<div class="rc-content">')]
	part = result.split('<figure class="thumbnail ">')
	for i in range(1,len(part),1):
		element=part[i]
		try:
			matchUN = re.compile('class=["\']([^ "]+) thumbnail-container thumbnail-link["\'] title=["\'](.+?)["\']>', re.DOTALL).findall(element)
			oldURL = matchUN[0][0].replace("ACr", "")
			newURL = base64.b64decode(oldURL).decode("utf-8", "ignore")
			title = matchUN[0][1]
			name = cleanTitle(title)
			image = re.compile(r'src=["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.DOTALL|re.IGNORECASE).findall(element)[0]
			photo = enlargeIMG(image)
			if "serien-archiv" in PGurl:
				try: movieDATE = re.compile('<div class=["\']meta-body-item meta-body-info["\']>([^<]+?)<span class=["\']spacer["\']>/</span>', re.DOTALL).findall(element)[0]
				except: movieDATE =""
			else:
				try: movieDATE = re.compile('<span class=["\']date["\']>.*?([a-zA-Z]+ [0-9]+)</span>', re.DOTALL).findall(element)[0]
				except: movieDATE =""
			if movieDATE != "" and "serien-archiv" in PGurl:
				name = name+"   ("+str(movieDATE.replace('\n', '').replace(' - ', '~').replace('läuft seit', 'ab').strip())+")"
			elif movieDATE != "" and "besten-filme/user-wertung" in PGurl:
				newDATE = cleanMonth(movieDATE.lower())
				name = name+"   ("+str(newDATE)+")"
			try: # Grab - Genres
				result_1 = re.compile('<span class=["\']spacer["\']>/</span>.*?<span class=["\']spacer["\']>/</span>(.+?)</div>', re.DOTALL).findall(element)[0]
				matchG = re.compile('<span class=["\']ACr.*?["\']>(.+?)</span>', re.DOTALL).findall(result_1)
				genres = []
				for gNames in matchG:
					genres.append(gNames.strip())
				gGenre =", ".join(genres)
			except: gGenre =""
			try: # Grab - Directors
				result_2 = element[element.find('class="meta-body-item meta-body-direction light">')+1:]
				result_2 = result_2[:result_2.find('</div>')]
				matchD = re.compile('class=["\'].*?["\']>([^<]+?)</', re.DOTALL).findall(result_2)
				directors = []
				for dNames in matchD:
					directors.append(dNames.strip())
				dDirector =", ".join(directors)
			except: dDirector =""
			try: # Grab - Plot
				desc = re.compile('<div class=["\']synopsis["\']>(.+?)</div>', re.DOTALL).findall(element)[0]
				plot = re.sub(r'\<.*?\>', '', desc)
				plot = cleanTitle(plot)
			except: plot=""
			try: # Grab - Rating
				result_3 = element[element.find('User-Wertung')+1:]
				rRating = re.compile('class=["\']stareval-note["\']>([^<]+?)</span></div>', re.DOTALL).findall(result_3)[0].strip().replace(',', '.')
			except:
				try:
					result_3 = element[element.find('Pressekritiken')+1:]
					rRating = re.compile('class=["\']stareval-note["\']>([^<]+?)</span></div>', re.DOTALL).findall(result_3)[0].strip().replace(',', '.')
				except: rRating =""
			video = re.compile('<div class="buttons-holder["\']>(.+?)</div>', re.DOTALL).findall(element)
			debug_MS("(listKino_big) Name : "+name)
			debug_MS("(listKino_big) Link : "+baseURL+newURL)
			debug_MS("(listKino_big) Icon : "+photo)
			debug_MS("(listKino_big) Regie : "+dDirector)
			debug_MS("(listKino_big) Genre : "+gGenre)
			if ("Trailer" in video[0] or "Teaser" in video[0]) and not 'button btn-disabled' in element:
				FOUND = True
				addLink(name, baseURL+newURL, 'playVideo', photo, plot, gGenre, dDirector, rRating, extraURL=url)
			else:
				FOUND = True
				addDir(name+translation(30701), "", 'listKino_big', photo, plot, gGenre, dDirector, rRating)
		except:
			failing("..... exception .....")
			failing("(listKino_big) Fehler-Eintrag : {0} #####".format(str(element)))
	if not FOUND:
		return xbmcgui.Dialog().notification(translation(30523), translation(30524), icon, 8000)
	if NEXT_BEFORE_PAGE and datum !="" and datum !="J" and datum !="N":
		try:
			Start = datetime.strptime(datum, "%Y-%m-%d")
		except TypeError:
			Start = datetime(*(time.strptime(datum, "%Y-%m-%d")[0:6]))
		Nextweek = Start + timedelta(days=7)
		Beforweek = Start - timedelta(days=7)
		nx = Nextweek.strftime("%Y-%m-%d")
		bx = Beforweek.strftime("%Y-%m-%d")
		next = Nextweek.strftime("%d.%m.%Y")
		before = Beforweek.strftime("%d.%m.%Y")
		addDir((translation(30691).format(str(next))), NEPVurl, 'listKino_big', icon, datum=nx)
		addDir((translation(30692).format(str(before))), NEPVurl, 'listKino_big', icon, datum=bx)
		addDir(translation(30693), "", 'listKino_big', pic+"attention.png")
	if int(position) > page and datum =="N":
		addDir(translation(30685), NEPVurl, 'listKino_big', pic+"nextpage.png", page=page+1, datum=datum, position=position)
	xbmcplugin.endOfDirectory(pluginhandle)

def listKino_small(url, page=1):
	debug_MS("(listKino_small) -------------------------------------------------- START = listKino_small --------------------------------------------------")
	page = int(page)
	FOUND = False
	if page > 1:
		PGurl = url+"?page="+str(page)
	else:
		PGurl = url
	debug_MS("(listKino_small) ##### URL={0} ##### PAGE={1} #####".format(PGurl, str(page)))
	content = getUrl(PGurl)
	part = content.split('<div class="data_box">')
	for i in range(1,len(part),1):
		element = part[i]
		try:
			try:
				newURL = re.compile('button btn-primary ["\'] href=["\']([^"]+?)["\']', re.DOTALL).findall(element)[0]
			except:
				try:
					matchU = re.compile('class=["\']acLnk ([^ ]+?) button btn-primary', re.DOTALL).findall(element)[0]
					newURL = decodeURL(matchU)
				except: newURL =""
			image = re.compile(r'src=["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.DOTALL|re.IGNORECASE).findall(element)[0]
			photo = enlargeIMG(image)
			title = re.compile('alt=["\'](.+?)["\'\" \' ]\s+title=', re.DOTALL).findall(element)[0]
			name = cleanTitle(title)
			try:
				movieDATE = re.compile('<span class=["\']film_info lighten fl["\']>Starttermin(.+?)</div>', re.DOTALL).findall(element)[0]
				newDATE = re.sub(r'\<.*?\>', '', movieDATE)
			except: newDATE =""
			if newDATE != "" and not "unbekannt" in newDATE.lower():
				name = name+"   ("+newDATE.replace('\n', '').replace('.', '-').strip()[0:10]+")"
			try: # Grab - Directors
				result_1 = element[element.find('<span class="film_info lighten fl">Von </span>')+1:]
				result_1 = result_1[:result_1.find('</div>')]
				matchD = re.compile(r'(?:<span title=|<a title=)["\'](.+?)["\'] (?:class=|href=)', re.DOTALL).findall(result_1)
				directors = []
				for dNames in matchD:
					directors.append(dNames.strip())
				dDirector =", ".join(directors)
			except: dDirector =""
			try: # Grab - Genres
				result_2 = element[element.find('<span class="film_info lighten fl">Genre</span>')+1:]
				result_2 = result_2[:result_2.find('</div>')]
				matchG = re.compile('<span itemprop=["\']genre["\']>([^<]+?)</span>', re.DOTALL).findall(result_2)
				genres = []
				for gNames in matchG:
					genres.append(gNames.strip())
				gGenre =", ".join(genres)
			except: gGenre =""
			try: # Grab - Plot
				desc = re.compile("<p[^>]*>([^<]+)<", re.DOTALL).findall(element)[0]
				plot = desc.replace('&nbsp;', '')
				plot = cleanTitle(plot)
			except: plot=""
			try: # Grab - Rating
				result_3 = element[element.find('User-Wertung')+1:]
				result_3 = result_3[:result_3.find('</TrueTemplate>')]
				rRating = re.compile('<span class=["\']note["\']>([^<]+?)</span></span>', re.DOTALL).findall(result_3)[0].strip().replace(',', '.')
			except:
				try:
					result_3 = element[element.find('Pressekritiken')+1:]
					result_3 = result_3[:result_3.find('User-Wertung')]
					rRating = re.compile('<span class=["\']note["\']>([^<]+?)</span></span>', re.DOTALL).findall(result_3)[0].strip().replace(',', '.')
				except: rRating=""
			debug_MS("(listKino_small) Name : "+name)
			debug_MS("(listKino_small) Link : "+baseURL+newURL)
			debug_MS("(listKino_small) Icon : "+photo)
			debug_MS("(listKino_small) Regie : "+dDirector)
			debug_MS("(listKino_small) Genre : "+gGenre)
			if newURL !="" and not 'button btn-disabled' in element:
				FOUND = True
				addLink(name, baseURL+newURL, 'playVideo', photo, plot, gGenre, dDirector, rRating, extraURL=url)
			else:
				FOUND = True
				addDir(name+translation(30701), "", 'listKino_small', photo, plot, gGenre, dDirector, rRating)
		except:
			failing("..... exception .....")
			failing("(listKino_small) Fehler-Eintrag : {0} #####".format(str(element)))
	if not FOUND:
		return xbmcgui.Dialog().notification(translation(30523), translation(30524), icon, 8000)
	if 'fr">Nächste<i class="icon-arrow-right">' in content:  
		addDir(translation(30685), url, 'listKino_small', pic+"nextpage.png", page=page+1)
	xbmcplugin.endOfDirectory(pluginhandle)

def listSeries_small(url, page=1):
	debug_MS("(listSeries_small) -------------------------------------------------- START = listSeries_small --------------------------------------------------")
	page = int(page)
	FOUND = False
	if page > 1:
		PGurl = url+"?page="+str(page)
	else:
		PGurl = url
	debug_MS("(listSeries_small) ##### URL={0} ##### PAGE={1} #####".format(PGurl, str(page)))
	content = getUrl(PGurl)
	part = content.split('<div class="data_box">')
	for i in range(1,len(part),1):
		element = part[i]
		try:
			try:
				newURL = re.compile('button btn-primary ["\'] href=["\']([^"]+?)["\']', re.DOTALL).findall(element)[0]
			except:
				try:
					matchU = re.compile('class=["\']acLnk ([^ ]+?) button btn-primary', re.DOTALL).findall(element)[0]
					newURL = decodeURL(matchU)
				except: newURL =""
			image = re.compile(r'src=["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.DOTALL|re.IGNORECASE).findall(element)[0]
			photo = enlargeIMG(image)
			title =re.compile('<h2 class=["\']tt_18 d_inlin[^>]*>(.+?)</h2>', re.DOTALL).findall(element)[0]
			name = re.sub(r'\<.*?\>', '', title)
			name = cleanTitle(name)
			try:
				movieDATE = re.compile('<span class=["\']lighten(?:\">|\'>)\s+Produktionszeitraum(.+?)</tr>', re.DOTALL).findall(element)[0]
				newDATE = re.sub(r'\<.*?\>', '', movieDATE)
			except: newDATE =""
			if newDATE != "" and not "unbekannt" in newDATE:
				name = name+'   ('+newDATE.replace('\n', '').replace(' ', '').replace('-', '~').strip()+')'
			try: # Grab - Directors
				result_1 = element[element.find('<span class="lighten">mit</span>')+1:]
				result_1 = result_1[:result_1.find('</tr>')]
				matchD = re.compile(r'(?:<span title=|<a title=)["\'](.+?)["\'] (?:class=|href=)', re.DOTALL).findall(result_1)
				directors = []
				for dNames in matchD:
					directors.append(dNames.strip())
				dDirector =", ".join(directors)
			except: dDirector =""
			try: # Grab - Genres
				result_2 = element[element.find('<span class="lighten">Genre')+1:]
				result_2 = result_2[:result_2.find('</tr>')]
				matchG = re.compile('<span itemprop=["\']genre["\']>([^<]+?)</span>', re.DOTALL).findall(result_2)
				genres = []
				for gNames in matchG:
					genres.append(gNames.strip())
				gGenre =", ".join(genres)
			except: gGenre =""
			try: # Grab - Plot
				desc = re.compile("<p[^>]*>([^<]+)<", re.DOTALL).findall(element)[0]
				plot = desc.replace('&nbsp;', '')
				plot = cleanTitle(plot)
			except: plot=""
			try: # Grab - Rating
				rRating = re.compile('<span class=["\']note["\']><span class=["\']acLnk.*?["\']>([^<]+?)</span></span>', re.DOTALL).findall(element)[0].strip().replace(',', '.')
			except: rRating=""
			debug_MS("(listSeries_small) Name : "+name)
			debug_MS("(listSeries_small) Link : "+baseURL+newURL)
			debug_MS("(listSeries_small) Icon : "+photo)
			debug_MS("(listSeries_small) Regie : "+dDirector)
			debug_MS("(listSeries_small) Genre : "+gGenre)
			if newURL !="" and not 'button btn-disabled' in element:
				FOUND = True
				addLink(name, baseURL+newURL, 'playVideo', photo, plot, gGenre, dDirector, rRating, extraURL=url)
			else:
				FOUND = True
				addDir(name+translation(30701), "", 'listSeries_small', photo, plot, gGenre, dDirector, rRating)
		except:
			failing("..... exception .....")
			failing("(listSeries_small) Fehler-Eintrag : {0} #####".format(str(element)))
	if not FOUND:
		return xbmcgui.Dialog().notification(translation(30523), translation(30524), icon, 8000)
	if 'fr">Nächste<i class="icon-arrow-right">' in content:  
		addDir(translation(30685), url, 'listSeries_small', pic+"nextpage.png", page=page+1)
	xbmcplugin.endOfDirectory(pluginhandle)

def listNews(url, page=1):
	debug_MS("(listNews) -------------------------------------------------- START = listNews --------------------------------------------------")
	page = int(page)
	if page > 1:
		PGurl = url+"?page="+str(page)
	else:
		PGurl = url
	debug_MS("(listNews) ##### URL={0} ##### PAGE={1} #####".format(PGurl, str(page)))
	content = getUrl(PGurl)
	result = content[content.find('<div class="colcontent">')+1:]
	result = result[:result.find('class="centeringtable">')]
	part = result.split('<div class="datablock')
	for i in range(1,len(part),1):
		element = part[i]
		try:
			image = re.compile(r'src=["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.DOTALL|re.IGNORECASE).findall(element)[0]
			photo = enlargeIMG(image)
			try:
				matchUN = re.compile('href=["\'](.+?)["\'] class=.*?</strong>([^<]+?)</', re.DOTALL).findall(element)
				link = matchUN[0][0]
				title = matchUN[0][1]
			except:
				matchUN = re.compile('href=["\'](.+?)["\']>(.+?)</a>', re.DOTALL).findall(element)
				link = matchUN[0][0]
				title = matchUN[0][1].replace("\n", "")
				title = re.sub(r'\<.*?\>', '', title)
			name = cleanTitle(title)
			try: # Grab - Plot
				desc = re.compile('class=["\']fs11 purehtml["\']>(.+?)<div class=["\']spacer["\']></div>', re.DOTALL).findall(element)[0]
				plot = re.sub(r'\<.*?\>', '', desc)
				plot = cleanTitle(plot)
			except: plot =""
			debug_MS("(listNews) Name : "+name)
			debug_MS("(listNews) Link : "+baseURL+link)
			debug_MS("(listNews) Icon : "+photo)
			addLink(name, baseURL+link, 'playVideo', photo, plot, extraURL=url)
		except:
			failing("..... exception .....")
			failing("(listNews) Fehler-Eintrag : {0} #####".format(str(element)))
	try:
		nextP = re.compile('(<li class="navnextbtn">[^<]+<span class="acLnk)', re.DOTALL).findall(content)[0]
		addDir(translation(30685), url, 'listNews', pic+"nextpage.png", page=page+1)
	except: pass
	xbmcplugin.endOfDirectory(pluginhandle)

def playVideo(url, extraURL=""):
	debug_MS("(playVideo) -------------------------------------------------- START = playVideo --------------------------------------------------")
	debug_MS("(playVideo) ##### URL={0} ##### REFERER={1} ##### ".format(url, extraURL))
	finalURL = False
	content = getUrl(url, referer=extraURL)
	try:
		LINK = re.compile("<iframe[^>]+?src=['\"](.+?)['\"]", re.DOTALL).findall(content)
		debug_MS("(playVideo) *FOUND-1* Extra-Content : {0}".format(LINK))
		if  "_video" in LINK[1]:
			newURL = baseURL+LINK[1]
			content = getUrl(newURL, referer=url)
		elif "youtube.com" in LINK[0]:
			youtubeID = LINK[0].split('/')[-1].strip()
			debug_MS("(playVideo) *FOUND-2* Extern-Video auf Youtube [ID] : {0}".format(youtubeID))
			finalURL = 'plugin://plugin.video.youtube/play/?video_id='+youtubeID
	except: pass
	if not finalURL:
		DATA = {}
		DATA['media'] = []
		mp4_QUALITIES = ['high', 'medium']
		try:
			response = re.compile(r'(?:class=["\']player  js-player["\']|class=["\']player player-auto-play js-player["\']|<div id=["\']btn-export-player["\'].*?) data-model=["\'](.+?),&quot;disablePostroll&quot;:false', re.DOTALL).findall(content)[0].replace('&quot;', '"')+"}"
			debug_MS("(playVideo) ##### Extraction of Stream-Links : {0} #####".format(response))
			jsonObject = json.loads(response)
			for item in jsonObject['videos']:
				vidQualities = item['sources']
				for found in mp4_QUALITIES:
					for quality in vidQualities:
						if quality == found:
							DATA['media'].append({'url': vidQualities[quality], 'quality': quality, 'mimeType': 'video/mp4'})
				finalURL = DATA['media'][0]['url']
		except: pass
	if finalURL:
		finalURL = finalURL.replace(' ', '%20')
		if not "youtube" in finalURL and finalURL[:4] != "http":
			finalURL ="http:"+finalURL
		log("(playVideo) StreamURL : {0}".format(finalURL))
		listitem = xbmcgui.ListItem(path=finalURL)
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	else:
		failing("(playVideo) ##### Abspielen des Streams NICHT möglich #####\n   ##### URL : {0} #####".format(url))
		return xbmcgui.Dialog().notification((translation(30521).format("URL")), translation(30522), icon, 8000)

def cleanTitle(title):
	title = py2_enc(title)
	title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&Amp;", "&").replace("&#34;", "”").replace("&#39;", "'").replace("&#039;", "'").replace("&quot;", "\"").replace("&Quot;", "\"").replace("&reg;", "").replace("&szlig;", "ß").replace("&mdash;", "-").replace("&ndash;", "-").replace('–', '-').replace('&sup2;', '²')
	title = title.replace("&#x00c4", "Ä").replace("&#x00e4", "ä").replace("&#x00d6", "Ö").replace("&#x00f6", "ö").replace("&#x00dc", "Ü").replace("&#x00fc", "ü").replace("&#x00df", "ß")
	title = title.replace("&Auml;", "Ä").replace("&auml;", "ä").replace("&Euml;", "Ë").replace("&euml;", "ë").replace("&Iuml;", "Ï").replace("&iuml;", "ï").replace("&Ouml;", "Ö").replace("&ouml;", "ö").replace("&Uuml;", "Ü").replace("&uuml;", "ü").replace("&#376;", "Ÿ").replace("&yuml;", "ÿ")
	title = title.replace("&agrave;", "à").replace("&Agrave;", "À").replace("&aacute;", "á").replace("&Aacute;", "Á").replace("&egrave;", "è").replace("&Egrave;", "È").replace("&eacute;", "é").replace("&Eacute;", "É").replace("&igrave;", "ì").replace("&Igrave;", "Ì").replace("&iacute;", "í").replace("&Iacute;", "Í")
	title = title.replace("&ograve;", "ò").replace("&Ograve;", "Ò").replace("&oacute;", "ó").replace("&Oacute;", "ó").replace("&ugrave;", "ù").replace("&Ugrave;", "Ù").replace("&uacute;", "ú").replace("&Uacute;", "Ú").replace("&yacute;", "ý").replace("&Yacute;", "Ý")
	title = title.replace("&atilde;", "ã").replace("&Atilde;", "Ã").replace("&ntilde;", "ñ").replace("&Ntilde;", "Ñ").replace("&otilde;", "õ").replace("&Otilde;", "Õ").replace("&Scaron;", "Š").replace("&scaron;", "š")
	title = title.replace("&acirc;", "â").replace("&Acirc;", "Â").replace("&ccedil;", "ç").replace("&Ccedil;", "Ç").replace("&ecirc;", "ê").replace("&Ecirc;", "Ê").replace("&icirc;", "î").replace("&Icirc;", "Î").replace("&ocirc;", "ô").replace("&Ocirc;", "Ô").replace("&ucirc;", "û").replace("&Ucirc;", "Û")
	title = title.replace("&alpha;", "a").replace("&Alpha;", "A").replace("&aring;", "å").replace("&Aring;", "Å").replace("&aelig;", "æ").replace("&AElig;", "Æ").replace("&epsilon;", "e").replace("&Epsilon;", "Ε").replace("&eth;", "ð").replace("&ETH;", "Ð").replace("&gamma;", "g").replace("&Gamma;", "G")
	title = title.replace("&oslash;", "ø").replace("&Oslash;", "Ø").replace("&theta;", "θ").replace("&thorn;", "þ").replace("&THORN;", "Þ")
	title = title.replace("\\'", "'").replace("&x27;", "'").replace("&iexcl;", "¡").replace("&iquest;", "¿").replace("&rsquo;", "’").replace("&lsquo;", "‘").replace("&sbquo;", "’").replace("&rdquo;", "”").replace("&ldquo;", "“").replace("&bdquo;", "”").replace("&rsaquo;", "›").replace("lsaquo;", "‹").replace("&raquo;", "»").replace("&laquo;", "«")
	title = title.replace("&#183;", "·")
	title = title.replace("&#196;", "Ä")
	title = title.replace("&#214;", "Ö")
	title = title.replace("&#220;", "Ü")
	title = title.replace("&#223;", "ß")
	title = title.replace("&#228;", "ä")
	title = title.replace("&#232;", "è")
	title = title.replace("&#233;", "é")
	title = title.replace("&#234;", "ê")
	title = title.replace("&#239;", "ï")
	title = title.replace("&#246;", "ö")
	title = title.replace("&#252;", "ü")
	title = title.replace("&#287;", "ğ")
	title = title.replace("&#304;", "İ")
	title = title.replace("&#305;", "ı")
	title = title.replace("&#350;", "Ş")
	title = title.replace("&#351;", "ş")
	title = title.replace("&#8211;", "-")
	title = title.strip()
	return title

def cleanMonth(month):
	month = month.replace("januar ", "01-").replace("februar ", "02-").replace("märz ", "03-").replace("april ", "04-").replace("mai ", "05-").replace("juni ", "06-")
	month = month.replace("juli ", "07-").replace("august ", "08-").replace("september ", "09-").replace("oktober ", "10-").replace("november ", "11-").replace("dezember ", "12-")
	month = month.strip()
	return month

def enlargeIMG(cover):
	debug_MS("(enlargeIMG) -------------------------------------------------- START = enlargeIMG --------------------------------------------------")
	debug_MS("(enlargeIMG) 1.Original-COVER : {0}".format(cover))
	try:
		if "commons/" in cover:
			cover = cover.split('.net/')[0]+".net/commons/"+cover.split('commons/')[1]
		elif "medias" in cover:
			cover = cover.split('.net/')[0]+".net/medias"+cover.split('medias')[1]
		elif "pictures" in cover:
			cover = cover.split('.net/')[0]+".net/pictures"+cover.split('pictures')[1]
		elif "seriesposter" in cover:
			cover = cover.split('.net/')[0]+".net/seriesposter"+cover.split('seriesposter')[1]
		elif "videothumbnails" in cover:
			cover = cover.split('.net/')[0]+".net/videothumbnails"+cover.split('videothumbnails')[1]
	except:
		try:
			imgLink = re.compile('(/[a-z]+_[0-9]+_[0-9]+)/', re.DOTALL).findall(cover)[0]
			cover = cover.replace(imgLink, "")
		except: pass
	debug_MS("(enlargeIMG) 2.Converted-COVER : {0}".format(cover))
	return cover

def decodeURL(url):
	debug_MS("(decodeURL) -------------------------------------------------- START = decodeURL --------------------------------------------------")
	debug_MS("(decodeURL) ## URL-Original={0} ##".format(url))
	normalstring = ['3F','2D','13', '1E', '19', '1F', '20', '2A', '21', '22', '2B', '23', '24', '2C', '25', '26', 'BA', 'B1', 'B2', 'BB', 'B3', 'B4', 'BC', 'B5', 'B6', 'BD', 'B7', 'B8', 'BE', 'B9', 'BF', '30', '31', '32', '3B', '33', '34', '3C', '35', '3D', '4A', '41', '42', '4B', '43', '44', '4C', '45', '46', '4D', '47', '48', '4E', '49', '4F', 'C0', 'C1', 'C2', 'CB', 'C3', 'C4', 'CC', 'C5', 'C6', 'CD']
	decodestring = ['_',':','%', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
	result =""
	for i in range(0,len(url),2):
		signs = url[i:i+2]
		ind = normalstring.index(signs)
		dec = decodestring[ind]
		result = result+dec
	debug_MS("(decodeURL) ## URL-Decoded={0} ##".format(result))
	return result

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def addDir(name, url, mode, iconimage, plot=None, genre=None, director=None, rating=None, page=1, type="", CAT_text="", datum="", position=0):  
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&type="+type+"&CAT_text="+str(CAT_text)+"&datum="+str(datum)+"&position="+str(position)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Genre": genre, "Director": director, "Rating": rating})
	liz.setArt({'banner': iconimage, 'poster': iconimage, 'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

def addLink(name, url, mode, iconimage, plot=None, genre=None, director=None, rating=None, duration=None, extraURL=""):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&extraURL="+quote_plus(extraURL)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Genre": genre, "Director": director, "Rating": rating, "Duration": duration, "mediatype": "video"})
	liz.setArt({'banner': iconimage, 'poster': iconimage, 'fanart': defaultFanart})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
iconimage = unquote_plus(params.get('iconimage', ''))
page = unquote_plus(params.get('page', ''))
type = unquote_plus(params.get('type', ''))
CAT_text = unquote_plus(params.get('CAT_text', ''))
datum = unquote_plus(params.get('datum', ''))
position = unquote_plus(params.get('position', ''))
extraURL = unquote_plus(params.get('extraURL', ''))
referer = unquote_plus(params.get('referer', ''))

if mode == 'aSettings':
	addon.openSettings()
elif mode == 'trailer':
	trailer()
elif mode == 'series':
	series()
elif mode == 'kino':
	kino()
elif mode == 'news':
	news()
elif mode == 'filtertrailer':
	filtertrailer(url)
elif mode == 'filterkino':
	filterkino(url)
elif mode == 'filterserien':
	filterserien(url)
elif mode == 'selectionCategories':
	selectionCategories(url, type, CAT_text)
elif mode == 'selectionWeek':
	selectionWeek(url)
elif mode == 'listTrailer':
	listTrailer(url, page)
elif mode == 'listSpecial_Series_Trailer':
	listSpecial_Series_Trailer(url, page)
elif mode == 'listKino_big':
	listKino_big(url, page, datum, position)
elif mode == 'listSeries_big':
	listKino_big(url, page, datum ,position)
elif mode == 'listKino_small':
	listKino_small(url, page)
elif mode == 'listSeries_small':
	listSeries_small(url, page)
elif mode == 'listNews':
	listNews(url, page)
elif mode == 'playVideo':
	playVideo(url, extraURL)
else:
	index()