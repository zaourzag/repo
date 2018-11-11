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
main_url = sys.argv[0]
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
seventv_favorites = xbmc.translatePath(os.path.join(dataPath, 'seventv_favorites', '')).encode('utf-8').decode('utf-8')
temp        = xbmc.translatePath(os.path.join(dataPath, 'temp', '')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg')
icon = os.path.join(addonPath, 'icon.png')
stationpic = os.path.join(addonPath, 'resources', 'media', 'channels', '')
letterpic = os.path.join(addonPath, 'resources', 'media', 'letters', '')
masterOLD = "favorit.txt"
masterNEW = "favorit.txt"
source = os.path.join(temp, masterOLD)
favdatei = os.path.join(seventv_favorites, masterNEW)
baseURL = "https://www.7tv.de"

xbmcplugin.setContent(pluginhandle, 'tvshows')

if not xbmcvfs.exists(seventv_favorites):
	xbmcvfs.mkdirs(seventv_favorites)

if xbmcvfs.exists(source):
	xbmcvfs.copy(source, favdatei)

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
	global cj
	for cook in cj:
		debug("(getUrl) Cookie : {0}".format(str(cook)))
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

def index():
	addDir("Sender", "Sender", 'senderlist', "")
	addDir("Sendungen A-Z", url+"/ganze-folgen", "sendungsmenu", "")
	addDir("Sendungen nach Datum", "", "verpasstdatum", "")
	addDir("Suche ...","","search","")
	addDir("* Meine 7TV-Favoriten *", "Favoriten", 'listfav', "")
	addDir("7TV Einstellungen", "", 'aSettings', "")
	xbmcplugin.endOfDirectory(pluginhandle)

def senderlist():
	content = getUrl(baseURL) 
	result = content[content.find('<ul class="site-nav-submenu">')+1:]
	result = result[:result.find('</nav>')]
	match = re.compile('<a href="([^"]+)" [^>]+>([^<]+)</a>', re.DOTALL).findall(result)
	for id, name in match:
		url2 = baseURL+id
		debug("(senderlist) URL2 : {0}".format(str(url2)))
		addDir(name, url2, "sender", stationpic+name.lower().replace('.','').replace(' ','')+".png")
	xbmcplugin.endOfDirectory(pluginhandle)

def sender(url):
	addDir("Beliebte Sendungen", url, "belibtesendungen", "")
	addDir("Aktuelle Ganze Folgen", url, "ganzefolgensender", "")
	xbmcplugin.endOfDirectory(pluginhandle)

def belibtesendungen(url):
	content = getUrl(url) 
	result = content[content.find('<h3 class="row-headline">Beliebte Sendungen</h3>')+1:]
	result = result[:result.find('<div class="row ">')]
	spl = result.split('<article class')
	for i in range(1,len(spl),1):
		entry = spl[i]
		try:
			debug("(belibtesendungen) ENTRY : {0}".format(str(entry)))
			url2 = baseURL+re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
			photo = re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0].replace('-teaser300x160', '-teaser940x516')
			title = url2.split('/')[-1].replace('-', ' ').title().replace('Ae', 'Ä').replace('ae', 'ä').replace('Oe', 'Ö').replace('oe', 'ö').replace('Ue', 'Ü').replace('ichäl', 'ichael')
			#title=re.compile('teaser-formatname">(.+?)<', re.DOTALL).findall(entry)[0]
			addDir(title, url2, "serie", photo, bild=photo, title=title)
		except: pass
	xbmcplugin.endOfDirectory(pluginhandle)

def ganzefolgensender(url):
	content = getUrl(url) 
	result = content[content.find('</h3>')+1:]
	result = result[:result.find('<h3 class="row-headline">Ihre Favoriten</h3>')]
	spl = result.split('<article class')
	for i in range(1,len(spl),1):
		entry = spl[i]
		try:
			if "class-clip" in entry:
				debug("(ganzefolgensender) ENTRY : {0}".format(str(entry)))
				urlt = re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
				photo = re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0].replace('-teaser300x160', '-teaser940x516')
				series = re.compile('<h4 class="teaser-formatname">(.+?)</h4>', re.DOTALL).findall(entry)[0]
				folge = re.compile('<h5 class="teaser-title">(.+?)</h5>', re.DOTALL).findall(entry)[0]
				try:
					teaser = re.compile('<p class="teaser-info">(.+?)</p>', re.DOTALL).findall(entry)[0]
					if not "Min." in teaser:
						aired = teaser
						duration =0
					else:
						aired =""
						laenge = re.compile('([0-9]+):([0-9]+) Min.', re.DOTALL).findall(teaser)
						duration = laenge[0][0]*60+laenge[0][1]
				except:
					aired =""
					duration =0
				try: staffel = re.compile('Staffel ([0-9]+)', re.DOTALL).findall(folge)[0]
				except: staffel =-1
				try: episode = re.compile('Episode ([0-9]+)', re.DOTALL).findall(folge)[0]
				except: episode =-1
				title = series.strip()+" - "+folge.strip()
				url2 = baseURL+urlt
				addLink(title, url2, "getvideoid", photo, duration=duration, staffel=staffel, episode=episode, serie=series, aired=aired)
		except: pass
	xbmcplugin.endOfDirectory(pluginhandle)

def favadd(url, title, bild):
	debug("(favadd) URL : {0}".format(url))
	textfile = url.strip()+"###"+title.strip()+"###"+bild.strip()+"\n"
	try:
		f = open(favdatei, 'r')
		for line in f:
			textfile = textfile+line
		f.close()
	except: pass
	f = open(favdatei, 'w')
	f.write(textfile)
	f.close()
	xbmcgui.Dialog().notification('7TV - Favoriten :', '[COLOR green]Serie * [/COLOR][COLOR blue]'+title.strip()+'[/COLOR][COLOR green] * hinzugefügt ![/COLOR]', icon, 8000)
	xbmc.executebuiltin("Container.Refresh")

def favdel(url):
	debug("(favdel) URL : {0}".format(url))
	textfile =""
	f = open(favdatei, 'r')
	for line in f:
		if not url in line and not line =="\n":
			textfile = textfile+line
	f.close()
	f = open(favdatei, 'w')
	f.write(textfile)
	f.close()
	xbmcgui.Dialog().notification('7TV - Favoriten :', '[COLOR red]! SERIE aus Favoriten entfernt ![/COLOR]', icon, 6000)
	xbmc.executebuiltin("Container.Refresh")  

def listfav():
	xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
	if xbmcvfs.exists(favdatei):
		f = open(favdatei, 'r')
		for line in f:
			spl = line.split('###')
			addDir(name=spl[1], url=spl[0], mode="serie", iconimage=spl[2].strip(), desc="", title=spl[1], bild=spl[2].strip())
		f.close()
	xbmcplugin.endOfDirectory(pluginhandle)

def serie(url, bild="", title=""):
	debug("(serie) URL : {0}".format(url))
	debug("(serie) TITLE : {0}".format(title))
	addDir("Alle Clips", url+"/alle-clips", "listvideos", "", series=title)
	addDir("Ganze Folgen", url+"/ganze-folgen", "listvideos", "", series=title)
	found = 0
	if xbmcvfs.exists(favdatei):
		f = open(favdatei, 'r')
		for line in f:
			if url in line:
				found = 1
		f.close()
	if found == 0:
		addDir("Favoriten hinzufügen ...", url, mode="favadd", iconimage="", desc="", title=title, bild=bild)
	else:
		addDir("... Favoriten löschen", url, mode="favdel", iconimage="", desc="")
	xbmcplugin.endOfDirectory(pluginhandle)

def sendungsmenu():
	addDir("Sender", "ProSieben", "allsender", "")
	addDir("Genres", "Abenteuer", "allsender", "")
	addDir("Alle Sendungen", baseURL+"/queue/format", "abisz", "")
	xbmcplugin.endOfDirectory(pluginhandle)

def abisz(url):
	url = url.replace(" ","+")
	debug("(abisz) URL : {0}".format(url))
	content = getUrl(url)
	struktur = json.loads(content)
	debug("(abisz) STRUKTUR : {0}".format(str(struktur)))
	for buchstabe in sorted(struktur["facet"], key=lambda str: (str=="#", str)):
		if buchstabe =="#":
			ubuchstabe ="0-9"
		else:
			ubuchstabe = buchstabe
		addDir(buchstabe.title(), url+"/(letter)/"+ubuchstabe.encode("utf-8"), "jsonfile", letterpic+ubuchstabe.title()+".jpg")
	xbmcplugin.endOfDirectory(pluginhandle)

def jsonfile(url):
	debug("(jsonfile) URL : {0}".format(url))
	content = getUrl(url)
	struktur = json.loads(content)
	for element in struktur["entries"]:
		url2 = baseURL+"/"+element["url"]
		photo = element["images"][0]["url"].replace('-teaser300x160', '-teaser940x516')
		title = element["title"]
		addDir(title, url2, "serie", photo, bild=photo, title=title)
	xbmcplugin.endOfDirectory(pluginhandle)

def allsender(begriff):
	debug("(allsender) BEGRIFF : {0}".format(begriff))
	url ="https://www.7tv.de/sendungen-a-z"    
	content = getUrl(url) 
	result = content[content.find('<nav class="tvshow-nav">')+1:]
	result = result[:result.find('</nav>')]  
	debug("(allsender) INHALT : {0}".format(str(result)))
	spl = result.split('<ul class="tvshow-filter">')
	for i in range(1,len(spl),1):   
		entry = spl[i]
		debug("(allsender) ENTRY : {0}".format(str(entry)))
		if not begriff.lower() in entry.lower():
			continue
		filter = re.compile('<a href="#tvshow-all" data-href="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
		for urlt, name in filter:
			url2 = baseURL+urlt
			addDir(name, url2, "abisz", stationpic+name.lower().replace('.','').replace(' ','')+".png")
	xbmcplugin.endOfDirectory(pluginhandle)

def listvideos(url, series=""):
	datetitle = addon.getSetting("datetitle")=="true"
	content = getUrl(url) 
	result = content[content.find('<div class="main-zone">')+1:]
	result = result[:result.find('<!--googleoff: index-->')]
	home = re.findall('<section class="notification-board">(.*?)</section>', result, re.DOTALL)
	if home and 'Derzeit nicht verfügbar' in home[0]:
		return xbmcgui.Dialog().notification('[COLOR red]Zurzeit KEINE Videos von :[/COLOR]', '* [COLOR blue]'+series+'[/COLOR] * in der 7TV-Mediathek', icon, 8000)
	else:
		part = result.split('<article class')
		for i in range(1, len(part), 1):
			element = part[i]
			try:
				debug("(listvideos) ELEMENT : {0}".format(str(element)))
				url2 = re.compile('href="([^"]+?)"', re.DOTALL).findall(element)[0]
				photo = re.compile('data-src="([^"]+?)"', re.DOTALL).findall(element)[0].replace('-teaser300x160', '-teaser940x516').replace('-teaser620x348', '-teaser940x516')
				title = re.compile('teaser-title">(.+?)</h5>', re.DOTALL).findall(element)[0]
				try:
					teaser = re.compile('<p class="teaser-info">(.+?)</p>', re.DOTALL).findall(element)[0]        
					if not "Min." in teaser:
						aired = teaser
						duration =0
						if datetitle:
							title = aired+" • "+title
					else:
						aired =""
						laenge = re.compile('([0-9]+):([0-9]+) Min.', re.DOTALL).findall(teaser)
						duration = int(laenge[0][0])*60+int(laenge[0][1])
				except:
					aired =""
					duration = 0
				try: staffel = re.compile('Staffel ([0-9]+)', re.DOTALL).findall(title)[0]
				except: staffel =-1
				try: episode = re.compile('Episode ([0-9]+)', re.DOTALL).findall(title)[0]
				except: episode =-1 
				if url2[:4] != "http":
					url2 = baseURL+url2
				addLink(title, url2, "getvideoid", photo, duration=duration, staffel=staffel, episode=episode, serie=series, aired=aired)
			except: pass
		if "data-ajax-more=" in content:
			nexturl = baseURL+re.compile('data-ajax-more="([^"]+?)"', re.DOTALL).findall(content)[0]
			addDir("[COLOR chartreuse]Nächste Seite  >>>[/COLOR]", nexturl, "listvideos", "", series="")
	xbmcplugin.endOfDirectory(pluginhandle)

def getvideoid(client_location):
	debug("(getvideoid) CLIENT_LOCATION : {0}".format(client_location))
	content = getUrl(client_location)
	try: video_id=re.compile(',"cid":(.*?),', re.DOTALL).findall(content)[0]  
	except: video_id=re.compile(',"clipId":"(.*?)",', re.DOTALL).findall(content)[0]  
	source_id = None
	videos = playvideo(video_id, client_location,  source_id)

def playvideo(video_id, client_location, source_id=None):
	from hashlib import sha1
	adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.GetAddonDetails", "params": {"addonid":"inputstream.adaptive", "properties": ["enabled"]}, "id":1}')
	struktur = json.loads(adaptivaddon) 
	debug("(playvideo) ADAPITIVADDON_STRUKTUR : {0}".format(str(struktur)))
	INPUTSTREAM =""
	if not "error" in struktur.keys() :	    
		if struktur["result"]["addon"]["enabled"]==True:
			INPUTSTREAM = "inputstream.adaptive"
	if INPUTSTREAM =="":
		access_token = 'h''b''b''t''v'  
		salt = '0''1''r''e''e''6''e''L''e''i''w''i''u''m''i''e''7''i''e''V''8''p''a''h''g''e''i''T''u''i''3''B'
		client_name='h''b''b''t''v'
	else:
		access_token = 'seventv-web'  
		salt = '01!8d8F_)r9]4s[qeuXfP%'
		client_name =""
	if source_id is None:
		source_id=0 
		js_URL1 = getUrl('http://vas.sim-technik.de/vas/live/v2/videos/%s?access_token=%s&client_location=%s&client_name=%s' % (video_id, access_token, client_location, client_name))
		js1 = json.loads(js_URL1)
		if INPUTSTREAM !="":
			if int(xbmc.getInfoLabel('System.BuildVersion')[:2]) < 18 and js1["is_protected"]==True:
				return xbmcgui.Dialog().notification('7TV : [COLOR red]!!! KODIVERSION - ERROR !!![/COLOR]', 'ERROR = [COLOR red]Für DRM geschützte Folgen ist mindestens KODI-18 erforderlich ![/COLOR]', icon, 18000)
			else:
				for stream in js1['sources']:
					if  stream['mimetype']=='application/dash+xml': 
						if int(source_id) <  int(stream['id']):
							source_id = stream['id']
		else:
			if js1["is_protected"]==True:
				return xbmcgui.Dialog().notification('7TV : [COLOR red]!!! INPUTSTREAM - ERROR !!![/COLOR]', 'ERROR = [COLOR red]Es liegt ein Fehler bei "inputstream.adaptive" vor ![/COLOR]', icon, 15000)
			else:
				for stream in js1['sources']:
					if stream['mimetype']=='video/mp4':
						if int(source_id) <  int(stream['id']):
							source_id = stream['id']
	client_id_1 = salt[:2] + sha1(''.join([str(video_id), salt, access_token, client_location, salt, client_name]).encode('utf-8')).hexdigest()
	js_URL2 = getUrl('http://vas.sim-technik.de/vas/live/v2/videos/%s/sources?access_token=%s&client_location=%s&client_name=%s&client_id=%s' % (video_id, access_token, client_location, client_name, client_id_1))
	js2 = json.loads(js_URL2)
	server_id = js2['server_id']
	client_id = salt[:2] + sha1(''.join([salt, video_id, access_token, server_id,client_location, str(source_id), salt, client_name]).encode('utf-8')).hexdigest()
	js_URL3 = getUrl('http://vas.sim-technik.de/vas/live/v2/videos/%s/sources/url?%s' %(video_id, urlencode({'access_token': access_token,'client_id': client_id,'client_location': client_location,'client_name': client_name,'server_id': server_id,'source_ids': str(source_id)})))
	js3 = json.loads(js_URL3)
	max_id = 0
	active = js3['status_code']
	if active != 0:
		return xbmcgui.Dialog().notification('7TV : [COLOR red]!!! VIDEO - ERROR !!![/COLOR]', 'ERROR = [COLOR red]Der angeforderte Stream ist NICHT verfügbar ![/COLOR]', icon, 12000)
	for stream in js3["sources"]:
		ul = stream["url"]
		try:
			sid = re.compile('-tp([0-9]+).mp4', re.DOTALL).findall(ul)[0]
			id = int(sid)
			if max_id < id:
				max_id = id
				data = ul
		except: data = ul
	userAgent = 'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
	listitem = xbmcgui.ListItem(path=data+"|"+userAgent)
	listitem.setProperty(INPUTSTREAM+".license_type", "com.widevine.alpha")
	listitem.setProperty(INPUTSTREAM+".manifest_type", "mpd")
	listitem.setProperty('inputstreamaddon', INPUTSTREAM)
	try:
		lic = js3["drm"]["licenseAcquisitionUrl"]
		token = js3["drm"]["token"]
		listitem.setProperty(INPUTSTREAM+'.license_key', lic +"?token="+token+"|"+userAgent+"|R{SSM}|")
	except: pass
	xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def verpasstdatum():
	#http://www.7tv.de/missedshows/data/20161215
	d = xbmcgui.Dialog().input('Datum', type=xbmcgui.INPUT_DATE)
	d = d.replace(' ','0')
	d = d[6:]+d[3:5]+d[:2]
	return verpasstdatummenu(d)

def verpasstdatummenu(d):
	url = baseURL+"/missedshows/data/"+d
	content = getUrl(url)
	json_data = json.loads(content) 
	for sendername in json_data["entries"]:
		debug("(verpasstdatummenu) SENDERNAME : {0}".format(str(sendername)))
		addDir(sendername, url, "listdatum", "", sendername=sendername)
	xbmcplugin.endOfDirectory(pluginhandle)

def listdatum(url, sendername):
	debug("(listdatum) URL : {0}".format(url))
	debug("(listdatum) SENDERNAME : {0}".format(sendername))
	EMPTY = True
	content = getUrl(url)
	json_data = json.loads(content) 
	senderliste = json_data["entries"][sendername]
	for element in senderliste:
		if 'title' in element and element["title"] != "":
			EMPTY = False
			title = element["title"]
			try: staffel = re.compile('Staffel ([0-9]+)', re.DOTALL).findall(title)[0]
			except: staffel =-1
			try: episode = re.compile('Episode ([0-9]+)', re.DOTALL).findall(title)[0]
			except: episode =-1
			url2 = element["url"]
			if url2[:1] != "/":
				url2 = baseURL+'/'+url2
			elif url2[:1] == "/":
				url2 = baseURL+url2
			duration = int(element["duration"])/1000
			series = element["metadata"]["tvShowTitle"]
			time = element["airtime"]
			name ="[COLOR orangered]"+time+"[/COLOR]  "+series+" - "+title
			addLink(name, url2, "getvideoid", "", duration=duration, staffel=staffel, episode=episode, serie=series)
	if EMPTY:
		return xbmcgui.Dialog().notification('[COLOR red]KEINE Einträge für das Datum auf :[/COLOR]', '* [COLOR blue]'+sendername+'[/COLOR] * in der 7TV-Mediathek', icon, 8000)
	xbmcplugin.endOfDirectory(pluginhandle)

def search():
	d = xbmcgui.Dialog().input('Suche', type=xbmcgui.INPUT_ALPHANUM)
	d = d.replace(" ","+")
	return searchmenu(d)

def searchmenu(d):
	#/type/episode/offset/1/limit/5
	d = d.replace(" ","+")
	addDir("Serien", url=baseURL+"/7tvsearch/search/query/"+d, mode="searchtext", iconimage="", offset=0, limit=5, type="format")
	addDir("Clips", url=baseURL+"/7tvsearch/search/query/"+d, mode="searchtext", iconimage="", offset=0, limit=5, type="clip")
	addDir("Ganze Folgen", url=baseURL+"/7tvsearch/search/query/"+d, mode="searchtext", iconimage="", offset=0, limit=5, type="episode")
	xbmcplugin.endOfDirectory(pluginhandle)

def searchtext(url, offset, limit, type): 
	debug("Type :"+type) 
	urlx = url+"/type/"+type+"/offset/"+offset+"/limit/"+limit
	debug("(searchtext) URL-x : {0}".format(str(urlx)))
	content = getUrl(urlx)
	spl = content.split('<article class')
	try:
		for i in range(1,len(spl),1):
			entry = spl[i]  
			url2 = baseURL+re.compile('href="([^"]+?)"', re.DOTALL).findall(entry)[0]
			photo = re.compile('data-src="([^"]+?)"', re.DOTALL).findall(entry)[0].replace('-teaser300x160', '-teaser940x516').replace('-teaser620x348', '-teaser940x516')
			title = re.compile('title="([^"]+?)"', re.DOTALL).findall(entry)[0].replace('&quot;', '"').replace('&amp;', '&')
			if title == 'Sendung' or title =="":
				title = url2.split('/')[-1].replace('-', ' ').title().replace('Ae', 'Ä').replace('ae', 'ä').replace('Oe', 'Ö').replace('oe', 'ö').replace('Ue', 'Ü').replace('ichäl', 'ichael')
			if type=="format":
				addDir(title, url2, "serie", photo, bild=photo, title=title)
			else:
				addLink(title, url2, "getvideoid", photo) 
		if i > 5:
			addDir("[COLOR chartreuse]Nächste Seite  >>>[/COLOR]", url, mode="searchtext", iconimage="", offset=str(int(offset)+7), limit=limit, type=type)
	except: pass
	xbmcplugin.endOfDirectory(pluginhandle)

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def addDir(name, url, mode, iconimage, desc="", sendername="", offset="", limit="", type="", bild="", title="", series=""):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&sendername="+str(sendername)+"&offset="+str(offset)+"&limit="+str(limit)+"&type="+str(type)+"&iconimage="+bild+"&title="+title+"&series="+series
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	if iconimage != icon and '940x516' in iconimage:
		liz.setArt({'fanart': iconimage})
	else:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

def addLink(name, url, mode, iconimage, duration="", desc="", genre="", staffel=-1, episode=-1, serie="", aired=None):
	u = sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Duration": duration, "Plot": desc, "Genre": genre, "Season": staffel, "Episode": episode, "TVShowTitle": serie, "Aired": aired, "Studio": "7TV.de", "mediatype": "episode"})
 	if iconimage != icon:
		liz.setArt({'fanart': iconimage})
	else:
		liz.setArt({'fanart': defaultFanart})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

params = parameters_string_to_dict(sys.argv[2])
mode = unquote_plus(params.get('mode', ''))
url = unquote_plus(params.get('url', ''))
sendername = unquote_plus(params.get('sendername', ''))
offset = unquote_plus(params.get('offset', ''))
limit = unquote_plus(params.get('limit', ''))
type = unquote_plus(params.get('type', ''))
title = unquote_plus(params.get('title', ''))
bild = unquote_plus(params.get('iconimage', ''))
series = unquote_plus(params.get('series', ''))

if mode == 'aSettings':
	addon.openSettings()
elif mode == 'senderlist':
	senderlist()
elif mode == 'sender':
	sender(url)
elif mode == 'belibtesendungen':
	belibtesendungen(url)
elif mode == 'serie':
	serie(url, bild, title)
elif mode == 'listvideos':
	listvideos(url, series)
elif mode == 'getvideoid':
	getvideoid(url)
elif mode == 'ganzefolgensender':
	ganzefolgensender(url)
elif mode == 'sendungsmenu':
	sendungsmenu()
elif mode == 'allsender':
	allsender(url)
elif mode == 'abisz':
	abisz(url)
elif mode == 'jsonfile':
	jsonfile(url)
elif mode == 'verpasstdatum':
	verpasstdatum()
elif mode == 'listdatum':
	listdatum(url, sendername)
elif mode == 'search':
	search()
elif mode ==  'searchtext':
	searchtext(url, offset, limit, type)
elif mode ==  'searchmenu':
	searchmenu(url)
elif mode ==  'verpasstdatummenu':
	verpasstdatummenu(url)
elif mode == 'favadd': 
	favadd(url, title, bild)
elif mode == 'favdel':
	favdel(url)
elif mode == 'listfav':
	listfav()
else:
	index()