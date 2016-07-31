#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, os, urlparse,json
import xbmc ,xbmcgui, xbmcaddon,xbmcvfs
import urllib2,urllib,json
import shutil
import re,md5
import socket, cookielib
import feedparser
import HTMLParser


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
  
wid = xbmcgui.getCurrentWindowId()
window=xbmcgui.Window(wid)
window.show()
  
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

# Soll Twitter Api Resetter Werden
#if len(sys.argv) > 1:
#    params = parameters_string_to_dict(sys.argv[2])
#    mode = urllib.unquote_plus(params.get('mode', ''))
    


        
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
    xbmc.log("Twitter:  Starte Plugin")
    oldfeeds=""
    schown=[]
    monitor = xbmc.Monitor()   
    while not monitor.abortRequested():
      xbmc.log("Hole Umgebung")
      bild=__addon__.getSetting("bild") 
      lesezeit=__addon__.getSetting("lesezeit")
      greyout=__addon__.getSetting("greyout")
      Feed=__addon__.getSetting("Feed")
      if not oldfeeds==Feed:
        schown=[]
        oldfeeds=Feed
      #channelr,channels,sendungr,sendungs,videor,videos=readersetzen()           
      feed = feedparser.parse(Feed)      
      debug("--Feed--")
      debug(feed)
      debug("----")
      for ii, item in enumerate(feed.entries):   
          if 'description' in item:
                inhalt = item.description 
          if 'content' in item:                         
            inhalt=item.content[0].value
          #convert news text into plain text
          inhalt = re.sub('<p[^>\\n]*>','\n\n',inhalt)
          inhalt = re.sub('<br[^>\\n]*>','\n',inhalt)
          inhalt = re.sub('<[^>\\n]+>','',inhalt)
          inhalt = re.sub('\\n\\n+','\n\n',inhalt)
          inhalt = re.sub('(\\w+,?) *\\n(\\w+)','\\1 \\2',inhalt)  
          inhalt = HTMLParser.HTMLParser().unescape(inhalt)
          title=item.title
          if 'published_parsed' in item:
                sdate=time.strftime('%d %b %H:%M',item.published_parsed)
          else:
              sdate=''            
          try:
              maxwidth=0
              if 'media_thumbnail' in item:
                  for img in item.media_thumbnail:
                        w=1
                        if 'width' in img: w=img['width']
                        if w>maxwidth:
                            cimg=img['url']
                            maxwidth=w
              if 'enclosures' in item:
                  for img in item.enclosures:
                        if re.search('\.(png|jpg|jpeg|gif)',img.href.lower()):
                            cimg = img.href
                        elif 'type' in img:
                            if img.type.lower().find('image') >= 0:
                                cimg = img.href
          except:                
                pass
          if cimg:
                cimg = cimg.replace('&amp;','&') #workaround for bug in feedparser                   
          #debug("Content:" + inhalt)
          debug("-----------------")
          debug("Datum"+ sdate)
          debug("-----------------")
          debug("Immage"+ cimg)
          debug("-----------------")
          if not bild=="true":
             cimg=""
          if title not in schown:
            #savemessage(title,cimg,greyout,lesezeit) 
            savemessage(title,cimg,greyout,lesezeit)             
            schown.append(title)
                   
      if monitor.waitForAbort(60):
        break            
      
           
      
