#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil, json
import time
import base64
from datetime import datetime, timedelta

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString

xbmcplugin.setContent(addon_handle, 'movies')

baseurl="http://www.filmstarts.de"
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)

addonPath = xbmc.translatePath(addon.getAddonInfo('path')).decode("utf-8")
icon = os.path.join(addonPath, 'icon.png')
fanart = os.path.join(addonPath, 'fanart.jpg')
pic = os.path.join(addonPath, 'resources/media/')
bitrate=addon.getSetting("bitrate")

profile    = xbmc.translatePath(addon.getAddonInfo('profile')).decode("utf-8")
temp       = xbmc.translatePath(os.path.join(profile, 'temp', '')).decode("utf-8")

try:
	if xbmcvfs.exists(temp):
		shutil.rmtree(temp)
except: pass
xbmcvfs.mkdirs(temp)
cookie=os.path.join( temp, 'cookie.jar')
cj = cookielib.LWPCookieJar();

if xbmcvfs.exists(cookie):
	cj.load(cookie,ignore_discard=True, ignore_expires=True)                  

def debug(content):
	log(content, xbmc.LOGDEBUG)

def notice(content):
	log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
	addon = xbmcaddon.Addon()
	addonID = addon.getAddonInfo('id')
	xbmc.log('%s: %s' % (addonID, msg), level) 

def ersetze(inhalt):
	inhalt=inhalt.replace("&#39;", "'").replace("&#039;", "'")
	inhalt=inhalt.replace("&rsquo;", "’").replace("&lsquo;", "‘").replace("&sbquo;", "’")
	inhalt=inhalt.replace("&quot;", "\"").replace("&Quot;", "\"")
	inhalt=inhalt.replace("&lt;", "<").replace("&gt;", ">")
	inhalt=inhalt.replace("&amp;", "&").replace("&Amp;", "&")
	inhalt=inhalt.replace("&Auml;", "Ä").replace("&auml;", "ä")
	inhalt=inhalt.replace("&Ouml;", "Ö").replace("&ouml;", "ö")
	inhalt=inhalt.replace("&Uuml;", "Ü").replace("&uuml;", "ü")
	inhalt=inhalt.replace("&#223;","ß").replace("&szlig;", "ß")
	inhalt=inhalt.replace("&#228;", "ä")
	inhalt=inhalt.replace("&#233;", "é")
	inhalt=inhalt.replace("&#246;", "ö")
	inhalt=inhalt.replace("&#252;", "ü")
	inhalt=inhalt.replace("&#287;", "G")
	inhalt=inhalt.replace("&#304;", "i")
	inhalt=inhalt.replace("&#305;", "ı")
	inhalt=inhalt.replace("&#350;", "Ş")
	inhalt=inhalt.replace("&#351;", "ş")
	inhalt=inhalt.strip()
	return inhalt

def enlargeIMG(cover):
	debug("COVER-old :"+cover)
	try:
		if "medias" in cover:
			cover = cover.split('.net/')[0]+".net/medias"+cover.split('medias')[1]
		elif "pictures" in cover:
			cover = cover.split('.net/')[0]+".net/pictures"+cover.split('pictures')[1]
		elif "seriesposter" in cover:
			cover = cover.split('.net/')[0]+".net/seriesposter"+cover.split('seriesposter')[1]
		elif "videothumbnails" in cover:
			cover = cover.split('.net/')[0]+".net/videothumbnails"+cover.split('videothumbnails')[1]
	except:
		try:
			quelle = re.compile('(/[a-z]+_[0-9]+_[0-9]+)/', re.DOTALL).findall(cover)[0]
		except:
			quelle = "XXXXXXXXXXXXXXX"
		cover = cover.replace(quelle, '')
	debug("COVER-new : "+cover)
	return cover

def addDir(name, url, mode, iconimage, desc="", page=1, xtype="", datum=""):  
	try:
		id  = re.compile('serien/(.+?)/videos/', re.DOTALL).findall(url)[0]
		icon="http://de.web.img1.acsta.net/r_1200_1600/seriesposter/"+id+"/poster_large.jpg"
	except:
		icon=iconimage
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&xtype="+xtype+"&datum="+datum
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	liz.setArt({'fanart': fanart, 'thumb': iconimage, 'banner': icon, 'icon': icon})
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok

def addLink(name, url, mode, iconimage, duration="", desc="", genre='', director="", bewertung="", referer=""):
	debug("URL ADDLINK :"+url)
	iconimage = enlargeIMG(iconimage)
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&referer="+str(referer)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre, "Director": director, "Rating": bewertung})
	liz.addStreamInfo('video', {'duration': duration})
	liz.setArt({'fanart': fanart, 'thumb': iconimage, 'banner': icon, 'icon': icon})
	liz.setProperty('IsPlayable', 'true')
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def decodeurl(url):
	debug("URL :"+ url)
	codestring=['3F','2D','13', '1E', '19', '1F', '20', '2A', '21', '22', '2B', '23', '24', '2C', '25', '26', 'BA', 'B1', 'B2', 'BB', 'B3', 'B4', 'BC', 'B5', 'B6', 'BD', 'B7', 'B8', 'BE', 'B9', 'BF', '30', '31', '32', '3B', '33', '34', '3C', '35', '3D', '4A', '41', '42', '4B', '43', '44', '4C', '45', '46', '4D', '47', '48', '4E', '49', '4F', 'C0', 'C1', 'C2', 'CB', 'C3', 'C4', 'CC', 'C5', 'C6', 'CD']
	decodesring=['_',':','%', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
	ziel=""
	for i in range(0,len(url),2):   
		debug("##")
		zeichen=url[i:i+2]
		debug("1. Zeichen :"+zeichen)
		ind=codestring.index(zeichen)
		z=decodesring[ind]
		debug("2. Zeichen :"+z)
		ziel=ziel+z  
	debug("ziel :"+ ziel)
	return ziel

def geturl(url,data="x",header="",referer=""):
	global cj
	debug("Get Url: " +url)
	for cook in cj:
		debug(" Cookie :"+ str(cook))
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"
	if header=="":
		opener.addheaders = [('User-Agent', userAgent)]	    
	else:
		opener.addheaders = header
	if not referer=="":
		opener.addheaders = [('Referer', referer)]
	try:
		if data!="x" :
			content=opener.open(url,data=data).read()
		else:
			content=opener.open(url).read()
	except urllib2.HTTPError as e:
		#debug( e.code )  
		cc=e.read()  
		debug("Error : " +cc)
		content=""
	opener.close()
	cj.save(cookie,ignore_discard=True, ignore_expires=True)
	match = re.compile('class="(ACr[^ "]+)', re.DOTALL).findall(content)
	for gefunden in match:
		ziel=gefunden.replace("ACr","")
		print(ziel)
		ziel=base64.b64decode(ziel)
		content=content.replace(gefunden,ziel)
	return content

def trailer():
	addDir(translation(30008), baseurl+"/trailer/beliebteste.html", 'trailerpage2', icon)
	addDir(translation(30009), baseurl+"/trailer/imkino/", 'trailerpage2', icon)
	addDir(translation(30010), baseurl+"/trailer/bald/", 'trailerpage2', icon)
	addDir(translation(30011), baseurl+"/trailer/neu/", 'trailerpage2', icon)
	addDir(translation(30012), baseurl+"/trailer/archiv/", 'filterart', icon)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def kino():
	addDir(translation(30013), baseurl+"/filme-imkino/kinostart/", 'kinovideosneu', icon, datum="N")
	addDir(translation(30014), baseurl+"/filme-imkino/neu/", 'kinovideosneu', icon, datum="J")
	addDir(translation(30015), baseurl+"/filme-imkino/besten-filme/user-wertung/", 'kinovideosneu', icon, datum="N")
	addDir(translation(30016), baseurl+"/filme-imkino/kinderfilme/", 'kinovideos', icon)
	addDir(translation(30017), "", 'selectwoche', icon)
	addDir(translation(30018), baseurl+"/filme/besten/user-wertung/", 'filterkino', icon)
	addDir(translation(30019), baseurl+"/filme/schlechtesten/user-wertung/", 'filterkino', icon)
	addDir(translation(30020), baseurl+"/filme/kinderfilme/", 'filterkino', icon)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def series():
	addDir(translation(30021), baseurl+"/serien/top/", 'filterserien', icon)
	addDir(translation(30022), baseurl+"/serien/beste/", 'filterserien', icon)
	addDir(translation(30023), baseurl+"/serien/top/populaerste/", 'serienvideos', icon)
	addDir(translation(30024), baseurl+"/serien/kommende-staffeln/meisterwartete/", 'serienvideos', icon)
	addDir(translation(30025), baseurl+"/serien/neue/", 'serienvideos', icon)
	addDir(translation(30026), baseurl+"/serien/videos/neueste/", 'neuetrailer', icon, xtype="")
	addDir(translation(30027), baseurl+"/serien-archiv/", 'filterserien', icon)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def news():
	addDir(translation(30028), baseurl+"/videos/shows/funf-sterne/", 'newsvideos', icon)
	addDir(translation(30029), baseurl+"/videos/shows/filmstarts-fehlerteufel/", 'newsvideos', icon)
	addDir(translation(30030), baseurl+"/trailer/interviews/", 'newsvideos', icon)
	addDir(translation(30031), baseurl+"/videos/shows/meine-lieblings-filmszene/", 'newsvideos', icon)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def newsvideos(url,page=1):
	page=int(page)
	if page >1:
		PGurl=url+"?page="+str(page)
	else:
		PGurl=url
	content=geturl(PGurl)
	debug("newsvideos URL :"+PGurl)
	kurz_inhalt = content[content.find('<div class="colcontent">')+1:]
	kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('centeringtable')]
	elemente=kurz_inhalt.split('<div class="datablock vpadding10b">')
	for i in range(1,len(elemente),1):
		element=elemente[i]
		try:
			debug("1.")
			link = re.compile("href='(.+?)'", re.DOTALL).findall(element)[0]
			title = re.compile('</strong>([^>]+?)<', re.DOTALL).findall(element)[0]
		except:
			debug("2.")
			match = re.compile("href='(.+?)'>(.+?)</a>", re.DOTALL).findall(element)
			link=match[0][0]
			title=match[0][1]
			title=title.replace("<span class='bold'>","")
			title=title.replace("</span>","")
			title=title.replace("\n","")
			title=ersetze(title)
			debug("LINK :"+link)
			debug("title :"+title)
		img = re.compile('src=["\'](http.+?[.png\.jpg])["\'\?]', re.DOTALL).findall(element)[0]
		addLink(title, baseurl+link, 'playVideo', img, referer=url)
	try:
		xyx = re.compile('(<li class="navnextbtn">[^<]+<span class="acLnk)', re.DOTALL).findall(content)[0]        
		addDir(translation(30006), url, 'newsvideos', pic+"nextpage.png", page=page+1)
	except: pass
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      

def selectwoche(url):
	dialog = xbmcgui.Dialog()
	d = dialog.input("Wähle die Woche des KinoProgramms", type=xbmcgui.INPUT_DATE)
	d=d.replace(' ','0')  
	d= d[6:] + "-" + d[3:5] + "-" + d[:2]
	addDir(translation(30032), baseurl+"/filme-vorschau/de/?week=", 'kinovideos', icon, datum=d)
	addDir(translation(30033), baseurl+"/filme-vorschau/usa/?week=", 'kinovideos', icon, datum=d)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def filterserien(url):
	debug("filterart url :"+ url)
	if not "serien-archiv" in url:
		if not "genre-" in url:
			addDir(translation(30034), url, 'genre', icon, xtype="filterserien")
		if not "jahrzehnt" in url:
			addDir(translation(30035), url, 'jahre', icon)
		if not "produktionsland-" in url:
			addDir(translation(30036), url, 'laender', icon)
		addDir(translation(30037), url, 'serienvideos', icon)
	else:
		addDir(translation(30037), url, 'kinovideosneu', icon, datum="N")
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def filterkino(url):
	debug("filterart url :"+ url)
	if not "genre-" in url:
		addDir(translation(30034), url, 'genre', icon, xtype="filterkino")
	if not "jahrzehnt" in url:
		addDir(translation(30035), url, 'jahre', icon)
	if not "produktionsland-" in url:
		addDir(translation(30036), url, 'laender', icon)
	addDir(translation(30037), url, 'kinovideos', icon)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def filterart(url):
	debug("filterart url :"+ url)
	if not "genre-" in url:
		addDir(translation(30034), url, 'genre', icon, xtype="filterart")
	if not "sprache-" in url:        
		addDir(translation(30038), url, 'sprache', icon)
	if not "format-" in url:
		addDir(translation(30039), url, 'types', icon)
	addDir(translation(30037), url, 'archivevideos', icon)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def sprache(url):  
	content=geturl(url)
	kurz_inhalt = content[content.find('Alle Sprachen</span>')+1:]
	kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]
	match = re.compile('<span class="acLnk ([^"]+)">(.+?)</span> <span class="lighten">\((.+?)\)</span>', re.DOTALL).findall(kurz_inhalt)
	for url,name,anzahl in match:    
		url=decodeurl(url)
		addDir(name.strip()+"  ("+anzahl +")", baseurl+url, 'filterart', icon)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   

def jahre(url,type="filterserien"):
	content=geturl(url)
	debug("Jahre URL :"+url)    
	kurz_inhalt = content[content.find('Alle Jahre</span>')+1:]
	kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]
	elemente=kurz_inhalt.split('</li><li')
	for i in range(1,len(elemente),1):   
		element=elemente[i]    
		debug("-------")
		debug(element)
		try:
			match = re.compile('<span class="acLnk ([^"]+)">([^<]+?)</span> <span class="lighten">\(([^<]+?)\)</span>', re.DOTALL).findall(element)  
			url=decodeurl(match[0][0])
			name=match[0][1].strip()
			anzahl=match[0][2].strip()
			debug("Decoded :"+url)
			addDir(name+"  ("+anzahl +")", baseurl+url, type, icon)
		except:
			match = re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(element)   
			url=match[0][0]
			name=match[0][1].strip()
			addDir(name , baseurl+url, type, icon)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def neuetrailer(url,page=1):
	page=int(page)
	debug("archivevideos URL :"+url)
	if page >1:
		PGurl=url+"?page="+str(page)
	else:
		PGurl=url
	content=geturl(PGurl)
	kurz_inhalt = content[content.find('<div class="tabs_main">')+1:]
	kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<div class="pager pager margin_40t">')]
	elemente=kurz_inhalt.split('<article data-block')
	for i in range(1,len(elemente),1):  
		try:
			element=elemente[i]    
			element=element.replace('<strong>',"")
			element=element.replace('</strong>',"")
			try:
				image = re.compile('src=["\'](http.+?[.png\.jpg])["\'\?]', re.DOTALL).findall(element)[0]
			except:
				image = re.compile('["\']src["\']:["\'](http.+?[.png\.jpg])["\'\?]', re.DOTALL).findall(element)[0]
			match = re.compile('<a href="([^"]+?)">([^<]+)</a>', re.DOTALL).findall(element)    
			urlx=match[0][0]
			name=match[0][1]
			name=ersetze(name)
			debug("IMG :"+image)
			if urlx !="":
				addLink(name, baseurl+urlx, 'playVideo', image, referer=url)
		except: pass
	if 'fr">Nächste<i class="icon-arrow-right">' in content:  
		addDir(translation(30006), url, 'neuetrailer', pic+"nextpage.png", page=page+1)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  
    
def laender(url,type="filterserien"):
	content=geturl(url)
	debug("Länder URL :"+url)
	kurz_inhalt = content[content.find('Alle Länder</span>')+1:]
	kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]
	elemente=kurz_inhalt.split('</li><li')
	for i in range(1,len(elemente),1):   
		element=elemente[i]  
		element=element.replace('<strong>',"")
		element=element.replace('</strong>',"")        
		debug("-------")
		debug(element)
		try:
			match = re.compile('<span class="acLnk ([^"]+)">([^<]+?)</span> <span class="lighten">\(([^<]+?)\)</span>', re.DOTALL).findall(element)  
			url=decodeurl(match[0][0])
			name=match[0][1].strip()
			anzahl=match[0][2].strip()
			debug("Decoed :"+url)
			addDir(name+"  ("+anzahl +")", baseurl+url, type, icon)
		except:
			match = re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(element)   
			url=match[0][0]
			name=match[0][1].strip()
			addDir(name , baseurl+url, type, icon)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
def types(url):
	content=geturl(url)
	kurz_inhalt = content[content.find('Alle Formate</span>')+1:]
	kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]  
	if "<a href" in kurz_inhalt:
		match = re.compile('<a href="/trailer/archiv/(format-.+?)/">(.+?)</a> <span class="lighten">\((.+?)\)</span>', re.DOTALL).findall(kurz_inhalt)
		for urln,name,anzahl in match:
			addDir(name.strip()+"  ("+anzahl +")", baseurl+urln, 'filterart', icon)
	else:  
		match = re.compile('<span class="acLnk ([^"]+)">(.+?)</span> <span class="lighten">\((.+?)\)</span>', re.DOTALL).findall(kurz_inhalt)
		for url,name,anzahl in match:
			debug("name : "+ name)
			debug("anzahl : "+ anzahl)
			url=decodeurl(url)
			addDir(name.strip()+"  ("+anzahl+")", baseurl+url, 'filterart', icon)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
   
def genre(url,type="filterart"):
	content=geturl(url)
	debug("Genre URL :"+url)
	kurz_inhalt = content[content.find('Alle Genres</span>')+1:]
	kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]
	elemente=kurz_inhalt.split('</li><li')
	for i in range(1,len(elemente),1):   
		element=elemente[i]  
		element=element.replace('<strong>',"")
		element=element.replace('</strong>',"")        
		debug("-------")
		debug(element)
		try:
			match = re.compile('<span class="acLnk ([^"]+)">([^<]+?)</span> <span class="lighten">\(([^<]+?)\)</span>', re.DOTALL).findall(element)  
			url=decodeurl(match[0][0])
			name=match[0][1].strip()
			anzahl=match[0][2].strip()
			debug("Decoed :"+url)
			addDir(name+"  ("+anzahl +")", baseurl+url, type, icon)
		except:
			match = re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(element)   
			url=match[0][0]
			name=match[0][1].strip()
			addDir(name , baseurl+url, type, icon)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     
   
def archivevideos(url,page=1):
	page=int(page)
	debug("archivevideos URL :"+url)
	if page >1:
		PGurl=url+"?page="+str(page)
	else:
		PGurl=url
	content=geturl(PGurl)
	elemente=content.split('<article class=')
	for i in range(1,len(elemente),1):
		try:
			element=elemente[i]
			element=element.replace('<strong>',"")
			element=element.replace('</strong>',"")
			debug("-##-")
			debug(element)
			debug("-##-")
			image = re.compile('src=["\'](http.+?[.png\.jpg])["\'\?]', re.DOTALL).findall(element)[0]
			match = re.compile('<a href="(.+?)">([^<]+)</a>', re.DOTALL).findall(element)
			urlx=match[0][0]
			name=match[0][1].strip()
			if not "En savoir plus" in name:
				addLink(name, baseurl+urlx, 'playVideo', image, referer=url)
		except:
			debug("....")
			debug(element)
	if 'fr">Nächste<i class="icon-arrow-right">' in content:
		addDir(translation(30006), url, 'archivevideos', pic+"nextpage.png", page=page+1)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  
   
def kinovideosneu(url,page=1,datum="N"):   
	debug("Start kinovideosneu")   
	page=int(page)
	debug("kinovideosneu URL :"+url)
	if page >1:
		PGurl=url+"?page="+str(page)
	else:
		PGurl=url
	content=geturl(PGurl)
	kurz_inhalt = content[content.find('<ul class="list">')+1:]
	kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('id="dfp-atf" class="js-atf"')]
	elemente=kurz_inhalt.split('<figure class="thumbnail ">')
	for i in range(1,len(elemente),1):
		try:
			element=elemente[i]
			debug(element)
			image = re.compile('src=["\'](http.+?[.png\.jpg])["\'\?]', re.DOTALL).findall(element)[0]
			debug("Bild :"+image)
			urlgs = re.compile('class="([^ "]+) thumbnail-container thumbnail-link" title="(.+?)">', re.DOTALL).findall(element)
			urlg=urlgs[0][0]
			debug("urlg :"+urlg)
			name=urlgs[0][1]
			name=ersetze(name)
			debug("name :"+name)
			if not "http" in urlg:
				urlg=baseurl+urlg
			debug("URLG : "+urlg)
			try:
				desc = re.compile('<div class="synopsis">(.+?)</div>', re.DOTALL).findall(element)[0]          
				desc=ersetze(desc)
			except: desc=""
			if 'class="icon icon-left icon-play-mini"></i></span> <span class="txt">' in element:
				addLink(name, urlg, 'playVideo', image, desc=desc, referer=url)
		except:
			debug("....")
			debug(element)
	if datum=="N":
		addDir(translation(30006), url, 'kinovideosneu', pic+"nextpage.png", page=page+1, datum=datum)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   

def kinovideos(url,page=1,datum=""):
	debug("Start kinovideos")   
	page=int(page)
	debug("Page : "+ str(page))
	debug("kinovideos URL :"+url)
	if page >1:
		PGurl=url+"?page="+str(page)
	else:
		PGurl=url
	if not datum=="":
		PGurl=PGurl+datum
	content=geturl(PGurl)   
	elemente=content.split('<div class="data_box">')
	for i in range(1,len(elemente),1):
		try:
			element=elemente[i]  
			debug("RUn")
			if not "button btn-disabled" in element:
				debug("Element :")
				debug (element)
				image = re.compile('src=["\'](http.+?[.png\.jpg])["\'\?]', re.DOTALL).findall(element)[0]
				debug("Image :"+image)
				try:
					urlg = re.compile('button btn-primary " href="(.+?)"', re.DOTALL).findall(element)[0]                                      
				except:
					urlg = re.compile('acLnk ([^ ]+?) button btn-primary', re.DOTALL).findall(element)[0]                    
					urlg=decodeurl(urlg)
				debug("URLG ::"+urlg)
				name= re.compile("title='(.+?)'", re.DOTALL).findall(element)[0].strip()
				debug("Name :"+name)
				try:
					desc=re.compile("<p[^>]*>([^<]+)<", re.DOTALL).findall(element)[0].strip()
				except: desc=""
				match=re.compile('<span itemprop="genre">(.+?)</span>', re.DOTALL).findall(element)          
				genres=[]
				for namex in match:
					genres.append(namex)
					genstr=",".join(genres)
					debug("GENRES")
					debug(genstr)
				try:
					kurz_inhalt = element[element.find('<span class="film_info lighten fl">Von </span>')+1:]
					kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</div>')]
					regisseur= re.compile('title="(.+?)"', re.DOTALL).findall(kurz_inhalt)[0] 
				except:
					regisseur=""
				debug("Regisseur :"+regisseur)
				try:
					match=re.compile('<span class="acLnk ([^"]+)">[^"]+?<span class="note">(.+?)</span></span>', re.DOTALL).findall(element)
					bewertung=""
					debug("X")
					for link, note in match:
						debug("y")
						link=decodeurl(link)
						debug("Notes: "+note)
						debug("link: "+link)
						if "spiegel" in link:
							bewertung=note
						debug("bewertung :"+ bewertung)
				except:
					bewertung=""
				name=ersetze(name)
				if not "http" in urlg:
					urlg=baseurl+urlg
				debug("URLG : "+urlg)
				addLink(name, urlg, 'playVideo', image, desc=desc, genre=genstr, director=regisseur, bewertung=bewertung, referer=url)
		except:
			debug("....")
			debug(element)
	if not datum =="":
		try:
			Start=datetime.strptime(datum, "%Y-%m-%d")
		except TypeError:
			Start=datetime(*(time.strptime(datum, "%Y-%m-%d")[0:6]))
		Nextweek = Start + timedelta(days=7)
		Beforweek = Start - timedelta(days=7)
		nx=Nextweek.strftime("%Y-%m-%d")
		bx=Beforweek.strftime("%Y-%m-%d")
		addDir(translation(30040), url, 'kinovideos', icon, datum=nx)
		addDir(translation(30041), url, 'kinovideos', icon, datum=bx)
	if 'fr">Nächste<i class="icon-arrow-right">' in content:  
		addDir(translation(30006), url, 'kinovideos', pic+"nextpage.png", page=page+1)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def tvstaffeln(url):
	content=geturl(url)
	debug ("tvstaffeln url :"+url)
	kurz_inhalt = content[content.find('<ul class="column-1">')+1:]
	kurz_inhalt = kurz_inhalt[:kurz_inhalt.find("id='seriesseasonnumb")]    
	elemente=kurz_inhalt.split('span class="acLnk')    
	x=0
	for i in range(1,len(elemente),1):
		try:
			element=elemente[i]
			element=element.replace('<strong>',"")
			element=element.replace('</strong>',"")  
			debug(" .... TVSTAFFELN .....")
			name= re.compile('w-scrollto">([^<]+)', re.DOTALL).findall(element)[0]  
			name=name.replace("\n","")
			anzahl= re.compile('<span class="lighten fs11">\((.+?)\)</span>', re.DOTALL).findall(element)[0]  
			debug("name :"+name)
			debug("anzahl :"+anzahl)
			addDir(name+"  ("+anzahl +")", url, "tvfolgen", icon, xtype=name)
			x=x+1
		except: pass
	if x>0:
		addDir(translation(30007), url, 'tvfolgen', icon, xtype="")
		xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)         
	else:
		tvfolgen(url,"") 

def tvfolgen(url,xtype):   
	debug(" Start TVfolgen")   
	debug(url)
	content=geturl(url)
	if "id='seriesseasonnumber" in content:
		elemente=content.split("id='seriesseasonnumber")
		for i in range(1,len(elemente),1):
			element=elemente[i]   
			debug("Element : ")
			debug (element)
			debug ("xtype :"+xtype)
			if xtype in element:
				elemente2=element.split("article data-bloc")
				for i in range(1,len(elemente2),1):
					element2=elemente2[i]
					element2=element2.replace('<strong>',"")
					element2=element2.replace('</strong>',"")
					image = re.compile('["\']src["\']:["\'](http.+?[.png\.jpg])["\'\?]', re.DOTALL).findall(element2)[0]
					match = re.compile('<a href="(.+?)">([^<]+)</a>', re.DOTALL).findall(element2)
					name=match[0][1].strip()
					urlx=match[0][0]
					addLink(name, baseurl+urlx, 'playVideo', image, referer=url)
	else:
		kurz_inhalt = content[content.find('<div class="list-line margin_20b">')+1:]
		kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<div class="social">')]
		elemente2=kurz_inhalt.split("article data-bloc")
		for i in range(1,len(elemente2),1):
			element2=elemente2[i]
			element2=element2.replace('<strong>',"")
			element2=element2.replace('</strong>',"")
			image = re.compile('["\']src["\']:["\'](http.+?[.png\.jpg])["\'\?]', re.DOTALL).findall(element2)[0]
			match = re.compile('<a href="(.+?)">([^<]+)</a>', re.DOTALL).findall(element2)
			name=match[0][1].strip()
			urlx=match[0][0]
			addLink(name, baseurl+urlx, 'playVideo', image, referer=url)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def trailerpage2(url,page=1) :
	page=int(page)
	debug("archivevideos URL :"+url)
	if page >1:
		PGurl=url+"?page="+str(page)
	else:
		PGurl=url
	content=geturl(PGurl)  
	kurz_inhalt = content[content.find('<section class="section-wrap section-trailer-wall">')+1:] 
	debug("--------------------------------------------")
	debug(kurz_inhalt)
	elemente=kurz_inhalt.split('<div class="card card-video-traile')
	for i in range(1,len(elemente),1):
		try:
			element=elemente[i]
			debug("....START")
			debug(element)
			image = re.compile('src=["\'](http.+?[.png\.jpg])["\'\?]', re.DOTALL).findall(element)[0]
			urlx = re.compile('href="(.+?)"', re.DOTALL).findall(element)[0]
			name = re.compile('alt="(.+?)"', re.DOTALL).findall(element)[0]
			name=ersetze(name) 
			debug("image : "+image)
			debug("url : "+urlx)
			debug("name :"+name)
			addLink(name, baseurl+urlx, 'playVideo', image)
		except:
			debug("....NOK")
			debug(element)
	if '<span class="txt">Nächste</span>' in content:
		addDir(translation(30006), url, 'trailerpage2', pic+"nextpage.png", page=page+1)
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def playVideo(url,referer):
	debug("Playvideo URL:"+url)
	content = geturl(url,referer=referer)
	finalUrl = False
	debug("CONTENT PLAYVIDEO")
	debug(content)
	debug("-------")
	try:
		match = re.compile("<iframe[^>]+?src=['\"](.+?)['\"]", re.DOTALL).findall(content)
		debug("LINK : "+match[1])
		if  "_video" in match[1]:
			newurl=baseurl+match[1]
			content = geturl(newurl,referer=url)
	except: pass
	contentx=content.replace("\/","/").replace("&quot;",'"')
	try:
		finalUrl = re.compile('"high":"(.+?)"', re.DOTALL).findall(contentx)[0]
	except:
		try:
			finalUrl = re.compile('"medium":"(.+?)"', re.DOTALL).findall(contentx)[0]
		except: pass
	if finalUrl:
		if not "http" in finalUrl:
			finalUrl="http:"+finalUrl
		debug("Finalurl :"+finalUrl)
		listitem = xbmcgui.ListItem(path=finalUrl)
		xbmcplugin.setResolvedUrl(addon_handle, True, listitem)

page=0   
params = parameters_string_to_dict(sys.argv[2])
name = urllib.unquote_plus(params.get('name', ''))
url = urllib.unquote_plus(params.get('url', ''))
mode = urllib.unquote_plus(params.get('mode', ''))
iconimage = urllib.unquote_plus(params.get('iconimage', ''))
page = urllib.unquote_plus(params.get('page', ''))
xtype = urllib.unquote_plus(params.get('xtype', ''))
datum = urllib.unquote_plus(params.get('datum', ''))
referer = urllib.unquote_plus(params.get('referer', ''))

# Haupt Menu Anzeigen 
if mode is '':
	addDir(translation(30002), "", 'trailer', icon)
	addDir(translation(30003), "", 'series', icon)
	addDir(translation(30004), "", 'kino', icon)
	addDir(translation(30005), "", 'news', icon)
	#addDir(translation(30001), translation(30001), 'Settings', "")
	xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
	# Wenn Settings ausgewählt wurde
	if mode == 'Settings':
		addon.openSettings()
	# Wenn Kategorie ausgewählt wurde
	if mode == 'trailer':
		trailer()
	if mode == 'filterart':
		filterart(url)
	if mode == 'genre':
		genre(url,xtype)
	if mode == 'archivevideos':
		archivevideos(url,page)
	if mode == 'playVideo':
		playVideo(url,referer)
	if mode == 'types':
		types(url)
	if mode == 'sprache':
		sprache(url)
	if mode == 'trailerpage2':
		trailerpage2(url,page)
	if mode == 'series':
		series()
	if mode == 'filterserien':
		filterserien(url)
	if mode == 'serienvideos':
		kinovideos(url,page)
	if mode == 'tvstaffeln':
		tvstaffeln(url)
	if mode == 'tvfolgen':
		tvfolgen(url,xtype)
	if mode == 'jahre':
		jahre(url,type="filterserien")
	if mode == 'laender':
		laender(url,type="filterserien")
	if mode == 'neuetrailer':
		neuetrailer(url,page)
	if mode == 'kino':
		kino()
	if mode == 'kinovideos':
		kinovideos(url,page,datum=datum)
	if mode == 'kinovideosneu':
		kinovideosneu(url,page,datum=datum)
	if mode == 'selectwoche':
		selectwoche(url)
	if mode == 'filterkino':
		filterkino(url)
	if mode == 'news':
		news()
	if mode == 'newsvideos':
		newsvideos(url,page)