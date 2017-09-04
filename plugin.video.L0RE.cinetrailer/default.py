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
  #ListRubriken("http://"+language2+".euronews.com","",x=1)
  addDir("Neueste Trailer","https://res.cinetrailer.tv/api/v1/de/movies/newest?pageSize=20&isDebug=false","newlist","",page=1)
  addDir("Demnächst im Kino","https://res.cinetrailer.tv/api/v1/de/movies/comingsoon?pageSize=20&isDebug=false","newlist","",page=1)
  addDir("Home Video","https://res.cinetrailer.tv/api/v1/de/movies/homevideo?pageSize=20&isDebug=false","newlist","",page=1)
  addDir("Im Kino","https://res.cinetrailer.tv/api/v1/de/movies/incinemas?orderBy=&pageSize=20&isDebug=false","newlist","",page=1)
  addDir("Genres","","genres","")
  xbmcplugin.endOfDirectory(pluginhandle)   
  
def genres():
  url="https://res.cinetrailer.tv/api/v1/de/categories"
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
  content = requests.get(url,allow_redirects=False,verify=False,cookies=cj,headers=values).text.encode('utf-8')
  struktur = json.loads(content)
  for genre in struktur["categories"]:
    idd=genre["id"]
    title=genre["title"].encode('utf-8')
    url="https://res.cinetrailer.tv/api/v1/de/movies/search?pageSize=20&desc=true&orderBy=date&categoryId="+str(idd)
    addDir(title,url,"newlist","",page=1)
  xbmcplugin.endOfDirectory(pluginhandle)     
  
def getsession():
  url="https://res.cinetrailer.tv/Token"
  values = {
      'client_id' : 'cinetrailer_android',
      'client_secret' : 'pKQvtSL9FdpB3u38GMHtNMA3',
      'grant_type': 'client_credentials',
    } 
  content = requests.post(url,data=values, allow_redirects=False,verify=False,cookies=cj)
  struktur = json.loads(content.text)
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
    urln="https://res.cinetrailer.tv/api/v1/de/movie/"+url+"/trailers"    
    content = requests.get(urln,allow_redirects=False,verify=False,cookies=cj,headers=values).text.encode('utf-8')
    struktur = json.loads(content)
    url=struktur["items"][0]["clips"][-1]["url"]
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
   content = requests.get(nurl,allow_redirects=False,verify=False,cookies=cj,headers=values).text.encode('utf-8')
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