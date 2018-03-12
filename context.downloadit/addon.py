#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon
import xbmcgui,xbmcvfs
import json,urllib2,re,urlparse,os
import pyxbmct
import requests,cookielib
from difflib import SequenceMatcher
import time,datetime
import YDStreamUtils
import YDStreamExtractor


try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

   
cachezeit=24  
cache = StorageServer.StorageServer("context.serieninfos", cachezeit) # (Your plugin name, Cache time in hours

addon = xbmcaddon.Addon()

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
session = requests.session()

if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       

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
  
  
def geturl(url,data="x",header=""): 
   
    headers = {'User-Agent':         'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0', 
    }        
    ip=addon.getSetting("ip")
    port=addon.getSetting("port")    
    if not ip=="" and not port=="":
      px="http://"+ip+":"+str(port)
      proxies = {
        'http': px,
        'https': px,
      }    
      content = session.get(url, allow_redirects=True,verify=False,headers=headers,proxies=proxies)    
    else:
      content = session.get(url, allow_redirects=True,verify=False,headers=headers)    
    return content.text


    

addon = xbmcaddon.Addon()    
debug("Hole Parameter")
debug("Argv")
debug(sys.argv)
debug("----")
try:
      params = parameters_string_to_dict(sys.argv[2])
      mode = urllib.unquote_plus(params.get('mode', ''))
      series = urllib.unquote_plus(params.get('series', ''))
      season = urllib.unquote_plus(params.get('season', ''))
      debug("Parameter Holen geklappt")
except:
      debug("Parameter Holen nicht geklappt")
      mode="" 
debug("Mode ist : "+mode)
folder=addon.getSetting("folder")
ffmpg=addon.getSetting("ffmpg")
quality=addon.getSetting("quality")
debug("FOLDER :"+folder)
if mode=="":   
 path = xbmc.getInfoLabel('ListItem.FileNameAndPath')
 title = xbmc.getInfoLabel('ListItem.Title')
 kodi_player = xbmc.Player()
 listitem = xbmcgui.ListItem(path=path)
 listitem.setInfo(type="Video", infoLabels={"Title": title})
 kodi_player.play(path,listitem)
 time.sleep(10)
 videoda=0
 while videoda==0 :
  try:
    file=kodi_player.getPlayingFile()
    debug("-----> "+file)
    if not file=="":
      videoda=1
  except:
    pass 
 debug("Start Download")
 debug("FILE :"+file)
 YDStreamExtractor.overrideParam('ffmpeg_location',ffmpg)
 YDStreamExtractor.overrideParam('preferedformat',"avi") 
 #YDStreamExtractor.overrideParam('title',title) 
 vid = YDStreamExtractor.getVideoInfo(file,quality=int(quality)) 
 #kodi_player.stop()
 with YDStreamUtils.DownloadProgress() as prog: #This gives a progress dialog interface ready to use
    try:
        YDStreamExtractor.setOutputCallback(prog)
        result = YDStreamExtractor.downloadVideo(vid,folder)
        if result:
            #success
            full_path_to_file = result.filepath
        elif result.status != 'canceled':
            #download failed
            error_message = result.message
    finally:
        YDStreamExtractor.setOutputCallback(None)
