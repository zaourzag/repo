#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil,json
import time


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

icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
bitrate=addon.getSetting("bitrate")

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)

cookie=temp+"/cookie.jar"
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
   inhalt=inhalt.replace('&#39;','\'')  
   inhalt=inhalt.replace('&quot;','"')    
   inhalt=inhalt.replace('&gt;','>')      
   inhalt=inhalt.replace('&amp;','&') 
   return inhalt
   
def addDir(name, url, mode, iconimage, desc="",page=1,format="",genre="",sprache=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&format="+str(format)+"&genre="+str(genre)+"&sprache="+str(sprache)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
	liz.setProperty('IsPlayable', 'true')
	liz.addStreamInfo('video', { 'duration' : duration })
	liz.setProperty("fanart_image", iconimage)
	#xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
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
  
def geturl(url,data="x",header=""):
        global cj
        print("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))        
        userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"
        if header=="":
          opener.addheaders = [('User-Agent', userAgent)]        
        else:
          opener.addheaders = header        
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #print e.code   
             cc=e.read()  
             debug("Error : " +cc)
       
        opener.close()
        cj.save(cookie,ignore_discard=True, ignore_expires=True) 
        return content
def makeurl(url,format,genre,sprache):
  zielurl=url
  if not format=="":
    zielurl=zielurl+format
  if not genre=="":
    zielurl=zielurl+genre
  if not sprache=="":
    zielurl=zielurl+sprache
  return zielurl
def trailer():
    #addDir("Beliebteste Trailer", baseurl, 'Trailer', "")
    #addDir("Aktuell im Kino", baseurl, 'Trailer', "")
    #addDir("Demnächst im Kino", baseurl, 'Trailer', "")
    #addDir("Neueste Trailer", baseurl, 'Trailer', "")
    addDir("Video-Archiv", baseurl+"/trailer/archiv/", 'filterart', "")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def filterart(url,format="",genre="",sprache=""):
    debug("filterart url :"+ url)
    if not "genre-" in genre:
        addDir("Filter nach Genre", url, 'genre', "",format=format,genre=genre,sprache=sprache)
    if not "sprache-" in sprache:        
      addDir("Filter nach Sprache", url, 'sprache',"",format=format,genre=genre,sprache=sprache)
    if not "format-" in format:
      addDir("Filter nach Format", url, 'type', "",format=format,genre=genre,sprache=sprache)
    zu=makeurl(url=url,format=format,genre=genre,sprache=sprache)
    addDir("Zeige Videos", zu, 'archivevideos', "")     
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
def sprache(url,format="",genre="",sprache=""):  
   zu=makeurl(url=url,format=format,genre=genre,sprache=sprache)
   content=geturl(zu)
   kurz_inhalt = content[content.find('Alle Sprachen</span>')+1:]
   kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]
   match = re.compile('<span class="acLnk [^"]+">(.+?)</span> <span class="lighten">\((.+?)\)</span>', re.DOTALL).findall(kurz_inhalt)
   for name,anzahl in match:    
      if name =="Deutsche Fassung":
          id=0      
      if name =="Originalversion":
          id=1      
      sprache="/sprache-"+str(id)
      addDir(name +" ( "+anzahl +" )", url, 'filterart', "",genre=genre,format=format,sprache=sprache)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
   
def type(url,format="",genre="",sprache=""):
   zu=makeurl(url=url,format=format,genre=genre,sprache=sprache)
   ids=["31018","31023","31016","31003","31004"]
   namen=["Making of","Reportage","Teaser","Trailer","Videoauszug"]
   content=geturl(zu)
   kurz_inhalt = content[content.find('Alle Formate</span>')+1:]
   kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]
   debug("Kurzinhalt")
   debug(kurz_inhalt)
   if "<a href" in kurz_inhalt:
      match = re.compile('<a href="/trailer/archiv/(format-.+?)/">(.+?)</a> <span class="lighten">\((.+?)\)</span>', re.DOTALL).findall(kurz_inhalt)
      for urln,name,anzahl in match:                 
          addDir(name +" ( "+anzahl +" )", baseurl+urln, 'filterart', "",genre=genre,format=format,sprache=sprache)
   else:  
      debug("ELSE")   
      match = re.compile('<span class="acLnk [^"]+">(.+?)</span> <span class="lighten">\((.+?)\)</span>', re.DOTALL).findall(kurz_inhalt)
      for name,anzahl in match:      
          debug("name : "+ name)
          debug("anzahl : "+ anzahl)
          ind=namen.index(name)
          id=ids[ind]
          format="/format-"+str(id)
          addDir(name +" ( "+anzahl +" )", url, 'filterart', "",genre=genre,format=format,sprache=sprache)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
   
def genre(url,format="",genre="",sprache=""):
   zu=makeurl(url=url,format=format,genre=genre,sprache=sprache)
   content=geturl(zu)
   debug("Genre URL :"+url)   
   # Kapitel 1 Die Genres
   url_genre = re.compile('src="(/[^"]+?/environment.js)"', re.DOTALL).findall(content)[0]
   url_genre=baseurl+url_genre
   content_genres=geturl(url_genre)
   genres_json = re.compile('genres : \[(.+?)\],', re.DOTALL).findall(content_genres)[0]   
   
   genres_json = "["+genres_json+"]"
   struktur = json.loads(genres_json) 
   ids=[]
   namen=[]
   for element in struktur:
     name=unicode(element["name"]).encode("utf-8")
     name=name.replace("Krieg","Kriegsfilm")
     namen.append(name)
     ids.append(element["key"])
   debug("Struktur :")
   debug (struktur)
   kurz_inhalt = content[content.find('Alle Genres</span>')+1:]
   match = re.compile('<span class="acLnk [^"]+">(.+?)</span> <span class="lighten">\((.+?)\)</span>', re.DOTALL).findall(kurz_inhalt)
   for name,anzahl in match:      
      debug("name : "+ name)
      debug("anzahl : "+ anzahl)
      ind=namen.index(name)
      id=ids[ind]
      genre="/genre-"+str(id)
      addDir(name +" ( "+anzahl +" )", url, 'filterart', "",genre=genre,format=format,sprache=sprache)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
   
def archivevideos(url,page=1):   
   page=int(page)
   debug("archivevideos URL :"+url)
   if page >1:
    getu=url+"?page="+str(page)
   else:
    getu=url     
   content=geturl(getu)   
   elemente=content.split('<article class="media-meta sidecontent small">')
   for i in range(1,len(elemente),1):
     try:
        element=elemente[i]
        image = re.compile('src="(.+?)"', re.DOTALL).findall(element)[0]
        urlx = re.compile('href="(.+?)"', re.DOTALL).findall(element)[0]
        name = re.compile('<strong>(.+?)</strong>', re.DOTALL).findall(element)[0]
        addLink(name, baseurl+urlx, 'playVideo', image)
     except:
        debug("....")
        debug(element)
   if 'fr">Nächste<i class="icon-arrow-right">' in content:
     addDir("Next", url, 'archivevideos', "",page=page+1)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     
   
   

def playVideo(url):
    content = geturl(url)
    match = re.compile('"html5PathHD":"(.*?)"', re.DOTALL).findall(content)
    finalUrl=""
    if match[0] and match[0].startswith("http://"):
        finalUrl=match[0]
    else:
        match = re.compile('"refmedia":(.+?),', re.DOTALL).findall(content)
        media = match[0]
        match = re.compile('"relatedEntityId":(.+?),', re.DOTALL).findall(content)
        ref = match[0]
        match = re.compile('"relatedEntityType":"(.+?)"', re.DOTALL).findall(content)
        typeRef = match[0]
        content = geturl(baseurl + '/ws/AcVisiondataV4.ashx?media='+media+'&ref='+ref+'&typeref='+typeRef)
        finalUrl = ""
        match = re.compile('hd_path="(.+?)"', re.DOTALL).findall(content)
        finalUrl = match[0]
        if finalUrl.startswith("youtube:"):
            finalUrl = getYoutubeUrl(finalUrl.split(":")[1])
    if finalUrl:
        listitem = xbmcgui.ListItem(path=finalUrl)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
   
   
   
page=0   
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
page = urllib.unquote_plus(params.get('page', ''))
name = urllib.unquote_plus(params.get('name', ''))
xformat = urllib.unquote_plus(params.get('format', ''))
xgenre = urllib.unquote_plus(params.get('genre', ''))
xsprache = urllib.unquote_plus(params.get('sprache', ''))
        
# Haupt Menu Anzeigen      
if mode is '':
    addDir(translation(30002), "", 'trailer', "")
    #addDir(translation(30001), translation(30001), 'Settings', "")   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'trailer':
          trailer()
  if mode == 'filterart':
          filterart(url,format=xformat,genre=xgenre,sprache=xsprache)
  if mode == 'genre':
          genre(url,format=xformat,genre=xgenre,sprache=xsprache)  
  if mode == 'archivevideos':
          archivevideos(url,page)               
  if mode == 'playVideo':
          playVideo(url)                     
  if mode == 'type':
          type(url,format=xformat,genre=xgenre,sprache=xsprache)                               
  if mode == 'sprache':
          sprache(url,format=xformat,genre=xgenre,sprache=xsprache)