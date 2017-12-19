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
import YDStreamExtractor

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString


xbmcplugin.setContent(addon_handle, 'Movies')

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
    

  
def addDir(name, url, mode, thump, desc="",page=1,sub="",serie=""):   
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&sub="+str(sub)+"&serie="+str(serie)
  ok = True
  liz = xbmcgui.ListItem(name)  
  liz.setArt({ 'fanart' : thump })
  liz.setArt({ 'thumb' : thump })
  liz.setArt({ 'banner' : icon })
  liz.setArt({ 'fanart' : icon })
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, thump, duration="", desc="", genre='',director="",bewertung="",serie=""):
  debug("URL ADDLINK :"+url)
  debug( icon  )
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name,thumbnailImage=thump)
  liz.setArt({ 'fanart' : icon })
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre, "Director":director,"Rating":bewertung,"TVShowTitle":serie})
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
    addDir("Sendungen" , "categories1", "themenliste","")   
    addDir("Stöbern" , "categories2", "themenliste","")   
    addDir("Studios" , "http://www.spiegel.tv/allstudios", "startrubrik","",sub="studios")   
    addDir("Meist gesehen" , "http://www.spiegel.tv/hot", "startrubrik","",sub="videos")      
    addDir("Neues" , "http://www.spiegel.tv/new  ", "startrubrik","",sub="videos")       
    xbmcplugin.endOfDirectory(addon_handle) 

def playvideo(url):    
   debug(url)
   vid = YDStreamExtractor.getVideoInfo(url,quality=2) #quality is 0=SD, 1=720p, 2=1080p and is a maximum
   debug(vid)
   stream_url = vid.streamURL()
   stream_url=stream_url.split("|")[0]
   listitem = xbmcgui.ListItem(path=stream_url)   
   addon_handle = int(sys.argv[1])  
   xbmcplugin.setResolvedUrl(addon_handle, True, listitem)


    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
referer = urllib.unquote_plus(params.get('referer', ''))
page= urllib.unquote_plus(params.get('page', ''))
sub= urllib.unquote_plus(params.get('sub', ''))
serie= urllib.unquote_plus(params.get('serie', ''))

def themenliste(url):
  starturl="http://www.spiegel.tv/start"  
  content=geturl(starturl)
  htmlPage = BeautifulSoup(content, 'html.parser')  
  themen_subs = htmlPage.find("ul",attrs={"id":url})  
  themen = themen_subs.find_all("li",attrs={"class":"underlinemagic"})    
  for thema in themen:          
    link_html=thema.find("a")
    link="http://www.spiegel.tv"+link_html["href"]
    text=link_html.text       
    addDir(text,link,"videoliste","")  
  xbmcplugin.endOfDirectory(addon_handle)
  
def startrubrik(url,sub):
  content=geturl(url)
  htmlPage = BeautifulSoup(content, 'html.parser')  
  Videos_block = htmlPage.find("div",attrs={"id":"rcblock"}) 
  Videos = Videos_block.find_all("a",attrs={"data-navigateto":sub}) 
  for video in Videos:
    link="http://www.spiegel.tv"+video["href"]
    image = video.find("img")["src"]
    title = video.find("img")["alt"]
    if sub=="studios":
      addDir(title,link,"videoliste",image,serie=title)
    else:
     addLink(title,link,"playvideo",image)
  xbmcplugin.endOfDirectory(addon_handle)  
  
def videoliste(url,serie):
  xbmcplugin.setContent(addon_handle, 'episodes')
  content=geturl(url)
  htmlPage = BeautifulSoup(content, 'html.parser')  
  Videos_block = htmlPage.find("div",attrs={"id":"rcblock"}) 
  Videos = Videos_block.find_all("a",attrs={"class":"focusable tholder material"}) 
  for video in Videos:
    debug("---")
    debug(video)
    link="http://www.spiegel.tv"+video["href"]
    image = video.find("img")["src"]
    title = video.find("div",attrs={"class":"autocut bold cardtitle"}).text
    desc = video.find("div",attrs={"class":"tdesc"}).text    
    durationstring = video.find("div",attrs={"class":"tholderbottom"}).text
    duration=re.compile('([0-9]+)', re.DOTALL).findall(durationstring)[0]    
    duration=int(duration)*60
    addLink(title,link,"playvideo",image,desc=desc,serie=serie,duration=duration)
  xbmcplugin.endOfDirectory(addon_handle)  
  
  
def playlive():
 url="http://www.weltderwunder.de/videos/live"
 content=geturl(url)
 htmlPage = BeautifulSoup(content, 'html.parser')
 videoinfo = htmlPage.find("iframe")["src"]
 content=geturl(videoinfo)
 debug(content)
 videoliste=re.compile('"applehttp","url":"(.+?)"', re.DOTALL).findall(content)[0]
 videoliste=videoliste.replace("\\/","/")
 listitem = xbmcgui.ListItem(path=videoliste)   
 addon_handle = int(sys.argv[1])  
 xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
 
 
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
  if mode == 'themenliste':
          themenliste(url)  
  if mode == 'playlive':
          playlive()
  if mode == 'videoliste':
          videoliste(url,serie)  
  if mode == 'startrubrik':
          startrubrik(url,sub)  