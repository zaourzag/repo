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
from StringIO import StringIO
import xml.etree.ElementTree as ET
import binascii
import time
from datetime import datetime


# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
debuging=""
# Es geht um Videos
xbmcplugin.setContent(addon_handle, 'movies')
baseurl="http://www1.wdr.de"
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
defaultBackground = ""
defaultThumb = ""
global bitrate
bitrate=addon.getSetting("bitrate")
global kurzvideos
kurzvideos=addon.getSetting("kurzvideos")

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)

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
   inhalt=inhalt.strip()
   return inhalt
   
def addDir(name, url, mode, iconimage, desc="",page=0):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  if page>0 :
      u=u+"&page="+str(page)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground
    liz.setProperty("fanart_image", iconimage)
  else:
    liz.setProperty("fanart_image", defaultBackground)
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre=''):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
	liz.setProperty('IsPlayable', 'true')
	liz.addStreamInfo('video', { 'duration' : duration })
	liz.setProperty("fanart_image", iconimage)
	#liz.setProperty("fanart_image", defaultBackground)
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
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
  
  
def abisz():
  letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
  for letter in letters:
		addDir(letter.upper(), letter.upper(), 'Buchstabe', "")
  xbmcplugin.endOfDirectory(addon_handle)
 
def geturl(url):
   cj = cookielib.CookieJar()
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   req = urllib2.Request(url)
   inhalt = urllib2.urlopen(req).read()   
   return inhalt
  
def getbuchstabe(url):
    adresse=baseurl+"/mediathek/video/sendungen-a-z/sendungen-" + url.lower() +"-102.html"
    debug("getbuchstabe adresse:"+adresse)
    inhalt = geturl(adresse)
    inhalt=ersetze(inhalt) 
    kurz_inhalt = inhalt[inhalt.find('<h2 class="conHeadline hidden">Neuer Abschnitt</h2>')+1:]
    kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<div class="section sectionA" >')]
    spl=kurz_inhalt.split('</li>')
    la=len(spl)
    debug("LA : "+ str(la))
    for i in range(0,len(spl),1):
      entry=spl[i]
      error=0
      try:
        match=re.compile('<a href="([^"]+)"', re.DOTALL).findall(entry)
        serien_url=baseurl+match[0]
        match=re.compile('<span>([^<]+)</span>', re.DOTALL).findall(entry)
        serien_title=match[0]
        match=re.compile('<img.+?src="([^"]+)"', re.DOTALL).findall(entry)
        serien_bild=baseurl+match[0]       
     
        addDir(name=serien_title, url=serien_url, mode="list_serie", iconimage=serien_bild )
       
      except :
         error=1
         debug("URL ERROR: "+ entry )
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)


 
def list_serie(url):
    global icon
    debug("listserie : url "+url)
    inhalt = geturl(url)
    spl=inhalt.split('<div class="teaser hideTeasertext">')
    for i in range(1,len(spl),1):
       entry=spl[i]
       entry = entry[:entry.find('<div class="box"')]
       debug("-------------------")
       debug(entry)
       debug("-------------------")
       match=re.compile('<a href="(.+?)" data-extension=', re.DOTALL).findall(entry) 
       try:
           url=match[0]       
           match=re.compile('<span class="hidden">Video:</span>(.+?)</h4>', re.DOTALL).findall(entry) 
           title=ersetze(match[0])
       except:
           continue           
       match=re.compile('<img .+?src="(.+?)"/>', re.DOTALL).findall(entry) 
       img=match[0]
       try:
         match=re.compile('<p class="teasertext">([^<]+)', re.DOTALL).findall(entry) 
         desc=ersetze(match[0])
       except:
         desc=0 
       try:                           
         match=re.compile('<p class="programInfo">(.+?) .+?<span class="hidden">L&auml;nge: </span>(.+?)<', re.DOTALL).findall(entry) 
         datum=match[0][0]
         laufzeit=match[0][1]
         debug("Laufzeit1 :"+laufzeit)
         sp1=laufzeit.split(":")
         debug("Laenge: "+ str(len(sp1)))
         if len(sp1) == 3 :
            laufzeit=int(sp1[0])*3600+int(sp1[1])*60+int(sp1[2])
         if len(sp1) == 2 :
            laufzeit=int(sp1[0])*60+int(sp1[1])
         if len(sp1) == 1 :
            laufzeit=int(sp1[0])
         debug("Laufzeit2 : "+str(laufzeit))          
       except:
         datum=0    
         laufzeit=0       
       debug("list_serie desc : "+ desc)   
       debug("list_serie url : "+ url)   
       debug("list_serie title : "+ title)   
       debug("list_serie img : "+ img)   
       addLink(name=ersetze(title), url=baseurl+url, mode="folge", iconimage=baseurl+img,desc=desc,duration=laufzeit)  
    kurz_inhalt = inhalt[inhalt.find('<div class="mod modA modGlossar shortNews"')+1:]
    spl=inhalt.split('<h3 class="headline"')
    for i in range(1,len(spl),1):
       entry=spl[i]  
       debug("-------------------")
       debug(entry)
       debug("-------------------")
       match=re.compile('<a href="([^"]+?)" data-extension="{[^<]+?title="([^"]+?)">', re.DOTALL).findall(entry)   
       try:
           url=match[0][0]       
           title=ersetze(match[0][1])
       except:
           continue 
       try:           
           match=re.compile('<img .+?src="(.+?)"/>', re.DOTALL).findall(entry) 
           img=match[0]
       except:
            img=icon
       try:
         match=re.compile('<p class="teasertext">([^<]+)', re.DOTALL).findall(entry) 
         desc=ersetze(match[0])
       except:
         desc=0       
       debug("list_serie url : "+ url)   
       debug("list_serie title : "+ title)   
       debug("list_serie img : "+ img)   
       addLink(name=ersetze(title), url=baseurl+url, mode="folge", iconimage=baseurl+img,desc=desc)     
    
    
    
    
              
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
def folge(url):
    if debuging=="true":
      xbmc.log("Folge URL"+ url)
    debug("1------")
    debug(url)
    debug("------")
    inhalt = geturl(url)    
    match=re.compile("url': '(.+?)'", re.DOTALL).findall(inhalt)
    urljs=match[0]
    debug("2------")
    debug(urljs)
    debug("------")
    inhalt = geturl(urljs)    
    match=re.compile('"alt":{"videoURL":"(.+?)"', re.DOTALL).findall(inhalt)     
    videourl=match[0]   
    debug("3------")
    debug(videourl)
    debug("------")
    listitem = xbmcgui.ListItem(path=videourl)
    xbmcplugin.setResolvedUrl(addon_handle,True, listitem)  
def live(url):
    inhalt = geturl(url)    
    match=re.compile("'mediaObj': { 'url': '(.+?)'", re.DOTALL).findall(inhalt)
    urljs=match[0]    
    debug("2------")
    debug(urljs)
    debug("------")
    inhalt = geturl(urljs)    
    match=re.compile('"alt":{"videoURL":"(.+?)"', re.DOTALL).findall(inhalt)     
    videourl=match[0]   
    debug("3------")
    debug(videourl)
    debug("------")
    listitem = xbmcgui.ListItem(path=videourl)
    xbmcplugin.setResolvedUrl(addon_handle,True, listitem)  
      
def getdatum (starturl,sender):
   debug("XXX Start getdatum" )
   dialog = xbmcgui.Dialog()
   d = dialog.input(translation(30009), type=xbmcgui.INPUT_DATE)
   d=d.replace(' ','0')  
   d= d[6:] + "-" + d[3:5] + "-" + d[:2]
   2016-06-05
   datumstr=d[8:10]+d[5:7]+d[:4]
   url=baseurl+"/mediathek/video/sendungverpasst/sendung-verpasst-100~_mon-"+datumstr+"_tag-"+datumstr+".html"
   debug("Search URL:" + url)   
   list_serie(url)
   #inhalt = geturl(url) 
#<div class="teaser hideTeasertext">
def search(url=""):
   dialog = xbmcgui.Dialog()
   d = dialog.input(translation(30010), type=xbmcgui.INPUT_ALPHANUM)      
   getcontent_search(d,1)
  
def getcontent_search(d,page):
   url=baseurl+"/mediathek/video/suche/index.jsp?q=" + d+"&pt_video=on&pageNumber="+str(page)
   debug("getcontent_search :" + url)
   inhalt=geturl(url)
   inhalt=ersetze(inhalt)
   spl=inhalt.split('<div class="media mediaA">')
   for i in range(1,len(spl),1):
       entry=spl[i]
       match=re.compile('<img.+?src="([^"]+)"', re.DOTALL).findall(entry) 
       img=baseurl+match[0]            
       entry = entry[entry.find('<h3 class="headline">')+1:]
       entry = entry[:entry.find('</h3>')]
       debug("2-------")
       debug(entry)
       debug("-------")
       match=re.compile('<a href="([^"]+)">(.+?)</a>', re.DOTALL).findall(entry)   
       url=match[0][0]
       name=match[0][1]         
       addLink(name=name, url=url, mode="folge", iconimage=img) 
   anz=len(spl)
   if anz>=11:
      page=int(page)+1
      addDir(name="Next", url=d, mode="getcontent_search", iconimage="",page=page)   
   #debug(inhalt)       
   match=re.compile('<a class="sprite ir" href="([^"]+)"', re.DOTALL).findall(inhalt)       
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   

   

       
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
page = urllib.unquote_plus(params.get('page', ''))
showName = urllib.unquote_plus(params.get('showName', ''))
hideShowName = urllib.unquote_plus(params.get('hideshowname', '')) == 'True'
nextPage = urllib.unquote_plus(params.get('nextpage', '')) == 'True'
einsLike = urllib.unquote_plus(params.get('einslike', '')) == 'True'    

# Haupt Menu Anzeigen      
if mode is '':
    addDir(translation(30001), translation(30001), 'A-Z', "")
    addDir(translation(30005), translation(30005), 'Datum', "")
    addLink(translation(30007) , translation(30007),"live","") 
    addDir(translation(30011), translation(30011), 'Search', "")
    #addDir(translation(30002), translation(30002), 'Settings', "")   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'A-Z':
          abisz()
  if mode == 'Datum':
          getdatum("/mediathek/video/programm/index.html","BR3")
  if mode == 'Buchstabe':
          getbuchstabe(url)
  if mode == 'list_serie':
          list_serie(url)            
  if mode == 'folge':
          folge(url)      
  if mode == 'live':
          live("http://www1.wdr.de/mediathek/video/live/index.html")     
  if mode == 'Search':
          search()             
  if mode == 'getcontent_search':
          getcontent_search(url,page)             
