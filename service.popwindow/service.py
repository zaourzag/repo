#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, os, urlparse
import xbmc ,xbmcgui, xbmcaddon,xbmcvfs
import urllib2,urllib,json
import re,md5,shutil
import socket, cookielib



__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__addondir__    = xbmc.translatePath( __addon__.getAddonInfo('path') )
background = os.path.join(__addondir__,"bg.png")

profile    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
translation = __addon__.getLocalizedString
  
wid = xbmcgui.getCurrentWindowId()
window=xbmcgui.Window(wid)
window.show()

if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)
       
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

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
def geturl(url):
   req = urllib2.Request(url)
   inhalt = urllib2.urlopen(req).read()   
   return inhalt   
   

def showMessage(Message,image="",greyout="true",lesezeit=10):
    global alles_anzeige
    global urlfilter
    global background
    global window
    #tw=unicode(Message).encode('utf-8')
    tw=Message
    tw=tw.replace("&amp;","&")
    xbmc.log("showMessage")
    wid = xbmcgui.getCurrentWindowId()
    window=xbmcgui.Window(wid)
    res=window.getResolution()    
    if len(tw) > 100 :
       bis=100
       for i in range(90,100):
         if tw[i]==' ':
           bis=i
    else:
        bis=len(tw)
    zeile1=tw[:bis]
    rest=tw[bis:]
    if len(rest) > 100 :
       bis=100
       for i in range(90,100):
         if rest[i]==' ':
           bis=i
    else:
        bis=len(rest)
    zeile2=rest[:bis]   
    zeile3=rest[bis:]  
    if zeile1:
        ll=70
    if zeile2:
        ll=100
    if zeile3: 
        ll=130
        
    if greyout=="true":
       bg=xbmcgui.ControlImage(0,10,3000,ll,"")
       bg.setImage(background)
       window.addControl(bg)

    twitterlabel1=xbmcgui.ControlLabel (111, 31, 3000, 100, zeile1,textColor='0xFF000000')
    twitterlabel2=xbmcgui.ControlLabel (110, 30, 3000, 100, zeile1,textColor='0xFFFFFFFF')        
    window.addControl(twitterlabel1)
    window.addControl(twitterlabel2)        
    if zeile2:
     twitterlabel3=xbmcgui.ControlLabel (111, 61, 3000, 100, zeile2,textColor='0xFF000000')
     twitterlabel4=xbmcgui.ControlLabel (110, 60, 3000, 100, zeile2,textColor='0xFFFFFFFF')
     window.addControl(twitterlabel3)
     window.addControl(twitterlabel4)
    if zeile3:
     twitterlabel5=xbmcgui.ControlLabel (111, 91, 3000, 100, zeile3,textColor='0xFF000000')
     twitterlabel6=xbmcgui.ControlLabel (110, 90, 3000, 100, zeile3,textColor='0xFFFFFFFF')
     window.addControl(twitterlabel5)
     window.addControl(twitterlabel6) 
    avatar=xbmcgui.ControlImage(0,10,100,100,"")
    avatar.setImage(image)
    window.addControl(avatar)        
    time.sleep(int(lesezeit))
        
    window.removeControl(twitterlabel1)
    window.removeControl(twitterlabel2)
    if zeile2:
       window.removeControl(twitterlabel3)
       window.removeControl(twitterlabel4)
    if zeile3:
       window.removeControl(twitterlabel5)
       window.removeControl(twitterlabel6)       
    window.removeControl(avatar)
    if greyout=="true":
       window.removeControl(bg)
      
        
           
if __name__ == '__main__':
    temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
    monitor = xbmc.Monitor()       
    while not monitor.abortRequested():
      text=[]
      image=[]
      greyout=[]
      fileliste=[]
      datumliste=[]
      dirs, files = xbmcvfs.listdir(temp)      
      for name in files:     
          pf=os.path.join( temp, name)     
          zeit=os.path.getctime(pf)
          fileliste.append(name)
          datumliste.append(zeit)          
      if len(datumliste) > 0:
        datumliste,fileliste = (list(x) for x in zip(*sorted(zip(datumliste,fileliste))))
        for name in fileliste:
          debug("File :" + name)
          f = open(temp+"/"+name, 'r')    
          for line in f:      
                message,image,grey,lesezeit=line.split("###")         
                showMessage(message,image,grey,lesezeit)
          f.close()           
          xbmcvfs.delete(temp+"/"+name)                    
      xbmc.log("Hole Umgebung")  
      time.sleep(int(20))      
      if monitor.waitForAbort(60):
        break            
           

