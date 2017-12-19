#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import httplib
import socket
import sys
import re
import os
import random
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc,json

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.servustv_com'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceView") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
defaultFanart = os.path.join(addonDir ,'fanart.png')
siteVersion = addon.getSetting("siteVersion")
siteVersion = ["de-de", "de-at"][int(siteVersion)]
viewMode = str(addon.getSetting("viewID"))
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')]
urlMain = "http://www.servustv.com"
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

def addLink(name, url, mode, iconimage, desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+str(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    liz.setProperty('IsPlayable', 'true')
    if useThumbAsFanart and iconimage!=icon:
        liz.setProperty("fanart_image", iconimage)
    liz.addContextMenuItems([(translation(30007), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage,ttype=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&ttype="+str(ttype)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart and iconimage!=icon:
        liz.setProperty("fanart_image", defaultFanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
ttype = urllib.unquote_plus(params.get('ttype', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
  

def getUrl(url,data="x"):        
        debug("Get Url: " +url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        userAgent = "Dalvik/2.1.0 (Linux; U; Android 5.0;)"
        opener.addheaders = [('User-Agent', userAgent),
        ('Accept-Language',siteVersion),
         ('Authorization',"DeviceId 427502496159111")        
        ]
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

        
def index():
  addDir(translation(30001), "https://api.servustv.com/videolists?start&broadcast_limit=5", 'startseite', defaultFanart)
  addDir(translation(30008), "https://api.servustv.com/topics", 'topics', defaultFanart)
  addDir("Serien", "https://api.servustv.com/series", 'series', defaultFanart)
  addLink(translation(30011), "", 'playLiveStream', defaultFanart)
  xbmcplugin.endOfDirectory(pluginhandle)
  
def topics(url):
  content=getUrl(url)
  struktur = json.loads(content) 
  for element in struktur["topics"]:
      title=element["title"]
      idd=str(element["id"])
      addDir(title, idd, 'subtopic', "")            
  xbmcplugin.endOfDirectory(pluginhandle)              
def subtopic(idd):
  url="https://api.servustv.com/topics/"+idd+"/series?vod_only&broadcast_limit=50&limit=500"  
  content=getUrl(url)
  struktur = json.loads(content) 
  for element in struktur["series"]:
      ids=str(element["id"])
      title=element["title"].encode("utf-8")
      try:
        image=element["images"][0]["url"].encode("utf-8")
      except:
        image=""
      addDir(title, ids, 'serie', image) 
  url="https://api.servustv.com/topics/"+idd+"/broadcasts?vod_only&no_series=&broadcast_limit=5"
  content=getUrl(url)
  struktur = json.loads(content)  
  debug(struktur)
  for element in struktur["broadcasts"]:
      ids=str(element["id"])
      title=element["title"].encode("utf-8")
      subtitle=element["subtitle"].encode("utf-8")
      try:
        image=element["images"][0]["url"].encode("utf-8")
      except:
        image=""
      addLink(title+" - "+subtitle, ids, 'Play', image)       
  xbmcplugin.endOfDirectory(pluginhandle)  

def series():
  url="https://api.servustv.com/series"
  content=getUrl(url)
  struktur = json.loads(content) 
  for element in struktur["series"]:
      ids=str(element["id"])
      title=element["title"].encode("utf-8")
      try:
        image=element["images"][0]["url"].encode("utf-8")
      except:
        image=""
      addDir(title, ids, 'serie', image) 
  xbmcplugin.endOfDirectory(pluginhandle)  

def serie(idd):    
    url="https://api.servustv.com/series/"+idd+"?vod_only&broadcast_limit=100"
    content=getUrl(url)
    struktur = json.loads(content) 
    for element in  struktur["series"]["broadcasts"]:
        name=element["title"].encode("utf-8")
        subtitle=element["subtitle"].encode("utf-8")
        dauer=str(element["vod_duration"])
        ids=str(element["id"])
        image=element["images"][0]["url"].encode("utf-8")
        addLink(name +" - "+subtitle, ids, "Play", image, desc="", duration=dauer)                
    xbmcplugin.endOfDirectory(pluginhandle) 
  
def startseite(url,ttype=""):
       content=getUrl(url)
       struktur = json.loads(content) 
       for element in  struktur["videolists"]:
          debug(element)
          title=element["title"]
          debug("title :"+title) 
          debug("Type :"+ttype)
          if ttype=="":
            addDir(title, url, 'startseite', "",ttype=title)            
          else:
            if ttype=="Alle" or title==ttype:
                for element2 in element["broadcasts"]:
                   name=element2["title"].encode("utf-8")
                   subtitle=element2["subtitle"].encode("utf-8")
                   dauer=str(element2["vod_duration"])
                   idd=str(element2["id"])
                   #desc=element2["description"]
                   image=element2["images"][0]["url"].encode("utf-8")
                   addLink(name +" - "+subtitle, idd, "Play", image, desc="", duration=dauer)                
       if ttype=="":
        addDir("Alle", url, 'startseite', "",ttype="Alle")          
       xbmcplugin.endOfDirectory(pluginhandle)        





def Play(idd):
    url="https://api.servustv.com/broadcasts/"+idd
    content=getUrl(url)
    struktur = json.loads(content)
    playurl=struktur["broadcast"]["vod_hls_link"]
    listitem = xbmcgui.ListItem(path=playurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


    
def playLiveStream():
    debug( "siteVersion :"+siteVersion)
    if siteVersion=="de-de":    
                streamUrl="http://hdiosstv-f.akamaihd.net/i/servustvhdde_1@75540/index_2592_av-p.m3u8"    
    else: 
                streamUrl="http://hdiosstv-f.akamaihd.net/i/servustvhd_1@51229/index_2592_av-p.m3u8"    
    listitem = xbmcgui.ListItem(path=streamUrl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)







if mode == 'startseite':
    startseite(url,ttype)       
elif mode == 'Play':
    Play(url)    
elif mode == 'topics':
    topics(url)    
elif mode == 'subtopic':
    subtopic(url)    
elif mode == 'serie':
    serie(url)        
elif mode == 'series':
    series()       
elif mode == 'playLiveStream':
    playLiveStream()           
elif mode == 'Settings':
          addon.openSettings()
else:
    index()
