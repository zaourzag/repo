#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import os
import re
import xbmcplugin
import xbmcaddon,xbmc
import xbmcgui,json,cookielib
import requests


addon = xbmcaddon.Addon()
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
translation = addon.getLocalizedString

cj = cookielib.LWPCookieJar();
language = str(addon.getSetting("language"))


try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

cachezeit=addon.getSetting("cachetime")   
cache = StorageServer.StorageServer("plugin.video.L0RE.cinetrailer", cachezeit) # (Your plugin name, Cache time in hours



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


def addLink(name, url, mode, iconimage, duration="", desc="", genre='',text=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name"+urllib.quote_plus(name)+"&text="+urllib.quote_plus(text)+"&bild="+iconimage
	ok = True
	liz = xbmcgui.ListItem(name, iconImage="", thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
	liz.setProperty('IsPlayable', 'true')
	liz.addStreamInfo('video', { 'duration' : duration })
	liz.setProperty("fanart_image", iconimage)
	#liz.setProperty("fanart_image", defaultBackground)
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok

def addDir(name, url, mode, iconimage, desc="",text="",page=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&text="+str(text)+"&page="+str(page)+"&name"+str(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
page = urllib.unquote_plus(params.get('page', ''))

def index():  
  addDir("Neueste Trailer","https://res.cinetrailer.tv/api/v1/"+language+"/movies/newest?pageSize=20&isDebug=false","newlist","",page=1)
  addDir("Demnächst im Kino","https://res.cinetrailer.tv/api/v1/"+language+"/movies/comingsoon?pageSize=20&isDebug=false","newlist","",page=1)
  addDir("Home Video","https://res.cinetrailer.tv/api/v1/"+language+"/movies/homevideo?pageSize=20&isDebug=false","newlist","",page=1)
  addDir("Im Kino","https://res.cinetrailer.tv/api/v1/"+language+"/movies/incinemas?orderBy=&pageSize=20&isDebug=false","newlist","",page=1)
  addDir("Genres","","genres","")
  addDir("Settings", "", 'Settings', "")
  xbmcplugin.endOfDirectory(pluginhandle)   


def getUrl(url,method,allow_redirects=False,verify=False,cookies="",headers="",data=""):
   if method=="GET":
     content = requests.get(url,allow_redirects=allow_redirects,verify=verify,cookies=cookies,headers=headers,data=data).text.encode('utf-8')
   if method=="POST":
     content = requests.post(url,data=data, allow_redirects=allow_redirects,verify=verify,cookies=cookies).text.encode('utf-8')
   return content
   
def genres():
  url="https://res.cinetrailer.tv/api/v1/"+language+"/categories"
  token=getsession()
  values = {
      'Model' : 'Huawei MLA-TL10',
      'AppVersion' : '3.3.15',
      'OsVersion': '4.4.4',
      'OsName': 'android',
      'Market': 'android',   
      'Authorization': 'Bearer '+token,
      #'TimeStamp': '2017-09-04 11:04:45'
  }  
  content = cache.cacheFunction(getUrl,url,"GET",False,False,cj,values)
  struktur = json.loads(content)
  for genre in struktur["categories"]:
    idd=genre["id"]
    title=genre["title"].encode('utf-8')
    url="https://res.cinetrailer.tv/api/v1/"+language+"/movies/search?pageSize=20&desc=true&orderBy=date&categoryId="+str(idd)
    addDir(title,url,"newlist","",page=1)
  xbmcplugin.endOfDirectory(pluginhandle)     
  
def getsession():
  url="https://res.cinetrailer.tv/Token"
  values = {
      'client_id' : 'cinetrailer_android',
      'client_secret' : 'pKQvtSL9FdpB3u38GMHtNMA3',
      'grant_type': 'client_credentials',
    } 
  content = cache.cacheFunction(getUrl,url,"POST",False,False,cj,"",values)    
  struktur = json.loads(content)
  return struktur["access_token"]
def Play(url):
    token=getsession()
    values = {
      'Model' : 'Huawei MLA-TL10',
      'AppVersion' : '3.3.15',
      'OsVersion': '4.4.4',
      'OsName': 'android',
      'Market': 'android',   
      'Authorization': 'Bearer '+token,
      #'TimeStamp': '2017-09-04 11:04:45'
    }  
    urln="https://res.cinetrailer.tv/api/v1/"+language+"/movie/"+url+"/trailers"  


    quality = str(addon.getSetting("quality"))

    content = cache.cacheFunction(getUrl,urln,"GET",False,False,cj,values)    
    struktur = json.loads(content)
    debug("PLAY")
    debug("URLN :"+urln)
    debug(struktur)
    url=struktur["items"][0]["clips"][0]["url"]
    for video in struktur["items"][0]["clips"]:
      if quality==video["quality"]:
          url=video["url"]
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)  
    debug(struktur)
    
def newlist(url,page=1):
   token=getsession()  
   nurl=url +"&pageNumber="+str(page)
   debug("URL newlist :"+url)
   values = {
      'Model' : 'Huawei MLA-TL10',
      'AppVersion' : '3.3.15',
      'OsVersion': '4.4.4',
      'OsName': 'android',
      'Market': 'android',   
      'Authorization': 'Bearer '+token,
      #'TimeStamp': '2017-09-04 11:04:45'
    }  
   debug("Newlist url :"+url)
   content = cache.cacheFunction(getUrl,nurl,"GET",False,False,cj,values)    
   struktur = json.loads(content)
   debug(struktur)
   count=0
   for trailer in struktur["items"]:
      id=trailer["id"]
      image=trailer["poster_high"]
      name=trailer["title"].encode('utf-8')
      addLink(name,str(id),"Play",image)
      count+=1
   if int(struktur["page_count"]) > int(page):
     debug("## NEXT ##")
     addDir("Next",url,"newlist","",page=str(int(page)+1))
   xbmcplugin.endOfDirectory(pluginhandle) 
if mode == "":
    index()
if mode == "newlist":
     newlist(url,page)
if mode == "Play":
     Play(url)
if mode == "genres":
     genres()
if mode == 'Settings':
          addon.openSettings()      