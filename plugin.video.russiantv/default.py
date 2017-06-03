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


# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString


xbmcplugin.setContent(addon_handle, 'movies')

icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
bitrate=addon.getSetting("bitrate")

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
      
def addDir(name, url, mode, thump, desc="",page=1,xtype="",datum=""):  
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&xtype="+xtype+"&datum="+datum
  ok = True
  liz = xbmcgui.ListItem(name)  
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

    
def geturl(url,data="x",header=""):
        global cj
        debug("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))        
        userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"
        if header=="":
          opener.addheaders = [('User-Agent', userAgent)]        
        else:
          opener.addheaders = header        
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #debug( e.code )  
             cc=e.read()  
             debug("Error : " +cc)
       
        opener.close()
        cj.save(cookie,ignore_discard=True, ignore_expires=True) 
        return content


def tvone():
    url="http://www.1tv.ru/live"
    content = geturl(url)    
    for cook in cj:
      debug("++++++")      
      s=urllib.quote_plus(cook.value)
    url2="http://stream.1tv.ru/api/playlist/1tvch_as_array.json?r=2116258"
    content = geturl(url2)
    debug("URL2:")
    debug(content)
    match = re.compile('"(http:.+?)"', re.DOTALL).findall(content)    
    url3=match[0]+"&s="+s
    content = geturl(url3) 
    debug(content)
    listitem = xbmcgui.ListItem(path=url3)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
   
def ntv():
   url="http://www.ntv.ru/#air"
   content = geturl(url)
   match = re.compile("hlsURL = '(.+?)'", re.DOTALL).findall(content)
   url2=match[0]  
   listitem = xbmcgui.ListItem(path="http:"+url2)   
   xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
   
page=0   
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
page = urllib.unquote_plus(params.get('page', ''))
name = urllib.unquote_plus(params.get('name', ''))
xtype = urllib.unquote_plus(params.get('xtype', ''))
datum = urllib.unquote_plus(params.get('datum', ''))


        
# Haupt Menu Anzeigen      
if mode is '':
    addLink("1TV", "http://www.1tv.ru/live", 'tvone', "")
    addLink("NTV", "http://www.ntv.ru/#air", 'ntv', "")
    #addLink("Прямой эфир", "http://live.russia.tv/index/index/channel_id/82", 'channel_82', "")    
    #addDir(translation(30001), translation(30001), 'Settings', "")   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'tvone':
          tvone()
  if mode == 'ntv':
          ntv()