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

xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)


icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')


profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

cachezeit=addon.getSetting("cachetime")   
cache = StorageServer.StorageServer("plugin.video.L0RE.3plus", cachezeit) # (Your plugin name, Cache time in hours


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
    

  
def addDir(name, url, mode, thump, desc="",page=1,sub=""):   
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&sub="+str(sub)
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
    addDir("Sendungen" , "http://3plus.tv/videos", "Serien","")   
    xbmcplugin.endOfDirectory(addon_handle) 

def playvideo(url):  
   newurl="https://playout.3qsdn.com/"+url+"?timestamp=0&key=0&js=true&container=sdnPlayer&width=100%&height=100%&protocol=http&wmode=direct&preload=true&amp=false"
   debug(newurl)
   content=geturl(newurl)   
   liste=re.compile("{src:'(.+?)', type: '(.+?)', quality: '(.+?)' }", re.DOTALL).findall(content)
   quality_setting=addon.getSetting("quality")   
   stream=""
   for url,type,quality in liste:     
     stream=url
     if quality==quality_setting:
       break     
    
   listitem = xbmcgui.ListItem(path=stream)   
   addon_handle = int(sys.argv[1])  
   xbmcplugin.setResolvedUrl(addon_handle, True, listitem)


    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
referer = urllib.unquote_plus(params.get('referer', ''))
page= urllib.unquote_plus(params.get('page', ''))
sub= urllib.unquote_plus(params.get('sub', ''))




def episoden(url):
#views-field-field-video-embed
  debug("Start episodes")
  debug(url)
  content = cache.cacheFunction(geturl,url)  
  htmlPage = BeautifulSoup(content, 'html.parser')    
  subhtml = htmlPage.find("div",attrs={"class":"pane-content"})   
  Videos = subhtml.find_all("li",attrs={"class":re.compile("views-row")}) 
  for video in Videos:
    debug("------")
    debug(video)
    linkrhtml=video.find("div",attrs={"class":"views-field-field-threeq-value"})
    debug(linkrhtml)
    link=linkrhtml.find("div",attrs={"class":"field-content"}).text
    debug("######"+link+"######")    
    titlehtml=video.find("div",attrs={"class":"views-field-title"})
    title=titlehtml.find("div",attrs={"class":"field-content"}).text
    bild=video.find("img")["src"]
    bild=bild.replace("_video","_big")
    addLink(title,link,"playvideo",bild)
  xbmcplugin.endOfDirectory(addon_handle)      
  
def staffelliste(url):  
  content = cache.cacheFunction(geturl,url) 
  htmlPage = BeautifulSoup(content, 'html.parser')  
  Videos = htmlPage.find_all("div",attrs={"class":"views-field-title-1"}) 
  for video in Videos:
    linkhtml=video.find("a")
    link="http://3plus.tv"+linkhtml["href"]  
    title = linkhtml.text   
    addDir(title,link,"episoden","")
  xbmcplugin.endOfDirectory(addon_handle)      
  
def Serien(url):
  content = cache.cacheFunction(geturl,url) 
  htmlPage = BeautifulSoup(content, 'html.parser')  
  Videos_block = htmlPage.find("div",attrs={"class":"view view-videos view-id-videos view-display-id-block_8 view-dom-id-4"}) 
  Videos = Videos_block.find_all("li") 
  for video in Videos:
    linkhtml=video.find("a")
    link="http://3plus.tv"+linkhtml["href"]  
    title = linkhtml.text   
    addDir(title,link,"staffelliste","")
  xbmcplugin.endOfDirectory(addon_handle)  
  
  
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
  if mode == 'Serien':
          Serien(url)  
  if mode == 'staffelliste':
          staffelliste(url)  
  if mode == 'episoden':
          episoden(url)           