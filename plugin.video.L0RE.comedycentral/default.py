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

baseurl="http://www.comedycentral.tv"
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
  content=geturl(baseurl+"/shows/alle")
  htmlPage = BeautifulSoup(content, 'html.parser')  
  subpart = htmlPage.find("div",attrs={"class":"shows_lst teaser_collection"})
  serien = subpart.find_all("li")
  for serie in serien:
     link=serie.find("a")["href"]
     image=serie.find("img")["src"]
     text=serie.find("h3").text
     addDir(text,baseurl+link,"serie",image)  
  xbmcplugin.endOfDirectory(addon_handle)
  
def staffel(url):  
  content=geturl(url)
  htmlPage = BeautifulSoup(content, 'html.parser')  
  try:
    subpart = htmlPage.find("div",attrs={"class":"related_episodes"})
    folgen = subpart.find_all("li")
    for folge in folgen:
        try:
            token=folge["data-token"]
            image=folge.find("img")["src"]
            try:
                episodenr=folge.find("span",attrs={"class":"episode_number"}).text
            except:
                episodenr=0
            title=folge.find("a")["title"]
            addLink(episodenr +" - "+title,token,"playvideo",image)
        except:
            pass
  except:
     dialog = xbmcgui.Dialog()
     dialog.notification("Error", 'Keine Videos Gefunden', xbmcgui.NOTIFICATION_ERROR)
  xbmcplugin.endOfDirectory(addon_handle)
  
def serie(url):  
  content=geturl(url)
  htmlPage = BeautifulSoup(content, 'html.parser')  
  try:
    subpart = htmlPage.find("ul",attrs={"class":"related_seasons"})
    staffeln = subpart.find_all("li")
    for sstaffel in staffeln:
        link=sstaffel.find("a")["href"]
        text=sstaffel.find("a").text
        addDir(text,baseurl+link,"staffel","")  
    xbmcplugin.endOfDirectory(addon_handle)
  except:
     staffel(url)

def playvideo(idd):
   url="http://api.mtvnn.com/v2/de/DE/local_playlists/"+idd+".json?video_format=m3u8" 
   content=geturl(url)
   struktur = json.loads(content)     
   file=struktur["local_playlist_videos"][0]["url"]
   listitem = xbmcgui.ListItem(path=file)
   xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
  
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
# Haupt Menu Anzeigen      
if mode is '':
     liste()   
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'serie':
          serie(url)
  if mode == 'staffel':
          staffel(url)
  if mode == 'playvideo':
          playvideo(url)