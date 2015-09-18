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



# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
debuging=""
# Es geht um Videos
xbmcplugin.setContent(addon_handle, 'movies')
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
defaultBackground = ""
defaultThumb = ""


profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
m3ulistdir=xbmc.translatePath( os.path.join( temp, 'm3u', '') ).decode("utf-8")



# Anlegen von Directorys
if xbmcvfs.exists(m3ulistdir):
  shutil.rmtree(m3ulistdir)
xbmcvfs.mkdirs(m3ulistdir)

if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)


xbmcvfs.mkdirs(temp)
xbmcvfs.mkdirs(m3ulistdir)


def clearSubTempDir(pfad):

        files = os.listdir(pfad)
        for file in files:
          try:
            os.remove(xbmc.translatePath(pfad+"/"+file))
          except:
            pass
            
def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
  
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

def playlive(url):    
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)


def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
  
   


def geturl(url,ref=""):
   cj = cookielib.CookieJar()  
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   req = urllib2.Request(url)
   req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')
   if not ref=="":
     req.add_header('Referer', ref)
   inhalt = urllib2.urlopen(req).read()   
   return inhalt
   
def getstream(url)   :
   debug("URL1:" + url)
   inhalt = geturl(url) 
   kurz_inhalt = inhalt[inhalt.find('<div class="webcam1">')+1:]
   kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</div>')]
   match=re.compile('<script src="([^"]+)" type="text/javascript" language="javascript"></script>', re.DOTALL).findall(kurz_inhalt)
   url2=match[0]
   debug("URL2:" + url2)
   inhalt = geturl(url2)
   match=re.compile('<iframe src="([^"]+)" name="webcam"', re.DOTALL).findall(inhalt)
   url3=match[0] 
   debug ("URL3:"+ url3)
   inhalt=geturl(url=url3 , ref=url)
   match=re.compile("ipadUrl: escape\('([^']+)'", re.DOTALL).findall(inhalt)
   url4=match[0]
   inhalt = geturl(url4)
   clearSubTempDir(m3ulistdir)
   playlist=m3ulistdir+"playlist.m38u"
   debug ("Playlist: "+ playlist)
   fh = open(playlist, 'wb')
   fh.write(inhalt)
   fh.close()
   playlive(playlist)
   
   
       
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
showName = urllib.unquote_plus(params.get('showName', ''))
hideShowName = urllib.unquote_plus(params.get('hideshowname', '')) == 'True'
nextPage = urllib.unquote_plus(params.get('nextpage', '')) == 'True'
einsLike = urllib.unquote_plus(params.get('einslike', '')) == 'True'    

# Haupt Menu Anzeigen      
if mode is '':    
    addLink("Wirtsbudenstrasse" , url="https://streams.muenchen.tv/wiesncam/wiesencam1.stream_1/jwplayer.m3u8", mode="playlive", iconimage="https://www.muenchen.tv/storage/thumbs/366x/r:1442558753/125465.jpg",duration="",desc="")    
    addLink("Hofbräu Festzelt" , url="https://streams.muenchen.tv/wiesncam/wiesencam2.stream_1/jwplayer.m3u8", mode="playlive", iconimage="https://www.muenchen.tv/storage/thumbs/366x/r:1442558715/125467.jpg",duration="",desc="")    
    addLink("Schausteller Strasse", url="http://www.wiesn.tv/livestream-webcam/schaustellerstrasse", mode="getstream", iconimage="http://www.wiesn.tv/images/smartslider/webcam-schausteller-kachel.jpg",duration="",desc="")        
    addLink("Loewenbraeuturm", url="http://www.wiesn.tv/livestream-webcam/loewenbraeuturm", mode="getstream", iconimage="http://www.wiesn.tv/images/smartslider/webcam-loewenbraeu-kachel.jpg",duration="",desc="")        
    addLink("Ochsenbraterei", url="http://www.wiesn.tv/livestream-webcam/webcam-ochsenbraterei", mode="getstream", iconimage="http://www.wiesn.tv/images/smartslider/webcam-grillrider-kachel.jpg",duration="",desc="")        
    addLink("Oberhalb der Bavaria", url="http://www.wiesn.tv/livestream-webcam/webcam-oberhalb-der-bavaria", mode="getstream", iconimage="http://www.wiesn.tv/images/smartslider/webcam-arabella-kachel.jpg",duration="",desc="")        
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:  
  if mode == 'playlive':
          playlive(url)     
  if mode == 'getstream':
          getstream(url)   
