#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, os, urlparse,json
import xbmc ,xbmcgui, xbmcaddon,xbmcvfs
import urllib2,urllib,json
import shutil
import re,md5
import socket, cookielib
import feedparser
import HTMLParser,xbmcplugin
from dateutil import parser

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__addondir__    = xbmc.translatePath( __addon__.getAddonInfo('path') )
background = os.path.join(__addondir__,"bg.png")

profile    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
translation = __addon__.getLocalizedString

popupaddon=xbmcaddon.Addon("service.popwindow")
popupprofile    = xbmc.translatePath( popupaddon.getAddonInfo('profile') ).decode("utf-8")
popuptemp       = xbmc.translatePath( os.path.join( popupprofile, 'temp', '') ).decode("utf-8")
  
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
defaultBackground = ""
defaultThumb = ""


def geturl(url):
   debug("geturl url : "+url)
   cj = cookielib.CookieJar()
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   req = urllib2.Request(url)
   inhalt = urllib2.urlopen(req).read()   
   return inhalt
   
def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
    
# Einlesen von Parametern, Notwendig für Reset der Twitter API
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

if not xbmcvfs.exists(temp):
   xbmcvfs.mkdirs(temp)



def addDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})	
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
        iconimage = defaultBackground
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultBackground)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre=''):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
    liz.setProperty('IsPlayable', 'true')
    liz.addStreamInfo('video', { 'duration' : duration })
    liz.setProperty("fanart_image", iconimage)
    #liz.setProperty("fanart_image", defaultBackground)
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok
    
        
def savemessage(message,image,grey,lesezeit)  :
    message=unicode(message).encode('utf-8')
    image=unicode(image).encode('utf-8')
    debug("message :"+message)
    debug("image :"+image)
    debug("grey :"+grey)
    debug("popuptemp :"+popuptemp)
    debug("lesezeit :"+str(lesezeit))
    filename=md5.new(message).hexdigest()  
    f = open(popuptemp+"/"+filename, 'w')    
    f.write(message+"###"+image+"###"+grey+"###"+str(lesezeit))
    f.close()   
    

  
    
  
   
if __name__ == '__main__':
    cimg=""
    xbmc.log("FussballPupup:  Starte Plugin")

    schown=[]
    monitor = xbmc.Monitor()   
    
    while not monitor.abortRequested():
      titlelist=[]
      cimglist=[]
      greyoutlist=[]
      lesezeitlist=[]
      timelist=[] 
      xbmc.log("Hole Umgebung")
      bild=__addon__.getSetting("bild") 
      lesezeit=__addon__.getSetting("lesezeit")
      greyout=__addon__.getSetting("greyout")
      filename       = xbmc.translatePath( os.path.join( temp, 'spiel.txt') ).decode("utf-8")
      gesamtliste=[]
      if xbmcvfs.exists(filename) :
        fp=open(filename,"r") 
        content=fp.read()
        fp.close()          
        liste=content.split("\n")                
        for spiel in liste:   
          if  "##" in spiel:       
            arr=spiel.split("##")
            name=arr[0]
            live_status=arr[1]
            lieganr=arr[2]
            dayid=arr[3]     
            spielnr=arr[4]            
            if live_status=="full":
               url="https://api.sport1.de/api/sports/liveticker/co"+lieganr+"/ma"+spielnr
               content=geturl(url)
            else:
               url="https://api.sport1.de/api/sports/match-event/ma"+spielnr
               content=geturl(url)
            debug("-----------------------------------------------------------------------------------------------------")
            debug(content)
                #    titlelist.append(title)
                #    cimglist.append("")
                #    greyoutlist.append(greyout)
                #    lesezeitlist.append(lesezeit) 
                #    #Donnerstag, 4. August 2016 16:07                           
                #    dt = parser.parse(sdate)                    
                #    day_string = dt.strftime('%Y-%m-%d %H:%M')                    
                #    timelist.append(day_string)
                #    timelist,titlelist,cimglist,lesezeitlist,greyoutlist = (list(x) for x in zip(*sorted(zip(timelist,titlelist,cimglist,lesezeitlist,greyoutlist))))
        for i in range(len(titlelist)):                      
                  savemessage(titlelist[i],cimglist[i],greyoutlist[i],lesezeitlist[i])             
                  schown.append(title)                   
      if monitor.waitForAbort(60):
        break            
      
           
      
