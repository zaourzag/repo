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


xbmcplugin.setContent(addon_handle, 'movies')

baseurl="https://bvbtotal.de/"
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
    addDir("Settings","Settings","Settings","")
    starturl="https://www.arte.tv/de/"
    content=geturl(starturl)
    htmlPage = BeautifulSoup(content, 'html.parser')
    elemente = htmlPage.find_all("li",attrs={"class":"next-menu-nav__item"})
    for element in elemente:
       link=element.find("a")
       name=link.text
       url=link["href"]
       if (not "Programm" in name) and (not "Home" in name) and (not "360" in name) and (not "Magazin" in name) and (not "Edition" in name) and (not "Digitale" in name) and (not "Live" in name):
            addDir(name, url, "subrubrik","")
    xbmcplugin.endOfDirectory(addon_handle) 
def subrubrik(surl):
  content=geturl(surl)
  htmlPage = BeautifulSoup(content, 'html.parser')
  elemente = htmlPage.find_all("li",attrs={"class":"next-menu-nav__item"})
  anz=0
  for element in elemente :
        if '"'+surl+'"' in str(element):
            debug(element)
            debug("------")
            try:                                                      
                elemente2=element.find_all("li",attrs={"class":"next-menu-nav__item"})                                                                  
                debug("++++++++++++")
                debug(elemente2)
                for element in elemente2:                                        
                        debug(element)
                        debug("+++++++")
                        link=element.find("a")
                        url=link["href"]
                        name=link.text
                        addDir(name, url, "videoliste","")
                        anz=1
            except:
                pass
  if anz==0:
     videoliste(surl)
  xbmcplugin.endOfDirectory(addon_handle) 
  
  
def playvideo(url):      
 vid = YDStreamExtractor.getVideoInfo(url,quality=2) #quality is 0=SD, 1=720p, 2=1080p and is a maximum
 stream_url = vid.streamURL()
 stream_url=stream_url.split("|")[0]
 listitem = xbmcgui.ListItem(path=stream_url)  
 xbmcplugin.setResolvedUrl(addon_handle,True, listitem) 
    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
referer = urllib.unquote_plus(params.get('referer', ''))
page = urllib.unquote_plus(params.get('page', ''))
nosub= urllib.unquote_plus(params.get('nosub', ''))

def videoliste(url,page="1"):  
  debug("Start Videoliste")
  debug(url)
  #https://www.arte.tv/guide/api/api/zones/de/web/videos_subcategory_OPE?page=2&limit=10
  #https://www.arte.tv/sites/de/webproductions/api/?lang=de&paged=3  
  if int(page)==1:
    content=geturl(url)
    #,"nextPage":"https:\u002F\u002Fapi-cdn.arte.tv\u002Fapi\u002Femac\u002Fv2\u002Fde\u002Fweb\u002Fzones\u002Fvideos_subcategory_OPE?page=2&limit=10"
    content=re.compile(' window.__INITIAL_STATE__ = ({.+})', re.DOTALL).findall(content)[0]    
    strukturs = json.loads(content)
    debug("###")
    debug(strukturs)
    sub=strukturs["pages"]["list"]
    key=sub.keys()[0]
    sub2=sub[key]["zones"]
    debug(sub2)
    for zone in sub2:
      if "videos" in zone["code"]:
         code=zone["code"]
         break
    url="https://www.arte.tv/guide/api/api/zones/de/web/"+code
  jsonurl=url+"?page="+page+"&limit=100"    
  content=geturl(jsonurl)
  struktur = json.loads(content)
  for element in struktur["data"]:
     video_url=element["url"]
     video_title=element["title"]
     video_subtitle=element["subtitle"]
     if not video_subtitle==None:
       video_title = video_title + " - "+video_subtitle
     video_desc=element["description"]
     video_image=element["images"]["landscape"]["resolutions"][-1]["url"]
     video_duration=element["duration"]
     addLink(video_title,video_url,"playvideo",video_image,duration=video_duration,desc=video_desc)
  debug(url)
  try:
    debug("Next try:")
    nextpage=struktur["nextPage"]
    debug(nextpage)
    debug("Endnext")
    if not nexpage == None:
        addDir("Next",url,"videoliste","",page=int(page)+1)
  except:
    pass
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
  if mode == 'subrubrik':
          subrubrik(url)
  if mode == 'videoliste':
          videoliste(url,page)  