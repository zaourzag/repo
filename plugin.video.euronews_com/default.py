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
from django.utils.encoding import smart_str
import io
import gzip


global debuging
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath    = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
temp           = xbmc.translatePath(os.path.join(dataPath, 'temp', '')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg')
icon = os.path.join(addonPath, 'icon.png')
langSHORTCUT = {0: 'www', 1: 'gr', 2: 'fr', 3: 'de', 4: 'it', 5: 'es', 6: 'pt', 7: 'hu', 8: 'ru', 9: 'ua', 10: 'tr', 11: 'arabic', 12: 'fa'}[int(addon.getSetting('language'))]
# Spachennummerierung(settings) ~ English=0|Greek=1|French=2|German=3|Italian=4|Spanish=5|Portuguese=6|Hungarian=7|Russian=8|Ukrainian=9|Turkish=10|Arabic=11|Persian=12
#         Webseitenkürzel(euronews) = 0: www|1: gr|2: fr|3: de|4: it|5: es|6: pt|7: hu|8: ru|9: ua|10: tr|11: arabic|12: fa
baseURL = "https://"+langSHORTCUT+".euronews.com"

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

if not os.path.exists(os.path.join(dataPath, 'settings.xml')):
	addon.openSettings()

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
			xbmcgui.Dialog().notification((translation(30521).format("URL")), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 12000)
		elif hasattr(e, 'reason'):
			failing("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
			xbmcgui.Dialog().notification((translation(30521).format("URL")), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 12000)
		content = ""
		return sys.exit(0)
	opener.close()
	try: cj.save(cookie, ignore_discard=True, ignore_expires=True)
	except: pass
	return content

def TopicsIndex():
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
	debug("(TopicsIndex) -------------------------------------------------- START = TopicsIndex --------------------------------------------------")
	debug("(TopicsIndex) ##### baseURL : "+baseURL+" #####")
	un_WANTED = ['Video', 'Living It']
	title_ISOLATED = set()
	content = getUrl(baseURL)
	htmlPage = BeautifulSoup(content, 'html.parser')
	elements = htmlPage.find_all("a",attrs={"class":"enw-menuList__sub-title"})
	for elem in elements:
		url = elem["href"]
		name = smart_str(elem.get_text()).strip()
		if not any(x in name for x in un_WANTED):
			newNAME = name.lower()
			if newNAME in title_ISOLATED:
				continue
			title_ISOLATED.add(newNAME)
			debug("(TopicsIndex) ### TITLE : "+name+" ### URL : "+url+" ###")
			addDir(name, url, "SubTopics", icon)
	liveTV(baseURL+"/api/watchlive.json")
	xbmcplugin.endOfDirectory(pluginhandle)   

def SubTopics(firstURL):
	debug("(SubTopics) -------------------------------------------------- START = SubTopics --------------------------------------------------")
	debug("(SubTopics) ##### startURL : "+firstURL+" #####")
	url_ISOLATED = set()
	content = getUrl(baseURL)
	addDir("NEWS", firstURL, "listVideos", icon)
	result = content[content.find('<li id="programs_links" class="programs_links">')+1:]
	result = result[:result.find('<div class="top-bar-allviews__footer">')]
	part = result.split('<h3')
	for i in range(1,len(part),1):
		entry = part[i]
		debug("(SubTopics) xxxxx ENTRY : "+str(entry)+" xxxxx")
		if firstURL in str(entry):
			debug("(SubTopics) +++++ Eintrag gefunden +++++")
			match = re.compile('<li><a href="([^"]+?)".*?class="js-menu.*?enw-menuList__sub-item.*?>([^<]+?)</a></li>', re.DOTALL).findall(entry)
			for link, title in match:
				newURL = link.split('/')[-1].strip()
				if newURL in url_ISOLATED:
					continue
				url_ISOLATED.add(newURL)
				name = smart_str(title).strip()
				debug("(SubTopics) ### TITLE : "+name+" ### newURL : /api/program/"+newURL+" ###")
				addDir(name, "/api/program/"+newURL, "listVideos", icon, category=name)
	xbmcplugin.endOfDirectory(pluginhandle)

def listVideos(url, category=""):
	debug("(listVideos) -------------------------------------------------- START = listVideos --------------------------------------------------")
	debug("(listVideos) ### startURL : "+url+" ### CATEGORY : "+category+" ###")
	finalURL = False
	EMPTY = True
	plot =""
	YOUTUBE_id = ""
	duration =""
	vid_ISOLATED = set()
	if not "/api/program/" in url and not "###" in url:
		content1 = getUrl(baseURL+url)
		url = re.compile('data-api-url="(.+?)"', re.DOTALL).findall(content1)[0]
	# https://de.euronews.com/api/program/state-of-the-union?before=1519998565&extra=1&offset=13
	if url[:2] == "//":
		url2 = "https:"+url.replace('###', '')+"?extra=1"
	else:
		url2 = baseURL+url.replace('###', '')+"?extra=1"
	debug("(listVideos) ##### URL-2 : "+url2+" #####")
	content2 = getUrl(url2)  
	DATA = json.loads(content2)
	for article in DATA['articles']:
		debug("(listVideos) xxxxx ARTIKEL : "+str(article)+" xxxxx")
		name = smart_str(article['title']).strip()
		thumb = article['images'][0]['url'].replace('{{w}}x{{h}}', '861x485')
		if "leadin" in article and article['leadin'] !="":
			plot = smart_str(article['leadin']).strip()
		debug("(listVideos) ##### Title : "+name+" #####")
		debug("(listVideos) ##### Thumb : "+thumb+" #####")
		for video in article['videos']:
			if "quality" in video and video['quality'] == "md":
				finalURL = video['url']
				EMPTY = False
			elif "quality" in video and video['quality'] == "hd":
				finalURL = video['url']
				EMPTY = False
			if "youtubeId" in video and video['youtubeId'] != "" and "quality" in video and video['quality'] == "md":
				YOUTUBE_id = video['youtubeId']
			elif "youtubeId" in video and video['youtubeId'] != "" and "quality" in video and video['quality'] == "hd":
				YOUTUBE_id = video['youtubeId']
			if "duration" in video and video['duration'] != "" and "quality" in video and video['quality'] == "md":
				duration = int(video['duration'])/1000
			elif "duration" in video and video['duration'] != "" and "quality" in video and video['quality'] == "hd":
				duration = int(video['duration'])/1000
		if not finalURL or finalURL in vid_ISOLATED:
			continue
		vid_ISOLATED.add(finalURL)
		debug("(listVideos) ##### Video : "+str(finalURL)+" #####")
		debug("(listVideos) ##### YT-ID : "+str(YOUTUBE_id)+" #####")
		addLink(name, finalURL, "playVideo", thumb, plot, duration, YOUTUBE_id)
	#if DATA['extra']['offset'] < DATA['extra']['total']:
		#addDir("Next Page  >>>", url+"###", "listVideos", icon, offset=DATA['extra']['offset']+DATA['extra']['count'])
	if EMPTY:
		return xbmcgui.Dialog().notification((translation(30522).format('Videos')), (translation(30524).format(category)), icon, 8000)
	xbmcplugin.endOfDirectory(pluginhandle)   

def liveTV(url):
	debug("(liveTV) -------------------------------------------------- START = liveTV --------------------------------------------------")
	debug("(liveTV) ##### startURL : "+url+" #####")
	content = getUrl(url)   
	url1 = re.compile('"url":"(.+?)"', re.DOTALL).findall(content)[0]
	url1 = url1.replace("\/","/").split('//')[1]
	debug("(liveTV) ##### URL-1 : https://"+url1+" #####")
	content1 = getUrl("https://"+url1)  
	url2 = re.compile('"primary":"(.+?)"', re.DOTALL).findall(content1)[0]
	url2 = url2.replace("\/","/").split('//')[1]
	debug("(liveTV) ##### URL-2 : https://"+url2+" #####")
	addLink("[COLOR lime]* EURONEWS LIVE-TV *[/COLOR]", "https://"+url2, "playVideo", icon)

def playVideo(url, YOUTUBE_id=""):
	debug("(playVideo) -------------------------------------------------- START = playVideo --------------------------------------------------")
	log("(playVideo) ### YoutubeID = "+YOUTUBE_id+" | Standard-URL = "+url+" ###")
	if (addon.getSetting("preferredStream_YOUTUBE") == "true" and YOUTUBE_id != "None"):
		url = 'plugin://plugin.video.youtube/play/?video_id='+YOUTUBE_id
	listitem = xbmcgui.ListItem(path=url)  
	xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def addLink(name, url, mode, image, plot=None, duration=None, YOUTUBE_id="None"):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&YOUTUBE_id="+str(YOUTUBE_id)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Duration': duration, 'Genre': 'News', 'Studio': 'euronews'})
	if image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

def addDir(name, url, mode, image, plot=None, category=""):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&category="+str(category)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=image)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
	if image != icon:
		liz.setArt({'fanart': image})
	else:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
image = unquote_plus(params.get('image', ''))
YOUTUBE_id = unquote_plus(params.get('YOUTUBE_id', ''))
category = unquote_plus(params.get('category', ''))
#offset = unquote_plus(params.get('offset', ''))
referer = unquote_plus(params.get('referer', ''))

if mode == "SubTopics":
	SubTopics(url)
elif mode == "listVideos":
	listVideos(url, category)
elif mode  == "liveTV":
	liveTV(url)
elif mode == "playVideo":
	playVideo(url, YOUTUBE_id)
else:
	TopicsIndex()