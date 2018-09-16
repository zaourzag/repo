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
language2 = {0: 'www', 1: 'gr', 2: 'fr', 3: 'de', 4: 'it', 5: 'es', 6: 'pt', 7: 'hu', 8: 'ru', 9: 'ua', 10: 'tr', 11: 'arabic', 12: 'fa'}[int(addon.getSetting('language'))]
# Spachennummerierung(settings) ~ English=0|Greek=1|French=2|German=3|Italian=4|Spanish=5|Portuguese=6|Hungarian=7|Russian=8|Ukrainian=9|Turkish=10|Arabic=11|Persian=12
#         Webseitenkürzel(euronews) = 0: www|1: gr|2: fr|3: de|4: it|5: es|6: pt|7: hu|8: ru|9: ua|10: tr|11: arabic|12: fa
baseURL = "https://"+language2+".euronews.com"

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

def cleanTitle(title):
	return title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#038;", "&").replace("&#39;", "'").replace("&#039;", "'").replace("&#8211;", "-").replace("&#8220;", "-").replace("&#8221;", "-").replace("&#8217;", "'").replace("&#8230;", "…").replace("&quot;", "\"").strip()

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
			opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0')]
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

def Rubriken():
	xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
	un_WANTED = ['Video', 'Living It']
	content = getUrl(baseURL)
	htmlPage = BeautifulSoup(content, 'html.parser')
	elemente = htmlPage.find_all("a",attrs={"class":"enw-menuList__sub-title"})
	liste = []
	for element in elemente:
		url = element["href"]
		name = element.get_text().strip()
		if not name in liste and not any(x in name for x in un_WANTED):
			debug("(Rubriken) ##### URL : "+str(url)+" #####")
			addDir(name, url, 'SubRubriken', icon)
			liste.append(name)
	live(baseURL+"/api/watchlive.json")
	xbmcplugin.endOfDirectory(pluginhandle)   

def SubRubriken(urls):
	debug("(SubRubriken) ##### URLS : "+urls+" #####")
	content = getUrl(baseURL)
	htmlPage = BeautifulSoup(content, "html.parser")
	items = htmlPage.find_all("div",attrs={"class": "medium-2 columns"})
	anz = 0
	liste = []
	addDir("NEWS", urls, 'listVideos', icon)
	for item in items:
		linkmain = item.find("a",attrs={"class":"enw-menuList__sub-title"})["href"]
		if urls == linkmain:
			debug("(SubRubriken) ##### Gefunden #####")
			elemente2 = item.find_all("a",attrs={'class':"enw-menuList__sub-item"})   
			for element2 in elemente2:
				link = baseURL+element2["href"]
				name = element2.get_text().strip()
				debug("(SubRubriken) ##### LINK : "+str(link)+" ##### TITLE : "+str(name)+" #####")
				if not name in liste:
					anz+=1
					url2 = link.split('/')[-1].strip()
					debug("(SubRubriken) ##### URL-2 : "+url2+" #####")
					addDir(name, "/api/program/"+url2, 'listVideos', icon, offset=anz)
					liste.append(name)
	xbmcplugin.endOfDirectory(pluginhandle)
   
def listVideos(url, offset):
	debug("(listVideos) ##### URL : "+url+" ##### OFFSET : "+str(offset)+" #####")
	finalURL = False
	plot =""
	duration =""
	if not "/api/program/" in url and not "###" in url:
		content1 = getUrl(baseURL+url)
		url = re.compile('data-api-url="(.+?)"', re.DOTALL).findall(content1)[0]
  # https://de.euronews.com/api/program/state-of-the-union?before=1519998565&extra=1&offset=13
	url2 = baseURL+url.replace('###', '')+"?extra=1&offset="+str(offset)
	content2 = getUrl(url2)  
	struktur = json.loads(content2)
	for artikel in struktur["articles"]:
		debug("(listVideos) ##### ARTIKEL : "+str(artikel)+" #####")
		title = smart_str(artikel["title"])
		bild = artikel["images"][0]["url"].replace("{{w}}x{{h}}","800x450")
		if "leadin" in artikel and artikel["leadin"] !="":
			plot = smart_str(artikel["leadin"]).strip()
		for video in artikel["videos"]:
			if "duration" in video and video["duration"] !="":
				duration = video["duration"].strip()
				duration = int(duration)/1000
			if video["quality"] == "hd":
				finalURL = video["url"]
		if not finalURL:
			for video in artikel["videos"]:
				if video["quality"] == "md":
					finalURL = video["url"]
		if finalURL:
			addLink(title, finalURL, "playVideo", bild, duration=duration, plot=plot, text=video["quality"].replace('hd', 'HIGH').replace('md', 'MEDIUM').upper())
	#if struktur["extra"]["offset"]< struktur["extra"]["total"]:
		#addDir("Next Page", url+"###", 'listVideos', icon, offset=struktur["extra"]["offset"]+struktur["extra"]["count"]) 
	xbmcplugin.endOfDirectory(pluginhandle)   

def live(url):
	content = getUrl(url)   
	url1 = re.compile('"url":"(.+?)"', re.DOTALL).findall(content)[0]
	url1 = url1.replace("\/","/").split('//')[1]
	debug("(live) ##### URL-1 : "+url1+" #####")
	content1 = getUrl("https://"+url1)  
	url2 = re.compile('"primary":"(.+?)"', re.DOTALL).findall(content1)[0]
	url2 = url2.replace("\/","/").split('//')[1]
	debug("(live) ##### URL-2 : "+url2+" #####")
	addLink("LIVE TV", "https://"+url2, "playVideo", icon)

def playVideo(url, quality):
	log("(playVideo) Quality = "+quality.replace('hd', 'HIGH').replace('md', 'MEDIUM').upper()+" | Url = "+url)
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

def addLink(name, url, mode, iconimage, duration="", plot="", genre='', text="unknown"):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&name="+str(name)+"&text="+str(text)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Duration": duration, "Genre": "News", "Studio": "euronews"})
	if iconimage != icon:
		liz.setArt({'fanart': iconimage})
	else:
		liz.setArt({'fanart': defaultFanart})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

def addDir(name, url, mode, iconimage, plot="", text="unknown", offset=1):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+'&name='+str(name)+"&offset="+str(offset)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
	if iconimage != icon:
		liz.setArt({'fanart': iconimage})
	else:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
text = unquote_plus(params.get('text', ''))
offset = unquote_plus(params.get('offset', ''))
bild = unquote_plus(params.get('bild', ''))
referer = unquote_plus(params.get('referer', ''))

if mode == "SubRubriken":
	SubRubriken(url)
elif mode == "listVideos":
	listVideos(url, offset)
elif mode  == "live":
	live(url)
elif mode == "playVideo":
	playVideo(url, text)
else:
	Rubriken()