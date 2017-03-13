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
import YDStreamExtractor
import xml.etree.ElementTree as ET


import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])

args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
defaultBackground = ""
defaultThumb = ""
cliplist=[]
filelist=[]
profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")


#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       
xbmcplugin.setContent(int(sys.argv[1]), 'musicvideos')
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"



def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def parameters_string_to_dict(parameters):
  paramDict = {}
  if parameters:
    paramPairs = parameters[1:].split("&")
    for paramsPair in paramPairs:
      paramSplits = paramsPair.split('=')
      if (len(paramSplits)) == 2:
        paramDict[paramSplits[0]] = paramSplits[1]
  return paramDict
  
    
def addDir(name, url, mode, iconimage, desc="",staffel="1",folge="1"):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&staffel="+str(staffel)+"&folge="+str(folge)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground    
    liz.setArt({ 'fanart': iconimage })
  else:
    liz.setArt({ 'fanart': defaultBackground })    
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="",artist_id="",genre="",shortname="",production_year=0,zeit=0,liedid=0):  
  cd=addon.getSetting("password")  
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre,"Sorttitle":shortname,"Dateadded":zeit,"year":production_year })
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setArt({ 'fanart': iconimage })     
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok


def getUrl(url,data="x"):        
        debug("Get Url: " +url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        userAgent = "Dalvik/2.1.0 (Linux; U; Android 5.0;)"
        opener.addheaders = [('User-Agent', userAgent)]
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #print e.code   
             cc=e.read()  
             struktur = json.loads(cc)  
             error=struktur["errors"][0] 
             error=unicode(error).encode("utf-8")
             debug("ERROR : " + error)
             dialog = xbmcgui.Dialog()
             nr=dialog.ok("Error", error)
             return ""
             
        opener.close()
        return content


      #addDir(namenliste[i], namenliste[i], mode+datum,logoliste[i],ids=str(idliste[i]))
   #xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
  


page="1"   
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
page = urllib.unquote_plus(params.get('page', ''))
staffel = urllib.unquote_plus(params.get('staffel', ''))
folge = urllib.unquote_plus(params.get('folge', ''))


def serie(mode,feld):
   dialog = xbmcgui.Dialog()
   d = dialog.input(translation(30010), type=xbmcgui.INPUT_ALPHANUM)
   d=d.replace(" ","%20")
   url="http://api.vodster.de/avogler/videos.php?api_key=ea469466-1fa9-420c-994e-42bdbbb32a38&format=json&title="+d
   content=getUrl(url)
   struktur = json.loads(content)
   ids=[]
   for element in struktur:
     debug("-----")
     debug(element)
     try:
       idd=element[feld]
       title=element["title"]
       if not idd in ids:
         ids.append(idd)
         addDir(title,idd,mode,"")
     except:
        pass
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      
       
def lsserie(idd):
   serienurl="http://thetvdb.com/api/EE7293E9091690C1/series/"+idd+"/all/"
   content=getUrl(serienurl)
   Seasons=re.compile('<SeasonNumber>(.+?)</SeasonNumber>', re.DOTALL).findall(content)
   sl=[]
   for season in Seasons:
         if season not in sl:
                addDir("Staffel "+season, idd, 'sseason', "",staffel=season)  
                sl.append(season)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      


def sseason(idd,staffel): 
    serienurl="http://thetvdb.com/api/EE7293E9091690C1/series/"+idd+"/all/"
    content=getUrl(serienurl)
    #debug("----------------------------------------")
    #debug(content)
    debug("----------------------------------------")
    tree = ET.fromstring(content)
    Serie=tree.find('Series')
    #name=Serie.find('SeriesName').text
    #debug("Serienname :"+name)
    debug("Starte Loop")
    all=tree.findall(".//Episode[SeasonNumber='"+staffel+"']")
    for element in all:  
     debug("Element")    
     try:
      name=element.find('EpisodeNumber').text
      debug("NAME :"+name)
     except:
       name=""
     try:
        image=element.find('filename').text
        debug("image :"+image)
     except:
        image=""
     addDir("Folge "+name, idd, 'ffolge', "http://thetvdb.com/banners/_cache/"+image,staffel=staffel,folge=name)     
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

def ffolge(idd,staffel,folge,field):
  debug("Start ffolge:")
  url="http://api.vodster.de/avogler/links.php?api_key=ea469466-1fa9-420c-994e-42bdbbb32a38&format=json&"+field+"="+idd
  if staffel>=0:
    url=url+"&season="+staffel+"&episode="+folge
  content=getUrl(url)
  struktur = json.loads(content)
  providerlist=["ZDF"]
  for element in struktur:
   debug("Provider :"+ element["provider"])
   debug("Url :"+element["url"])
   gef=0
   if element["provider"]=="Sky GO":
    idd=re.compile('/([^/]+?).html', re.DOTALL).findall(element["url"])[0] 
    gef=1    
    addLink(element["provider"], "plugin://plugin.video.skygo.de/?action=playVod&vod_id="+idd,"playplug","")
   if element["provider"]=="Netzkino":
    idd=re.compile('/([^/]+)$', re.DOTALL).findall(element["url"])[0] 
    gef=1    
    addLink(element["provider"], "plugin://plugin.video.netzkino_de/play/?slug="+idd,"playplug","")    
   if element["provider"] in providerlist:   
    gef=1    
    vid = YDStreamExtractor.getVideoInfo(element["url"],quality=1) #quality is 0=SD, 1=720p, 2=1080p and is a maximum
    stream_url = vid.streamURL() #This is what Kodi (XBMC) will play
    stream_url=stream_url.split("|")[0]
    debug("stream_url :"+stream_url)
    addLink(element["provider"], stream_url,"playplug","")
   if element["provider"]=="7TV":
    gef=1    
    addLink(element["provider"], "plugin://plugin.video.7tvneu/?url="+element["url"]+"&mode=getvideoid","playplug","")    
   if element["provider"]=="Maxdome":
    idd=re.compile('--([^/]+?).html', re.DOTALL).findall(element["url"])[0] 
    debug("IDD :"+idd)
    gef=1    
    addLink(element["provider"], "plugin://plugin.video.maxdome/?action=play&id="+idd,"playplug","")
    
   if element["provider"]=="Amazon Prime Instant Video":
      gef=1
      idd=re.compile('/([^/]+?)\?', re.DOTALL).findall(element["url"])[0] 
      addLink(element["provider"], "plugin://plugin.video.amazon/?asin="+idd+"&sitemode=PLAYVIDEO&mode=play","playplug","")      
   if element["provider"]=="Vodster":
     gef=1
   if gef==0:
     addLink(element["provider"] +" (Not Suported)", "","","")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
  
def playplug(url) : 
  debug("playplug :"+url)
  xbmc.executebuiltin("xbmc.PlayMedia("+url+")")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
  
if mode is '':
    addDir("Serien Suche", "", 'serie', "")  
    addDir("Filme Suche", "", 'filme', "")  
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'serie':
          serie("lsserie","tvdb") 
  if mode == 'filme':
          serie("lsfilme","tmdb") 
  if mode == 'lsserie':
          ffolge(url,staffel,folge,"tvdb")
  if mode == 'lsfilme':
          ffolge(url,-1,-1,"tmdb")
  if mode == 'sseason':
           sseason(url,staffel)     
  if mode == 'ffolge':
           ffolge(url,staffel,folge,"tvdb")
  if mode == 'playplug':
           playplug(url) 