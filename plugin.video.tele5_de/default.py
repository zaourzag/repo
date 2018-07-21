#!/usr/bin/python
# -*- coding: utf-8 -*-

#import urlparse  # Python 2.X
#import urllib.parse  # Python 3+
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import os
import re
import sys
try:
	import urllib, urllib2  # Python 2.X
	import cookielib  # Python 2.X
	unquote_plus = urllib.unquote_plus
	quote_plus = urllib.quote_plus
	quote = urllib.quote
	urlopen = urllib.urlopen
	makeRequest = urllib2
	makeCooks = cookielib
except ImportError:
	import urllib.parse, urllib.request  # Python 3+
	import http.cookiejar  # Python 3+
	unquote_plus = urllib.parse.unquote_plus
	quote_plus = urllib.parse.quote_plus
	quote = urllib.parse.quote
	urlopen = urllib.request.urlopen
	makeRequest = urllib.request
	makeCooks = http.cookiejar
import json
import xbmcvfs
import shutil
import socket
import time
from bs4 import BeautifulSoup
import io
import gzip


global debuging
base_url = sys.argv[0]
pluginhandle = int(sys.argv[1])
#args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
temp        = xbmc.translatePath(os.path.join(dataPath, 'temp', '')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath ,'fanart.jpg').encode('utf-8').decode('utf-8')
icon = os.path.join(addonPath ,'icon.png').encode('utf-8').decode('utf-8')
baseURL = "https://www.tele5.de/"

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

if xbmcvfs.exists(temp) and os.path.isdir(temp):
	shutil.rmtree(temp, ignore_errors=True)
xbmcvfs.mkdirs(temp)
cookie = os.path.join(temp, 'cookie.lwp')
cj = makeCooks.LWPCookieJar();

if xbmcvfs.exists(cookie):
	cj.load(cookie, ignore_discard=True, ignore_expires=True)

def translation(id):
	LANGUAGE = addon.getLocalizedString(id)
	if sys.version_info[0] < 3:
		if isinstance(LANGUAGE, unicode):
			LANGUAGE = LANGUAGE.encode('utf-8')
	return LANGUAGE

def log_Special(msg, level=xbmc.LOGNOTICE):
	if sys.version_info[0] < 3:
		if isinstance(msg, unicode):
			msg = msg.encode('utf-8')
	xbmc.log('[Tele5]'+msg, level)

def debug(content):
	log(content, xbmc.LOGDEBUG)
    
def notice(content):
	log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
	if sys.version_info[0] < 3:
		if isinstance(msg, unicode):
			msg = msg.encode('utf-8')
	xbmc.log('[plugin.video.tele5_de]'+msg, level)

def getUrl(url, header=False, referer=False):
	global cj
	debug("Get Url : "+url)
	for cook in cj:
		debug("Cookie : "+str(cook))
	opener = makeRequest.build_opener(makeRequest.HTTPCookieProcessor(cj))
	try:
		if header:
			opener.addheaders = header
		else:
			opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')]
			opener.addheaders = [('Accept-Encoding', 'gzip, deflate')]
		if referer:
			opener.addheaders = [('Referer', referer)]
		response = opener.open(url, timeout=40)
		content = response.read()
		if response.headers.get('Content-Encoding', '') == 'gzip':
			if sys.version_info[0] < 3:
				content = gzip.GzipFile(fileobj=io.BytesIO(content)).read()
			else:
				content = gzip.GzipFile(fileobj=io.BytesIO(content)).read().decode('utf-8')
	except Exception as e:
		failure = str(e)
		if hasattr(e, 'code'):
			log_Special("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
		elif hasattr(e, 'reason'):
			log_Special("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
		content =""
	opener.close()
	cj.save(cookie,ignore_discard=True, ignore_expires=True)
	return content

def index():
	addDir("Übersicht", baseURL+"mediathek", "listCategories", icon)
	addDir("Eigenproduktionen", baseURL+"mediathek/eigenproduktionen", "listCategories", icon)
	addDir("Serien", baseURL+"mediathek/serien-online", "listCategories", icon)
	addDir("Spielfilme", baseURL+"mediathek/filme-online", "listCategories", icon)
	#addDir("Lucha Undergroud", baseURL+"/videos/lucha-underground", "listCategories", icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def listCategories(url, type="listCategories"):
	debug("listCategories URL :"+url)
	starturl = url
	content = getUrl(url)
	anz=0
	if "ce_teaserelemen" in content:
		part2 = content.split('ce_teaserelemen')
		for i in range(1, len(part2), 1):
			entry = part2[i]
			try:
				url = re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
				if url[:4] != "http":
					url = baseURL+url
				try:
					title = re.compile('<h2>(.+?)</h2>', re.DOTALL).findall(entry)[0]
					title = cleanTitle(title)
				except: title =""
				try:
					subtitle = re.compile('<span class="shortdesc">(.+?)</span>', re.DOTALL).findall(entry)[0]
					subtitle = cleanTitle(subtitle)
				except: subtitle =""
				if title =="":
					title = subtitle
				if subtitle !="" and title != subtitle:
					title = title+" - "+subtitle
				try:
					thumb = re.compile('source srcset="(.+?)" sizes="1200w" media=', re.DOTALL).findall(entry)[0]
					if "," in thumb:
						thumb = thumb.split(',')[1].strip()
				except: thumb = ""
				debug("listCategories newUrl :"+url)
				debug("listCategories type :"+type)
				try: idd = re.compile(r'\?(?:vid=|v=)(.+)', re.DOTALL).findall(url)[0]
				except: idd = ""
				if not "filme-online" in starturl and not '<span class="broadcast">' in entry and idd == "":
					addDir(title, url, type, baseURL+thumb)
				elif idd != "":
					addLink(title, idd, "playVideo", baseURL+thumb)
				anz=anz+1
			except:
				log_Special("(listCategories) Fehler-Eintrag-01 : {0}".format(str(entry)))
	if 'class="scrollable"' in content:
		content1 = content[content.find('ce_tele5slider')+1:]
		content1 = content1[:content1.find('</ul>')]
		part1 = content1.split('class="scrollable"')
		for i in range(1, len(part1), 1):
			element = part1[i]
			try:
				url = re.compile('href="(.+?)"', re.DOTALL).findall(element)[0]
				if url[:4] != "http":
					url = baseURL+url
				title = re.compile('<h1>(.+?)</h1>', re.DOTALL).findall(element)[0]
				title = cleanTitle(title)
				thumb = re.compile('<img src="(assets/.+?)"', re.DOTALL).findall(element)[0]
				if "," in thumb:
					thumb = thumb.split(',')[1].strip()
				try: idd = re.compile(r'\?(?:vid=|v=)(.+)', re.DOTALL).findall(url)[0]
				except: idd = ""
				if not "filme-online" in starturl and not '<span class="broadcast">' in element and idd == "":
					addDir(title, url, type, baseURL+thumb)
				elif idd != "":
					addLink(title, idd, "playVideo", baseURL+thumb)
				anz=anz+1
			except:
				log_Special("(listCategories) Fehler-Eintrag-02 : {0}".format(str(entry)))
	listVideos(starturl)
	xbmcplugin.endOfDirectory(pluginhandle)

def listVideos(url):
	debug("listVideos URL :"+url)
	content = getUrl(url)
	#http://tele5.flowcenter.de/gg/play/l/17:pid=vplayer_1560&tt=1&se=1&rpl=1&ssd=1&ssp=1&sst=1&lbt=1&
	#<div class="fwlist" lid="14" pid="vplayer_3780" tt="1" ssp="1" sst="1" lbt="1" ></div>		</div>
	y=0
	try:
		debug("1.")
		divtag = re.compile('(<div class="fwlist".+?>)', re.DOTALL).findall(content)[0]
		debug("DIVTAG :"+divtag)
		lid = re.compile('lid="(.+?)"', re.DOTALL).findall(divtag)[0]
		debug("LID :"+lid)
		all = re.compile('([^ =]+?)="(.+?)"', re.DOTALL).findall(divtag)
		url = "https://tele5.flowcenter.de/gg/play/l/"+lid+":"
		for type, inhalt in all:
			if type !="lid":
				url = url+type+"="+inhalt
				#url = "http://tele5.flowcenter.de/gg/play/l/"+lid+":pid="+ pid +"&tt="+ tt +"&se="+ se +"&rpl="+ rpl +"&ssd="+ ssd +"&ssp="+ ssp +"&sst="+ sst +"&lbt="+lbt +"&"
		debug("URL :"+url)
	except:
		y=1
		debug("2.")
		htmlPage = BeautifulSoup(content, 'html.parser')
		debug("2a")
		searchitems = htmlPage.findAll("div",{"class" :"ce_area"})
		if len(searchitems) <= 0:
			debug("2a+")
			searchitems = htmlPage.findAll("div",{"class" :"ce_videoelement first block"})
			debug("+")
			debug("2b")
			for searchitem in searchitems: 
				debug("2c")
				debug(str(searchitem))
				try:
					cid = searchitem.find("div",{"class":"fwplayer"})["cid"]
					debug(":::XX:::"+cid)
					title =""
					try:
						debug("3a")
						title = searchitem.h3.string
						title = cleanTitle(title)
						utitle = searchitem.p.string
						utitle = cleanTitle(utitle)
					except:
						debug("3b")
						debug(title+"###")
						if title =="":
							debug("3c")
							contentn = getUrl("https://tele5.flowcenter.de/gg/play/p/"+cid)
							title = re.compile('"title":"(.+?)"', re.DOTALL).findall(contentn)[0]
							title = cleanTitle(title)
							debug("Title :"+title)
							utitle =""
						else:
							debug("3d")
							utitle =""
					if utitle !="" and utitle != title:
						title = title+" - "+utitle
					debug(title)
					img = searchitem.find('img')['src']
					if img[:4] != "http":
						img = baseURL+img
					debug(img)
					addLink(title, str(cid), 'playVideo', img)    
				except: pass
	if y==0:
		debug("3.")
		debug("NEWURL :"+url)
		content = getUrl(url)
		debug("##########")
		content = re.compile('\{"id"(.+)\},', re.DOTALL).findall(content)[0]
		content = '{"id"'+content+"}"
		debug("CONTENT")
		debug(content)
		struktur = json.loads(content) 
		elements = struktur["entries"]
		for element in elements:
			try:
				season = element["staffel"]
				episode = element["folge"]
				utitle = cleanTitle(element["utitel"])
				title = cleanTitle(element["title"])
				id = element["id"]
				last = element["vodate"]
				genre = element["welt"]
				image = element["image"].replace("\/","/")
				if episode =="0":
					name = title
				else:
					name = "Folge "+str(episode)
				if utitle !="" and utitle != name:
					name = name+" - "+utitle
				addLink(name, str(id), 'playVideo', image, last=last, genre=genre, episode=episode, season=season)
			except:
				log_Special("(listVideos) Fehler-Eintrag-03 : {0}".format(str(element)))
			#addLink("Folge :"+ episode , str(id), 'playVideo', image) 
			# addLink(h.unescape(title[i]), url, 'playVideo', thumb[i]) 
	xbmcplugin.endOfDirectory(pluginhandle)

def playVideo(url):
	debug("playVideo URL :"+url)
	stream_url = None
	try:
		content = getUrl("https://tele5.flowcenter.de/gg/play/p/"+url+":mobile=0&nsrc="+url+"&" )
		file = re.compile('"file":"(.+?)"', re.DOTALL).findall(content)[-2].replace("\/","/")
		result = getUrl(file)
		try:
			mpeg = re.compile(b'<BaseURL>(.+?)</BaseURL>').findall(result)[-1]
			stream_url = file.replace("manifest.mpd", mpeg.decode('utf-8'))
			debug("MPEG-stream-bytes : "+stream_url)
		except:
			mpeg = re.compile('<BaseURL>(.+?)</BaseURL>').findall(result)[-1]
			stream_url = file.replace("manifest.mpd", mpeg)
			debug("MPEG-stream-string : "+stream_url)
	except:
		try:
			result = json.loads(getUrl('https://arc.nexx.cloud/api/video/'+url+'.json'))
			secret = ""
			if result['result']['protectiondata']['token'] != "":
				secret = '?hdnts=' + j['result']['protectiondata']['token']
			if "tokenHLS" in result['result']['protectiondata'] and result['result']['protectiondata']['tokenHLS'] != "":
				secretHLS = "?hdnts=" + result['result']['protectiondata']['tokenHLS']
			else:
				secretHLS = secret
			HLS = "https://"+result['result']['streamdata']['cdnShieldHTTP']+result['result']['streamdata']['azureLocator']+"/"+str(result['result']['general']['ID'])+"_src.ism/Manifest(format=m3u8-aapl)"+secretHLS
			stream_url = HLS
			debug("HLS-stream : "+stream_url)
		except: log_Special("(playVideo) ##### Abspielen des Videos NICHT möglich - VideoCode : {0} - #####\n    ########## KEINEN Eintrag für NeXX-Player gefunden !!! ##########".format(url))
	listitem = xbmcgui.ListItem(path=stream_url)
	xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def cleanTitle(title):
	if sys.version_info[0] < 3:
		if isinstance(title, unicode):
			title = title.encode('utf-8')
	title = title.replace('\\', '').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&#39;', '\'').replace('&#039;', '\'').replace('&quot;', '"').replace('&szlig;', 'ß').replace('&ndash;', '-').replace('#', '')
	title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
	title = title.replace("u00C4", "Ä").replace("u00c4", "Ä").replace("u00E4", "ä").replace("u00e4", "ä").replace("u00D6", "Ö").replace("u00d6", "Ö").replace("u00F6", "ö").replace("u00f6", "ö")
	title = title.replace("u00DC", "Ü").replace("u00dc", "Ü").replace("u00FC", "ü").replace("u00fc", "ü").replace("u00DF", "ß").replace("u00df", "ß").replace("u0026", "&")
	title = title.replace("u00A0", "' '").replace("u00a0", "' '").replace("u003C", "<").replace("u003c", "<").replace("u003E", ">").replace("u003e", ">")
	title = title.replace("u20AC", "€").replace("u20ac", "€").replace("u0024", "$").replace("u00A3", "£").replace("u00a3", "£")
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

def addVideoList(url, name, iconimage):
	PL = xbmc.PlayList(1)
	listitem = xbmcgui.ListItem(name, thumbnailImage=iconimage)
	listitem.setInfo(type="Video", infoLabels={"Title": name, "Studio": "Tele5", "mediatype": "video"})
	if iconimage != icon:
		listitem.setArt({'fanart': iconimage})
	else:
		listitem.setArt({'fanart': defaultFanart})
	listitem.setProperty('IsPlayable', 'true')
	listitem.setContentLookup(False)
	PL.add(url, listitem)

def addLink(name, url, mode, iconimage, plot=None, duration=None, count=0, last=0, genre=None, episode=0, season=0):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&count="+str(count)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Duration": duration ,"Lastplayed": last, "Genre": genre, "Episode": episode, "Season": season, "mediatype": "video"})
	if iconimage != icon:
		liz.setArt({'fanart': iconimage})
	else:
		liz.setArt({'fanart': defaultFanart})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	liz.addContextMenuItems([(translation(30205), 'RunPlugin(plugin://{0}?mode=addVideoList&url={1}&name={2}&iconimage={3})'.format(addon.getAddonInfo('id'), quote_plus(u), quote_plus(name), quote_plus(iconimage)))])
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

def addDir(name, url, mode, iconimage, plot=None, duration=None):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Duration": duration})
	if iconimage != icon:
		liz.setArt({'fanart': iconimage})
	else:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
iconimage = unquote_plus(params.get('iconimage', ''))
count  = unquote_plus(params.get('count', ''))
referer = unquote_plus(params.get('referer', ''))

if mode == 'listCategories':
	listCategories(url)
elif mode == 'listVideos':
	listVideos(url)
elif mode == 'playVideo':
	playVideo(url)
elif mode == 'addVideoList':
	addVideoList(url, name, iconimage)
else:
	index()