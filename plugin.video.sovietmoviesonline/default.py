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
from datetime import datetime
import io
import gzip
import ssl

try:
	_create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
	pass
else:
	ssl._create_default_https_context = _create_unverified_https_context

global debuging
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
temp        = xbmc.translatePath(os.path.join(dataPath, 'temp', '')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg')
icon = os.path.join(addonPath, 'icon.png')
langSHORTCUT = addon.getSetting("language")
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == 'true'
baseURL = "https://sovietmoviesonline.com"

xbmcplugin.setContent(int(sys.argv[1]), 'movies')

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
	#debug("(getUrl) ##### getUrl : "+url+" #####")
	for cook in cj:
		debug("(getUrl) ##### COOKIE : "+str(cook)+" #####")
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
		elif hasattr(e, 'reason'):
			failing("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
		content = ""
		return sys.exit(0)
	opener.close()
	try: cj.save(cookie, ignore_discard=True, ignore_expires=True)
	except: pass
	return content

def index():
	debug("(index) -------------------------------------------------- START = index --------------------------------------------------")
	if langSHORTCUT == "EN":
		startURL = baseURL
	else:
		startURL = baseURL+"/ru"
	addDir(translation(30601), startURL+"/all_movies.html", "listVideos", icon)
	addDir(translation(30602), "", "listTopics", icon, category="Genres")
	addDir(translation(30603), "", "listTopics", icon, category="Decades")
	addDir(translation(30604), "", "listTopics", icon, category="Directors")
	addDir(translation(30608), "", "aSettings", icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def listTopics(category=""):
	debug("(listTopics) -------------------------------------------------- START = listTopics --------------------------------------------------")
	if langSHORTCUT == "EN":
		startURL = baseURL
	else:
		startURL = baseURL+"/ru/"
	debug("(listTopics) ##### startURL : "+startURL+" ##### Category : "+category+" #####")
	content = getUrl(startURL)
	if category == "Genres":
		result = content[content.find('<span class="link movie-popup-link">')+1:]
		result = result[:result.find('</div>')]
	elif category == "Decades":
		result = content[content.find('<div id="decades">')+1:]
		result = result[:result.find('</div>')]
	elif category == "Directors":
		result = content[content.find('<div id="directors">')+1:]
		result = result[:result.find('<div class="clear"></div>')]
	if category == "Genres" or category == "Decades":
		match = re.compile('<a href="([^"]+?)">(.+?)</a>', re.DOTALL).findall(result)
		for url2, title in match:
			if url2[:4] != "http":
				url2 = baseURL+url2
			name = py2_enc(re.sub('\<.*?\>', '', title))
			if category == "Decades" and langSHORTCUT == "EN":
				name += " 's"
			elif category == "Decades" and langSHORTCUT == "RU":
				name += " -e"
			debug("(listTopics) no.1 ### TITLE : "+name+" ### URL-2 : "+url2+" ###")
			addDir(name, url2, "listVideos", icon)
	else:
		match = re.compile(' href="([^"]+?)">.*?<img src="([^"]+?)" alt="([^"]+?)".*?</span>', re.DOTALL).findall(result)
		for url2, thumb, title in match:
			if url2[:4] != "http":
				url2 = baseURL+url2
			if thumb[:4] != "http":
				thumb = baseURL+thumb
			name = py2_enc(re.sub('\<.*?\>', '', title))
			debug("(listTopics) no.2 ### TITLE : "+name+" ### URL-2 : "+url2+" ###")
			addDir(name, url2, "listVideos", thumb)
	xbmcplugin.endOfDirectory(pluginhandle)

def listVideos(url):
	debug("(listVideos) -------------------------------------------------- START = listVideos --------------------------------------------------")
	debug("(listVideos) ##### startURL : "+url+" #####")
	un_WANTED = ['sovietmoviesonline.com/blog/', 'sovietmoviesonline.com/ru/blog/']
	startURL = url
	content = getUrl(url)
	part = content.split('<!--small movie-->')
	for i in range(1, len(part), 1):
		entry = part[i]
		debug("(listVideos) xxxxx ENTRY : "+str(entry)+" xxxxx")
		try:
			url2 = re.compile('<a href="([^"]+?)"', re.DOTALL).findall(entry)[0]
			if url2[:4] != "http":
				url2 = baseURL+url2
			if not any(x in url2 for x in un_WANTED):
				thumb = re.compile('src="([^"]+?)"', re.DOTALL).findall(entry)[0]
				if thumb[:4] != "http":
					thumb = baseURL+thumb
				Title1 = re.compile('<div class="small-title">(.+?)</div>', re.DOTALL).findall(entry)[0]
				Title2 = re.compile('<div class="title">(.+?)</div>', re.DOTALL).findall(entry)[0]
				CPtitle1 = re.sub('\<.*?\>', '', Title1)
				CPtitle2 = re.sub('\<.*?\>', '', Title2)
				if langSHORTCUT == "RU" and "/all_movies" in startURL:
					name = cleanTitle(CPtitle1)+"  ("+cleanTitle(CPtitle2)+")"
				else:
					name = cleanTitle(CPtitle2)+"  ("+cleanTitle(CPtitle1)+")"
				year = re.compile('<div class="year">(.+?)</div>', re.DOTALL).findall(entry)[0]
				#if "teleserial" in url2 or "mini-serial" in url2:
					#addDir(name, url2, "listSeries", thumb)
				#else:
				debug("(listVideos) ### TITLE : "+name+" ### URL-2 : "+url2+" ###")
				debug("(listVideos) ### YEAR : "+year+" ### THUMB : "+thumb+" ###")
				addLink(name, url2, "playVideo", thumb, year=year)
		except:
			failing("(listVideos) ERROR - ERROR - ERROR ### {0} ###".format(str(entry)))
	xbmcplugin.endOfDirectory(pluginhandle)

def listSeries(url, image):
	debug("(listSeries) -------------------------------------------------- START = listSeries --------------------------------------------------")
	debug("(listSeries)  ##### startURL : "+url+" ##### IMAGE : "+image+" #####")
	startURL = url
	content = getUrl(url)
	pos = 0
	result = content[content.find('<div id="video">')+1:]
	result = result[:result.find('<script type="text/javascript" src=')]
	videoPARTS = result.find('<div class="episodes-links')
	if videoPARTS != -1:
		if langSHORTCUT == "EN":
			EPlinks = re.findall('<div class="episodes-links en">(.+?)</div>', result, re.DOTALL)
		else:
			EPlinks = re.findall('<div class="episodes-links ru">(.+?)</div>', result, re.DOTALL)
		for chtml in EPlinks:
			debug("(listSeries) no.1 ### TITLE : Episode 1 ### URL-2 : "+startURL+" ###")
			addLink("Episode 1", startURL, "playVideo", image)
			match = re.compile('<a href="([^"]+?)">(.+?)</a>', re.DOTALL).findall(chtml)
			for url2, title in match:
				pos += 1
				if url2[:4] != "http":
					url2 = baseURL+url2
				name = py2_enc(re.sub('\<.*?\>', '', title))
				debug("(listSeries) no.2 ### TITLE : "+name+" ### URL-2 : "+url2+" ###")
				addLink("Episode "+name, url2, "playVideo", image)
	if pos == 0:
		playVideo(url)
	xbmcplugin.endOfDirectory(pluginhandle)
  
def playVideo(url):
	debug("(playVideo) -------------------------------------------------- START = playVideo --------------------------------------------------")
	debug("(playVideo)  ##### startURL : "+url+" #####")
	finalURL = False
	content = getUrl(url)
	try:
		finalURL = re.compile('<source src="([^"]+?)"', re.DOTALL).findall(content)[0]
		if finalURL and finalURL != "" and finalURL[:4] != "http":
			finalURL = baseURL+finalURL
		try:
			if langSHORTCUT == "EN":
				SUB = re.compile('track src="([^"]+?)"', re.DOTALL).findall(content)[0]
			else:
				SUB = re.compile('track src="([^"]+?)"', re.DOTALL).findall(content)[1]
			subContent = getUrl(baseURL+SUB)
			subFile = temp+"/sub.srt"
			fh = open(subFile, 'wb')
			fh.write(subContent)
			fh.close()
		except:
			SUB = ""
			subFile = ""
		debug("(playVideo) ### finalURL : "+str(finalURL)+" ###")
		debug("(playVideo) ### subTITLE : "+SUB+" ###")
		if finalURL:
			listitem = xbmcgui.ListItem(path=finalURL)
			listitem.setSubtitles([subFile])
			xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
			log("(playVideo) streamURL : {0}".format(finalURL))
	except:
		if '<div id="dle-info"  title="Error">' in content or '<div id="dle-info"  title="Ошибка">' in content:
			xbmcgui.Dialog().notification(addon.getAddonInfo('id')+translation(30521), translation(30522), icon, 8000)
		else:
			failing("(playVideo) PlayLink-00 : *Intern* Error requesting the play link !!!")

def cleanTitle(title):
	title = py2_enc(title)
	title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
	title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
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
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&image="+quote_plus(image)+"&category="+str(category)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
	if useThumbAsFanart and image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

def addLink(name, url, mode, image, plot=None, duration=None, year=""):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Duration': duration, 'Year': year, 'Studio': 'sovietmovies'})
	if image != icon:
		liz.setArt({'poster': image})
	if useThumbAsFanart and image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
image = unquote_plus(params.get('image', ''))
category = unquote_plus(params.get('category', ''))
referer = unquote_plus(params.get('referer', ''))

if mode == 'listTopics':
	listTopics(category)
elif mode == 'listVideos':
	listVideos(url)
elif mode == 'listSeries':
	listSeries(url, image)
elif mode == 'playVideo':
	playVideo(url)
elif mode == 'aSettings':
	addon.openSettings()
else:
	index()