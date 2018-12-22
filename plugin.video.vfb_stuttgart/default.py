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
import requests
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
enableInputstream = addon.getSetting("inputstream") == "true"
enableFreeVids = addon.getSetting("freeonly") == "true"
baseURL="https://vfbtv.vfb.de/tv"

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)

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

def getUrl(url, header=None, referer=None):
	debug("(getUrl) -------------------------------------------------- START = getUrl --------------------------------------------------")
	global cj
	for cook in cj:
		debug("(getUrl) Cookie : {0}".format(str(cook)))
	opener = build_opener(HTTPCookieProcessor(cj))
	try:
		if header:
			opener.addheaders = header
		else:
			opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36')]
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
			xbmcgui.Dialog().notification((translation(30521).format("URL")), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 12000)
		elif hasattr(e, 'reason'):
			failing("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
			xbmcgui.Dialog().notification((translation(30521).format("URL")), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 12000)
		content = ""
		return sys.exit(0)
	opener.close()
	try:
		cj.save(cookie, ignore_discard=True, ignore_expires=True)
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

def LOGIN(firstFOUND):
	debug("(LOGIN) -------------------------------------------------- START = LOGIN --------------------------------------------------")
	username = addon.getSetting("user")
	password = addon.getSetting("pass")
	if username !="" and password !="":
		# URLs zur Anmeldung = "https://shop.vfb.de/account/ajax_login"
		# URLs zur Anmeldung = "https://shop.vfb.de/konto/anmeldung"
		# URL zum ABO = "https://shop.vfb.de/konto/anmeldung"
		payload = urlencode({'username': username, 'password': password})
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0'}
			#'Host':                               'vfbtv.vfb.de',
			#'Accept':                           'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			#'Accept-Language':        'de,en-US;q=0.7,en;q=0.3',
			#'Accept-Encoding':         'gzip, deflate, br',
			#'Content-Type':               'text/html; charset=utf-8',
		#}
		ACCOUNT_URL = "https://vfbtv.vfb.de/ajax.php?contelPageId=167&noCache=1&cmd=login&"+payload
		debug("(LOGIN) ##### PAYLOAD : {0} #####".format(payload))
		with requests.Session() as rs:
			doLogin_URL = rs.post(ACCOUNT_URL, data=payload, allow_redirects=True, verify=True, headers=headers).text
			doLogin_URL = py2_enc(doLogin_URL)
			debug("(LOGIN) ##### doLogin_URL : {0} #####".format(doLogin_URL))
			if '"success":true' in doLogin_URL:
				streamAccess_URL = rs.get("https://vfbtv.vfb.de/video/streamAccess.php?videoId="+str(firstFOUND)+"&target=2&partner=2119&format=iphone", allow_redirects=True, verify=True, headers=headers).text
				streamAccess_URL = py2_enc(streamAccess_URL)
				debug("(LOGIN) ##### streamAccess_URL-1 : {0} #####".format(streamAccess_URL))
				if '"message":"Pay-Access granted"' in streamAccess_URL or '"message":"Video has free access"' in streamAccess_URL:
					return 1,streamAccess_URL
				else:
					failing("(LOGIN) LOGIN leider NICHT erfolgreich ##### streamAccess_URL-2 : {0} #####".format(streamAccess_URL))
					xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30502))
					return 0,"0"
			else:
				failing("(LOGIN) LOGIN leider NICHT erfolgreich ### EMAIL : {0} ### PASSWORT : {1} ### bitte überprüfen Sie Ihre Login-Daten !!!".format(username, password))
				xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30502))
				return 0,"0"
	else:
		failing("(LOGIN) Für dieses Video ist ein 'Bezahl-ABO' erforderlich - Bitte ein 'Bezahl-ABO' unter 'https://shop.vfb.de/registrierung/' einrichten !!!")
		xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30503))
		return 0,"0"
  
def index():
	debug("(index) -------------------------------------------------- START = index --------------------------------------------------")
	content = getUrl("https://vfbtv.vfb.de/tv/")
	selection = re.findall('<a id="(.+?)" class="access-key-anchor" data-access-key=".*?" data-access-title="(.+?)".*?</a>', content, re.DOTALL)
	for id, title in selection:
		debug("(index) TITLE : {0} ##### ID : {1}".format(title, id))
		title = cleanTitle(title)
		addDir(title, title, "listOverview", icon, category=title)
	addDir(translation(30601), "", "aSettings", icon)
	if enableInputstream:
		if ADDON_operate('inputstream.adaptive'):
			addDir(translation(30602), "", "iSettings", icon)
		else:
			addon.setSetting("inputstream", "false")
	xbmcplugin.endOfDirectory(pluginhandle)

def listOverview(url, category=""):
	debug("(listOverview) -------------------------------------------------- START = listOverview --------------------------------------------------")
	debug("(listOverview) ### URL : {0} ### CATEGORY : {1} ###".format(url, category))
	content = getUrl("https://vfbtv.vfb.de/tv/")
	result = content[content.find('data-access-title="'+category+'"'):]
	result = result[:result.find('</ul>')]
	match = re.compile('<a href="(.+?)" target="_self">(.+?)</a>', re.DOTALL).findall(result)
	for link, title in match:
		title = cleanTitle(title)
		if link[:4] != "http" and link[:4] != "/tv/":
			link = baseURL+link
		elif link[:4] != "http" and link[:4] == "/tv/":
			link = "https://vfbtv.vfb.de"+link
		if "bundesliga" in link:
			addDir(title, link, "listSaisons", icon, category="Bundesliga")
		elif "dfb-pokal" in link:
			addDir(title, link, "listSaisons", icon, category="DFB-Pokal")
		else:
			addDir(title, link, "listVideos", icon, category=title)
		debug("(listOverview) TITLE : {0} ##### LINK : {1}".format(title, link))
	xbmcplugin.endOfDirectory(pluginhandle)

def listSaisons(url, category=""):
	debug("(listSaisons) -------------------------------------------------- START = listSaisons --------------------------------------------------")
	debug("(listSaisons) ### URL : {0} ### CATEGORY : {1} ###".format(url, category))
	startURL = url
	content = getUrl(url)
	result = content[content.find('class="meldung-navi dropdown barrierfree-jumplink-anchor" data-barrierfree-jumplink="Content Navigation"')+1:]
	result = result[:result.find('</ul>')]
	match = re.compile('target="_self" href="([^"]+?)">(.+?)</a>', re.DOTALL).findall(result)
	if category == "Bundesliga":
		for link, title in match:
			title = cleanTitle(title)
			if link[:4] != "http" and link[:4] != "/tv/":
				link = baseURL+link
			elif link[:4] != "http" and link[:4] == "/tv/":
				link = "https://vfbtv.vfb.de"+link
			if ("/2--bundesliga/" in startURL and "/2--bundesliga/" in link) or ("/bundesliga/" in startURL and "/bundesliga/" in link):
				addDir(title, link, "listGamedays", icon, category=title)
			debug("(listSaisons) TITLE[1] : {0} ##### LINK[1] : {1}".format(title, link))
	elif category == "DFB-Pokal":
		for link, title in match:
			title = cleanTitle(title)
			if "/2--bundesliga/" in link:
				link = link.split('/2--bundesliga/')[0]+"/dfb-pokal/"
				debug("(listSaisons) newLINK-dfb[1] : {0}".format(link))
			elif "/bundesliga/" in link:
				link = link.split('/bundesliga/')[0]+"/dfb-pokal/"
				debug("(listSaisons) newLINK-dfb[2] : {0}".format(link))
			if link[:4] != "http" and link[:4] != "/tv/":
				link = baseURL+link
			elif link[:4] != "http" and link[:4] == "/tv/":
				link = "https://vfbtv.vfb.de"+link
			if (not "/saison-2015-2016" in startURL and not "/saison-2015-2016" in link):
				addDir(title, link, "listGamedays", icon, category=title)
			debug("(listSaisons) TITLE[2] : {0} ##### LINK[2] : {1}".format(title, link))
	xbmcplugin.endOfDirectory(pluginhandle)

def listGamedays(url, category=""):
	debug("(listGamedays) -------------------------------------------------- START = listGamedays --------------------------------------------------")
	debug("(listGamedays) ### URL : {0} ### CATEGORY : {1} ###".format(url, category))
	count = 0
	pos1 = 0
	pos2 = 0
	startSELECTION = ['<div class="spieltage swiper-container">', 'class="meldung-navi grey barrierfree-jumplink-anchor" data-barrierfree-jumplink="Content Navigation"', 'class="meldung-navi barrierfree-jumplink-anchor" data-barrierfree-jumplink="Content Navigation"']
	SPORTSNAME = category
	content = getUrl(url)
	if any(x in content for x in startSELECTION):
		if startSELECTION[0] in content:
			result = content[content.find(startSELECTION[0])+1:]
			part = result.split('class="image swiper-slide"')
			for i in range(1,len(part),1):
				entry = part[i]
				try:
					link = re.compile('href="([^"]+?)"', re.DOTALL).findall(entry)[0]
					if link[:4] != "http" and link[:4] != "/tv/":
						link = baseURL+link
					elif link[:4] != "http" and link[:4] == "/tv/":
						link = "https://vfbtv.vfb.de"+link
					photo = re.compile('<img.+?src="([^"]+?)" alt=', re.DOTALL).findall(entry)[0].replace('x_143x80', 'x_960x540')
					if photo[:4] != "http" and photo[:4] == "/tv/":
						photo = "https://vfbtv.vfb.de"+photo
					title = re.compile('class="spieltag">(.+?)</div>', re.DOTALL).findall(entry)[0]
					title = cleanTitle(title)
					addDir(title, link, "listVideos", photo, category=title)
				except:
					pos1 += 1
					failing("(listGamedays) Fehler-Eintrag-01 : {0} #####".format(str(entry)))
					if pos1 > 1 and count == 0:
						count += 1
						xbmcgui.Dialog().notification((translation(30521).format("DISPLAY")), translation(30523), icon, 8000)
		elif startSELECTION[1] in content or startSELECTION[2] in content:
			if startSELECTION[1] in content:
				result = content[content.find(startSELECTION[1])+1:]
			else:
				result = content[content.find(startSELECTION[2])+1:]
			result = result[:result.find('<div class="clear">')]
			part = result.split('target="_self"')
			for i in range(1,len(part),1):
				entry = part[i]
				try:
					link = re.compile('href="([^"]+?)"', re.DOTALL).findall(entry)[0]
					if link[:4] != "http" and link[:4] != "/tv/":
						link = baseURL+link
					elif link[:4] != "http" and link[:4] == "/tv/":
						link = "https://vfbtv.vfb.de"+link
					title = re.compile('<span>(.+?)</span>', re.DOTALL).findall(entry)[0]
					title = cleanTitle(title)
					addDir(title, link, "listVideos", icon, category=title)
				except:
					pos2 += 1
					failing("(listGamedays) Fehler-Eintrag-02 : {0} #####".format(str(entry)))
					if pos2 > 1 and count == 0:
						count += 1
						xbmcgui.Dialog().notification((translation(30521).format("DISPLAY")), translation(30523), icon, 8000)
	else:
		debug("(listGamedays) Leider gibt es in der Rubrik : {0} - KEINE Einträge !".format(SPORTSNAME))
		return xbmcgui.Dialog().notification((translation(30522).format("Einträge")), (translation(30524).format(SPORTSNAME.upper())), icon, 8000)
	xbmcplugin.endOfDirectory(pluginhandle)

def listVideos(url, category=""):
	debug("(listVideos) -------------------------------------------------- START = listVideos --------------------------------------------------")
	debug("(listVideos) ### URL : {0} ### CATEGORY : {1} ###".format(url, category))
	count = 0
	pos1 = 0
	FOUND = False
	SPORTSNAME = category
	content = getUrl(url)
	selection = re.findall('<article class="barrierfree-jumplink-anchor"(.+?)</article>', content, re.DOTALL)
	for chtml in selection:
		if ('class="zusatz">gratis</div>' in str(chtml) and enableFreeVids) or not enableFreeVids:
			FOUND = True
			try:
				link = re.compile('href="([^"]+?)"', re.DOTALL).findall(chtml)[0]
				if link[:4] != "http" and link[:4] != "/tv/":
					link = baseURL+link
				elif link[:4] != "http" and link[:4] == "/tv/":
					link = "https://vfbtv.vfb.de"+link
				photo = re.compile('<img.+?src="([^"]+?)" alt=', re.DOTALL).findall(chtml)[0].replace('f_274x154', 'f')
				if photo[:4] != "http" and photo[:4] == "/tv/":
					photo = "https://vfbtv.vfb.de"+photo
				try: datum = re.compile('class="date">(.+?)</div>', re.DOTALL).findall(chtml)[0]
				except: datum = ""
				title = re.compile('class="title">(.+?)</div>', re.DOTALL).findall(chtml)[0]
				title = cleanTitle(title)
				if datum != "":
					title = title+"  ("+datum+")"
				try: 
					desc = re.compile('class="text">(.+?)</div>', re.DOTALL).findall(chtml)[0]
					plot = re.sub('\<.*?\>', '', desc)
					plot = cleanTitle(plot)
				except: plot = ""
				if 'class="zusatz">gratis</div>' in str(chtml):
					access = "Free-Video"
				else:
					access = "Pay-Video"
				addLink(title, link, "playVideo", photo, plot=plot, category=access)
			except:
				pos1 += 1
				failing("(listVideos) Fehler-Eintrag-01 : {0} #####".format(str(chtml)))
				if pos1 > 1 and count == 0:
					count += 1
					xbmcgui.Dialog().notification((translation(30521).format("DISPLAY")), translation(30523), icon, 8000)
	if not FOUND:
		if not enableFreeVids:
			debug("(listVideos) Leider gibt es in der Rubrik : {0} - überhaupt KEINE verfügbaren Videos !".format(SPORTSNAME))
			return xbmcgui.Dialog().notification((translation(30522).format("Einträge")), (translation(30524).format(SPORTSNAME.upper())), icon, 8000)
		else:
			debug("(listVideos) Leider gibt es in der Rubrik : {0} - KEINE 'Gratis Videos' !".format(SPORTSNAME))
			return xbmcgui.Dialog().notification((translation(30522).format("'Gratis Videos'")), (translation(30524).format(SPORTSNAME.upper())), icon, 8000)
	xbmcplugin.endOfDirectory(pluginhandle)

def playVideo(url, category=""):
	debug("(playVideo) -------------------------------------------------- START = playVideo --------------------------------------------------")
	debug("(playVideo) ### URL : {0} ### CATEGORY : {1} ###".format(url, category))
	Access_List = []
	content = getUrl(url)
	firstFOUND = re.compile('data-video="([^"]+?)"', re.DOTALL).findall(content)[0]
	debug("(playVideo) firstFOUND : {0}".format(firstFOUND))
	if category=="Free-Video":
		secondURL = "https://vfbtv.vfb.de/video/streamAccess.php?videoId="+str(firstFOUND)+"&target=2&partner=2119&format=iphone"
		content2 = getUrl(secondURL)
		debug("(playVideo) CONTENT-Free-Video : {0}".format(content2))
		struktur = json.loads(content2)
	elif category=="Pay-Video":
		Status,Konto = LOGIN(firstFOUND)
		if Status == 1:
			debug("(playVideo) CONTENT-Pay-Video : {0}".format(Konto))
			struktur = json.loads(Konto)
		else:
			return
	if "data" in struktur and "stream-access" in struktur["data"] and not "error" in struktur["status"]:
		for video in struktur["data"]["stream-access"]:
			Access_List.append(video)
	if Access_List:
		if len(Access_List) > 1:
			link = Access_List[1]
			log("(playVideo) Wir haben 2 *StreamZugänge* - wähle den Zweiten : {0}".format(link))
		else:
			link = Access_List[0]
			log("(playVideo) Wir haben 1 *StreamZugang* - wähle Diesen : {0}".format(link))
		if link[:4] != "http" and link[:2] == "//":
			link = "https:"+link
		content3 = getUrl(link)
		url_FOUND = re.compile('url="([^"]+?)"', re.DOTALL).findall(content3)[0].replace('&amp;', '&')
		auth_FOUND = re.compile('auth="([^"]+?)"', re.DOTALL).findall(content3)[0].replace('&amp;', '&')
		finalURL = url_FOUND+"?hdnea="+auth_FOUND#+"&custom-mdt=on&b=0-10000"
		# Möglichkeit Video als -mp4- abzuspielen :
		# streamURL = url_FOUND+"?hdnea="+auth_FOUND#+"&custom-mdt=on&b=0-10000"
		# standardURL = "http://tvstreaming.vfb.de/"+streamURL.split('hdflash/')[1].split('_,low,')[0]+"_low.mp4"
		# finalURL = VideoBEST(standardURL)
		log("(playVideo) StreamURL : {0}".format(finalURL))
		listitem = xbmcgui.ListItem(path=finalURL)
		if enableInputstream and 'mil/master.m3u8' in finalURL:
			if ADDON_operate('inputstream.adaptive'):
				listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
				listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
				listitem.setMimeType('application/vnd.apple.mpegurl')
			else:
				addon.setSetting("inputstream", "false")
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	else:
		failing("(playVideo) ##### Abspielen des Streams NICHT möglich #####\n   ##### URL : {0} #####".format(url))
		return xbmcgui.Dialog().notification((translation(30521).format("URL")), translation(30525), icon, 8000)

def VideoBEST(best_url):
	# *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
	standards = [best_url,"","",""]
	standards[1] = standards[0].replace('_low.mp4', '_high.mp4')
	standards[2] = standards[1].replace('_high.mp4', '_hd.mp4')
	standards[3] = standards[2].replace('_hd.mp4', '_uhd.mp4')
	for element in reversed(standards):
		if len(element) > 0:
			try:
				code = urlopen(element).getcode()
				if str(code) == "200":
					return element
			except: pass
	return best_url

def cleanTitle(title):
	title = py2_enc(title)
	title = title.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&#39;', '\'').replace('&#039;', '\'').replace('&quot;', '"').replace('&szlig;', 'ß').replace('&ndash;', '-').replace('&nbsp;', ' ')
	title = title.replace('&#x00c4', 'Ä').replace('&#x00e4', 'ä').replace('&#x00d6', 'Ö').replace('&#x00f6', 'ö').replace('&#x00dc', 'Ü').replace('&#x00fc', 'ü').replace('&#x00df', 'ß')
	title = title.replace('&Auml;', 'Ä').replace('&Ouml;', 'Ö').replace('&Uuml;', 'Ü').replace('&auml;', 'ä').replace('&ouml;', 'ö').replace('&uuml;', 'ü')
	title = title.replace('&agrave;', 'à').replace('&aacute;', 'á').replace('&acirc;', 'â').replace('&egrave;', 'è').replace('&eacute;', 'é').replace('&ecirc;', 'ê').replace('&igrave;', 'ì').replace('&iacute;', 'í').replace('&icirc;', 'î')
	title = title.replace('&ograve;', 'ò').replace('&oacute;', 'ó').replace('&ocirc;', 'ô').replace('&ugrave;', 'ù').replace('&uacute;', 'ú').replace('&ucirc;', 'û')
	title = title.replace("\\'", "'").replace('<br />', ' -')
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

def addDir(name, url, mode, image, plot=None, category=""):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&category="+quote_plus(category)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
	if image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

def addLink(name, url, mode, image, plot=None, duration=None, studio=None, genre=None, category=""):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&category="+quote_plus(category)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Duration": duration, "Studio": "VfB-Stuttgart TV", "Genre": "Fussball", "mediatype": "video"})
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
category = unquote_plus(params.get('category', ''))
referer = unquote_plus(params.get('referer', ''))

if mode == 'aSettings':
	addon.openSettings()
elif mode == 'iSettings':
	xbmcaddon.Addon('inputstream.adaptive').openSettings()
elif mode == 'listOverview':
	listOverview(url, category)
elif mode == 'listSaisons':
	listSaisons(url, category)
elif mode == 'listGamedays':
	listGamedays(url, category)
elif mode == 'listVideos':
	listVideos(url, category)
elif mode == 'playVideo':
	playVideo(url, category)
else:
	index()