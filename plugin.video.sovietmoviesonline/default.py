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
from datetime import datetime

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
global substitle
substitle=addon.getSetting("substitle")
global text
text=addon.getSetting("text")
global mainurl
mainurl="http://sovietmoviesonline.com"

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
def ersetze(inhalt):
   inhalt=inhalt.replace('&#39;','\'')  
   inhalt=inhalt.replace('&quot;','"')    
   inhalt=inhalt.replace('&gt;','>')      
   inhalt=inhalt.replace('&amp;','&') 
   return inhalt
   
def addDir(name, url, mode, iconimage, desc="",year=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground
    liz.setProperty("fanart_image", iconimage)
  else:
    liz.setProperty("fanart_image", defaultBackground)
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  

def addLink(name, url, mode, iconimage, desc="", duration="",year=""):
    debug("Addlink")
    addonID = addon.getAddonInfo('id')
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+str(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc,"Year": year})
    liz.setProperty('IsPlayable', 'true')
    liz.setProperty("fanart_image", iconimage)
    liz.addContextMenuItems([(translation(30007), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
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
  
def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title

def geturl(url):
   debug("geturl url :"+url)
   cj = cookielib.CookieJar()
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   req = urllib2.Request(url)
   inhalt = urllib2.urlopen(req).read()   
   return inhalt
  
    
def menu():
    global text
    if text=="EN":
      url=mainurl+"/en/"
    else:
       url=mainurl
    inhalt = geturl(url)        
    kurz_inhalt = inhalt[inhalt.find('<!--mobile menu-->')+1:]
    kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<noindex>')]   
    match=re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(kurz_inhalt)
    for url,name in match:
       addDir(name, url, "Filme", "", desc="")

def Filme(url):  
  content = geturl(mainurl+url)   
  spl = content.split('<!--smallMovie-->')
  for i in range(1, len(spl), 1):
    entry = spl[i]
    match=re.compile('<div class="year".+?>(.+?)</div>', re.DOTALL).findall(entry)
    year=match[0]
    match=re.compile('href="(.+?)"', re.DOTALL).findall(entry)
    url=match[0]
    match=re.compile('src="(.+?)"', re.DOTALL).findall(entry)
    bild=match[0]
    debug("Bild : "+ mainurl+bild)
    match=re.compile('<div class="smallTitle">(.+?)</div>', re.DOTALL).findall(entry)
    title1=match[0]
    match=re.compile('</div>([^<]+)</div>', re.DOTALL).findall(entry)
    title2=match[0]
    title=cleanTitle(title2) +" ( "+ title1 +" )"
    addLink(title, url, "Playvideo", mainurl+bild, desc="",year=year)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
  
def Playvideo(url):
  content = geturl(url)   
  match=re.compile('<source src="(.+?)"', re.DOTALL).findall(content)
  file=match[0]  
  if not "http" in file:
    file=mainurl+file
  try:
      match=re.compile('track src="(.+?)"', re.DOTALL).findall(content)
      sub=match[0]
      subfilecontent = geturl(mainurl+sub)
      subFile=temp+"/sub.srt"
      fh = open(subFile, 'wb')
      fh.write(subfilecontent)
      fh.close()
  except:
     sub=""
     subFile=""
  debug("File: "+file)
  debug("sub: "+sub)  
  listitem = xbmcgui.ListItem(path=file)  
  listitem.setSubtitles([subFile])
  xbmcplugin.setResolvedUrl(addon_handle,True, listitem)  

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))


# Haupt Menu Anzeigen      
if mode is '':
    menu()   
    addDir(translation(30002), translation(30002), 'Settings', "")   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'Filme':
          Filme(url)
  if mode == 'Playvideo':
          Playvideo(url)  