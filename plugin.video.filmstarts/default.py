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
   
def addDir(name, url, mode, iconimage, desc="",page=1,xtype=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&xtype="+xtype
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

def decode(url):
    codestring=['1E', '1F', '20', '2A', '21', '22', '2B', '23', '24', '2C', '25', '26', '4A', '41', '42', '4B', '43', '44', '4C', '45', '46', '4D', '47', '48', '4E', '49', '4F', 'C0', 'C1', 'C2', 'CB', 'CD', 'C3', 'C4', 'CC', 'C6']
    decodesring=['-', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'z', 'u', 'v', 'w', 'y']
    ziel=""    
    for i in range(0,len(url),2):   
      zeichen=url[i:i+2]
      ind=codestring.index(zeichen)
      z=decodesring[ind]
      ziel=ziel+z     
    return ziel

    
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

def trailer():
    addDir("Beliebteste Trailer", "http://www.filmstarts.de/trailer/beliebteste.html", 'trailerpage', "")
    addDir("Aktuell im Kino", "http://www.filmstarts.de/trailer/imkino/", 'trailerpage', "")
    addDir("Demnächst im Kino", "http://www.filmstarts.de/trailer/bald/", 'trailerpage', "")
    addDir("Neueste Trailer", "http://www.filmstarts.de/trailer/neu/", 'trailerpage', "")
    addDir("Video-Archiv", baseurl+"/trailer/archiv/", 'filterart', "")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def series():
    addDir("Beliebteste Serien", "http://www.filmstarts.de/serien/top/", 'filterserien', "")
    addDir("Best Bewertete", "http://www.filmstarts.de/serien/beste/", 'filterserien', "")
    addDir("Populaerste Serien", "http://www.filmstarts.de/serien/top/populaerste/", 'serienvideos', "")  
    addDir("Meisterwartete Staffeln", "http://www.filmstarts.de/serien/kommende-staffeln/meisterwartete/", 'serienvideos', "")
    addDir("Neueste Gestartete Serien", "http://www.filmstarts.de/serien/neue/", 'serienvideos', "")         
    addDir("Neue Serien Trailer", "http://www.filmstarts.de/serien/videos/neueste/", 'neuetrailer', "",xtype="")      
    addDir("Video-Archiv", "http://www.filmstarts.de/serien-archiv/", 'filterserien', "")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def filterserien():
    debug("filterart url :"+ url)
    if not "genre-" in url:
        addDir("Filter nach Genre", url, 'genre', "",xtype="filterserien")
    if not "jahrzehnt" in url:        
      addDir("Filter nach Jahre", url, 'jahre',"")
    if not "produktionsland-" in url:
      addDir("Filter nach Laender", url, 'laender', "")
    addDir("Zeige Videos", url, 'serienvideos', "")     
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
def filterart(url):
    debug("filterart url :"+ url)
    if not "genre-" in url:
        addDir("Filter nach Genre", url, 'genre', "",xtype="filterart")
    if not "sprache-" in url:        
      addDir("Filter nach Sprache", url, 'sprache',"")
    if not "format-" in url:
      addDir("Filter nach Format", url, 'types', "")
    addDir("Zeige Videos", url, 'archivevideos', "")     
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
def sprache(url):  
   content=geturl(url)
   kurz_inhalt = content[content.find('Alle Sprachen</span>')+1:]
   kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]
   match = re.compile('<span class="acLnk ([^"]+)">(.+?)</span> <span class="lighten">\((.+?)\)</span>', re.DOTALL).findall(kurz_inhalt)
   for url,name,anzahl in match:    
      url=decode(url)
      addDir(name +" ( "+anzahl +" )", baseurl+url, 'filterart', "")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   


def jahre(url,type="filterserien"):
   content=geturl(url)
   debug("Genre URL :"+url)    
   kurz_inhalt = content[content.find('Alle Jahre</span>')+1:]
   kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]
   elemente=kurz_inhalt.split('<li class="visible">')
   for i in range(1,len(elemente),1):   
        element=elemente[i]    
        debug("-------")
        debug(element)
        match = re.compile('<span class="acLnk ([^"]+)">([^<]+?)</span> <span class="lighten">\(([^<]+?)\)</span>', re.DOTALL).findall(element)  
        url=decode(match[0][0])
        name=match[0][1]
        anzahl=match[0][2]
        debug("Decoed :"+url)
        addDir(name +" ( "+anzahl +" )", baseurl+url, type, "")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   

def neuetrailer(url,page=1):
    page=int(page)
    debug("archivevideos URL :"+url)
    if page >1:
      getu=url+"?page="+str(page)
    else:
      getu=url     
    content=geturl(getu)
    kurz_inhalt = content[content.find('<div class="tabs_main">')+1:]
    kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<div class="pager pager margin_40t">')]
    elemente=kurz_inhalt.split('<article data-block')
    for i in range(1,len(elemente),1):  
        try:    
          element=elemente[i]    
          element=element.replace('<strong>',"")
          element=element.replace('</strong>',"")
          try:
              image = re.compile("src='([^']+)'", re.DOTALL).findall(element)[0]
          except:           
              image = re.compile('"src":"([^"]+)"', re.DOTALL).findall(element)[0]        
          match = re.compile('<a href="([^"]+?)">([^<]+)</a>', re.DOTALL).findall(element)    
          urlx=match[0][0]
          text=match[0][1]
          debug("IMG :"+ image)
          addLink(text, baseurl+urlx, 'playVideo', image)
        except:
          pass
    if 'fr">Nächste<i class="icon-arrow-right">' in content:  
      addDir("Next", url, 'neuetrailer', "",page=page+1)
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  
    
def laender(url,type="filterserien"):
   content=geturl(url)
   debug("Genre URL :"+url)    
   kurz_inhalt = content[content.find('Alle Länder</span>')+1:]
   kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]
   elemente=kurz_inhalt.split('<li class="visible">')
   for i in range(1,len(elemente),1):   
        element=elemente[i]  
        element=element.replace('<strong>',"")
        element=element.replace('</strong>',"")        
        debug("-------")
        debug(element)
        match = re.compile('<span class="acLnk ([^"]+)">([^<]+?)</span> <span class="lighten">\(([^<]+?)\)</span>', re.DOTALL).findall(element)  
        url=decode(match[0][0])
        name=match[0][1]
        anzahl=match[0][2]
        debug("Decoed :"+url)
        addDir(name +" ( "+anzahl +" )", baseurl+url, type, "")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      
   
def types(url):
   content=geturl(url)
   kurz_inhalt = content[content.find('Alle Formate</span>')+1:]
   kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]  
   if "<a href" in kurz_inhalt:
      match = re.compile('<a href="/trailer/archiv/(format-.+?)/">(.+?)</a> <span class="lighten">\((.+?)\)</span>', re.DOTALL).findall(kurz_inhalt)
      for urln,name,anzahl in match:                 
          addDir(name +" ( "+anzahl +" )", baseurl+urln, 'filterart', "")
   else:  
      match = re.compile('<span class="acLnk ([^"]+)">(.+?)</span> <span class="lighten">\((.+?)\)</span>', re.DOTALL).findall(kurz_inhalt)
      for url,name,anzahl in match:      
          debug("name : "+ name)
          debug("anzahl : "+ anzahl)
          url=decode(url)
          addDir(name +" ( "+anzahl +" )", baseurl+url, 'filterart', "")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
   
def genre(url,type="filterart"):
   content=geturl(url)
   debug("Genre URL :"+url)    
   kurz_inhalt = content[content.find('Alle Genres</span>')+1:]
   kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</li></ul>')]
   match = re.compile('<span class="acLnk ([^"]+)">(.+?)</span> <span class="lighten">\((.+?)\)</span>', re.DOTALL).findall(kurz_inhalt)
   for url,name,anzahl in match:      
      url=decode(url)
      debug("Decoed :"+url)
      addDir(name +" ( "+anzahl +" )", baseurl+url, type, "")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
   
def archivevideos(url,page=1):   
   page=int(page)
   debug("archivevideos URL :"+url)
   if page >1:
    getu=url+"?page="+str(page)
   else:
    getu=url     
   content=geturl(getu)   
   elemente=content.split('<article class=')
   for i in range(1,len(elemente),1):
     try:
        element=elemente[i]          
        element=element.replace('<strong>',"")
        element=element.replace('</strong>',"")
        debug("-##-")
        image = re.compile('src="(.+?)"', re.DOTALL).findall(element)[0]
        match = re.compile('<a href="(.+?)">([^<]+)</a>', re.DOTALL).findall(element)
        name=match[0][1]
        urlx=match[0][0]     
        if not "En savoir plus" in name :
            addLink(name, baseurl+urlx, 'playVideo', image)
     except:
        debug("....")
        debug(element)
   if 'fr">Nächste<i class="icon-arrow-right">' in content:
     addDir("Next", url, 'archivevideos', "",page=page+1)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     
   
def serienvideos(url,page=1):   
   debug("Start serienvideos")   
   page=int(page)
   debug("serienvideos URL :"+url)
   if page >1:
    getu=url+"?page="+str(page)
   else:
    getu=url     
   content=geturl(getu)   
   elemente=content.split('<div class="data_box">')
   for i in range(1,len(elemente),1):
     try:
        element=elemente[i]                 
        image = re.compile("src='(.+?)'", re.DOTALL).findall(element)[0]
        urlg = re.compile('href="(.+?)"', re.DOTALL).findall(element)[0]
        urlg=url.replace(".html","/videos/")
        name= re.compile("title='(.+?)'", re.DOTALL).findall(element)[0] 
        name=ersetze(name)
        addDir(name, baseurl+urlg, 'tvstaffeln', image)        
     except:
        debug("....")
        debug(element)
   if 'fr">Nächste<i class="icon-arrow-right">' in content:  
     addDir("Next", url, 'serienvideos', "",page=page+1)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   

def tvstaffeln(url):
    content=geturl(url)
    kurz_inhalt = content[content.find('<ul class="column-1">')+1:]
    kurz_inhalt = kurz_inhalt[:kurz_inhalt.find("id='seriesseasonnumb")]    
    elemente=kurz_inhalt.split('span class="acLnk')    
    x=0
    for i in range(1,len(elemente),1):
            try:
                element=elemente[i]
                debug(" .... TVSTAFFELN .....")
                debug(element)     
                name= re.compile('w-scrollto">([^<]+)', re.DOTALL).findall(element)[0]  
                name=name.replace("\n","")
                anzahl= re.compile('<span class="lighten fs11">\((.+?)\)</span>', re.DOTALL).findall(element)[0]  
                debug("name :"+name)
                debug("anzahl :"+anzahl)
                addDir(name +" ( "+anzahl +" )", url, "tvfolgen", "",xtype=name)
                x=x+1
            except:
                pass
    if x>0:
            addDir("Alle Videos", url, 'tvfolgen', "",xtype="")
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
                image = re.compile('"src":"(.+?)"', re.DOTALL).findall(element2)[0]
                match = re.compile('<a href="(.+?)">([^<]+)</a>', re.DOTALL).findall(element2)
                name=match[0][1]
                urlx=match[0][0]                   
                addLink(name, baseurl+urlx, 'playVideo', image)    
    else:
        kurz_inhalt = content[content.find('<div class="list-line margin_20b">')+1:]
        kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<div class="social">')]    
        elemente2=kurz_inhalt.split("article data-bloc")
        for i in range(1,len(elemente2),1):
                element2=elemente2[i]
                element2=element2.replace('<strong>',"")
                element2=element2.replace('</strong>',"")        
                image = re.compile('"src":"(.+?)"', re.DOTALL).findall(element2)[0]
                match = re.compile('<a href="(.+?)">([^<]+)</a>', re.DOTALL).findall(element2)
                name=match[0][1]
                urlx=match[0][0]                   
                addLink(name, baseurl+urlx, 'playVideo', image)    
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
xtype = urllib.unquote_plus(params.get('xtype', ''))


def trailerpage(url,page=1) :
   page=int(page)
   debug("archivevideos URL :"+url)
   if page >1:
    getu=url+"?page="+str(page)
   else:
    getu=url     
   content=geturl(getu)  
   kurz_inhalt = content[content.find('<!-- /titlebar_01 -->')+1:]
   kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</section>')]   
   debug("--------------------------------------------")
   debug(kurz_inhalt)
   elemente=kurz_inhalt.split('article data-block')
   for i in range(1,len(elemente),1):
     try:
        element=elemente[i]
        debug("....START")
        debug(element)
        try:
            image = re.compile("src='(.+?)'", re.DOTALL).findall(element)[0]
        except:
           image = re.compile('"src":"(.+?)"', re.DOTALL).findall(element)[0]        
        urlx = re.compile('href="(.+?)"', re.DOTALL).findall(element)[0]        
        name = re.compile('<strong>(.+?)</strong>', re.DOTALL).findall(element)[0]        
        addLink(name, baseurl+urlx, 'playVideo', image)
     except:
        debug("....NOK")
        debug(element)
   if 'fr">Nächste<i class="icon-arrow-right">' in content:
     addDir("Next", url, 'trailerpage', "",page=page+1)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     
        
# Haupt Menu Anzeigen      
if mode is '':
    addDir(translation(30002), "", 'trailer', "")
    addDir("Serien", "", 'series', "")
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
          filterart(url)
  if mode == 'genre':
          genre(url,xtype)  
  if mode == 'archivevideos':
          archivevideos(url,page)               
  if mode == 'playVideo':
          playVideo(url)                     
  if mode == 'types':
          types(url)                               
  if mode == 'sprache':
          sprache(url)
  if mode == 'trailerpage':
          trailerpage(url,page)    
  if mode == 'series':
          series()                
  if mode == 'filterserien':
          filterserien()              
  if mode == 'serienvideos':
          serienvideos(url,page)       
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
