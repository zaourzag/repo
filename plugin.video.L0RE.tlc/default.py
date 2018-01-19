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
import base64
import requests
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString


xbmcplugin.setContent(addon_handle, 'movies')

baseurl="https://www.tlc.de"
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)


icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')


profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
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
    

  
def addDir(name, url, mode, thump, desc="",page=1,nosub=0):   
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&nosub="+str(nosub)
  ok = True
  liz = xbmcgui.ListItem(name)  
  liz.setArt({ 'fanart' : thump })
  liz.setArt({ 'thumb' : thump })
  liz.setArt({ 'banner' : icon })
  liz.setArt({ 'fanart' : icon })
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, thump, duration="", desc="", genre='',director="",bewertung=""):
  debug("URL ADDLINK :"+url)
  debug( icon  )
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name,thumbnailImage=thump)
  liz.setArt({ 'fanart' : icon })
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre, "Director":director,"Rating":bewertung})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
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


def geturl(url,data="x",header="",referer=""):
        global cj
        debug("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))        
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
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
        return content


    

   
   
  
def liste():      
    addDir("Featured" , baseurl+"/api/shows/featured?limit=100&page=1", "videoliste","",nosub="featured") 
    addDir("Belibteste" , baseurl+"/api/shows/most-popular?limit=100&page=1", "videoliste","",nosub="most-popular")    
    addDir("Neueste" , baseurl+"/api/shows/recently-added?limit=100&page=1", "videoliste","",nosub="recently-added")        
    addDir("Letzt Chance" , baseurl+"/api/shows/leaving-soon?limit=100&page=1", "videoliste","",nosub="leaving-soon")    
    addDir("Settings","Settings","Settings","")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

  
def playvideo(idd):      
    content=geturl(baseurl)    
    for cookief in cj:
          debug( cookief)
          if "sonicToken" in str(cookief) :         
                key=re.compile('sonicToken=(.+?) ', re.DOTALL).findall(str(cookief))[0]
                break

    playurl="https://sonic-eu1-prod.disco-api.com/playback/videoPlaybackInfo/"+str(idd)
    header = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'),
                    ("Authorization", "Bearer "+key)]

    content=geturl(playurl,header=header)
    debug(content)
    struktur = json.loads(content)    
    videofile=struktur["data"]["attributes"]["streaming"]["hls"]["url"]
    #licfile=struktur["data"]["attributes"]["protection"]["schemes"]["widevine"]["licenseUrl"]
    debug(videofile)
    #debug(licfile)
    listitem = xbmcgui.ListItem(path=videofile)    
    listitem.setProperty('IsPlayable', 'true')
    #listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
    #listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    #listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
    #listitem.setProperty('inputstream.adaptive.license_key', licfile)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
referer = urllib.unquote_plus(params.get('referer', ''))
page = urllib.unquote_plus(params.get('page', ''))
nosub= urllib.unquote_plus(params.get('nosub', ''))
def listserie(idd):
  url=baseurl+"/api/show-detail/"+str(idd)
  debug("listserie :"+url)
  content=geturl(url)
  struktur = json.loads(content)
  subelement=struktur["videos"]["episode"]
  for number,videos in subelement.iteritems(): 
    for video in videos:
        idd=video["id"]
        title=video["title"]
        title=title.replace("{S}","S").replace(".{E}","E")
        desc=video["description"]
        duration=video["videoDuration"]
        duration=duration/1000
        image=video["image"]["src"]
        airdate=video["airDate"]
        addLink(title,idd,"playvideo",image,desc=desc,duration=duration)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

def videoliste(url,page=1,nosub=""):    
  content=geturl(url)
  struktur = json.loads(content) 
  elemente=struktur["sections"][nosub]
  for element in elemente:
    title=element["title"]
    idd=element["id"]
    desc=element["description"]
    image=element["image"]["src"]
    addDir(title,idd,"listserie",image,desc=desc)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
# Haupt Menu Anzeigen      
if mode is '':
     liste()   
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'playvideo':
          playvideo(url)
  if mode == 'subrubrik':
          subrubrik(url)
  if mode == 'videoliste':
          videoliste(url,page,nosub)
  if mode == 'listserie':
           listserie(url)