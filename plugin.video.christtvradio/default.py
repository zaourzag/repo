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


addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
#xbmcplugin.setContent(addon_handle, 'movies')
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')

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
   
def addDir(name, url, mode, iconimage, desc=""):  
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)  
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre=''):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setArt({"fanart": iconimage})
  #liz.setProperty("fanart_image", defaultBackground)
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
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
  
def geturl(url):
   cj = cookielib.CookieJar()
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   req = urllib2.Request(url)
   inhalt = urllib2.urlopen(req).read()   
   return inhalt

def playstream(url):
  listitem = xbmcgui.ListItem(path=url)  
  xbmcplugin.setResolvedUrl(addon_handle,True, listitem)  
   
def llist(filter=""):
   debug("Filter "+ filter)
   content=geturl("http://rps.christtvradio.de/groupsctrlist.m3u")
   ##EXTINF:-1 tvg-id="" tvg-name="" tvg-shift="" radio="true" tvg-logo="RADIO7ALBANIA.png" group-title="Albanian",Radio 7 Albania (ALB)
   #http://cp6.serverse.com:7025/live

   spl=content.split("#EXTINF:")   
   radios=[]
   groups=[]
   names=[]
   urls=[]
   bilder=[]
   for i in range(1,len(spl),1):
      entry=spl[i]
      debug("entry :"+entry)
      if filter in entry:  
        try:      
          lines=entry.split("\n")
          url=lines[1].strip() 
          line=lines[0].replace('radio=""','radio="X"')
          debug("Line :"+line)
          daten=re.compile('radio="(.+?)" tvg-logo="(.+?)" group-title="(.+?)",(.+)', re.DOTALL).findall(line)[0]
          debug("DATEN")
          debug(daten)
          urls.append(url)
          debug("1")          
          radios.append(daten[0])
          debug("2")
          bilder.append(daten[1])          
          debug("3")
          groups.append(daten[2])       
          debug("4")
          names.append(daten[3])
          debug("5")
        except:
          pass 
   groups, radios,names,urls,bilder = (list(x) for x in zip(*sorted(zip(groups, radios,names,urls,bilder))))          
   for i in range(1,len(names),1):
    if 'true' in radios[i]:
       name = names[i]+" ( Radio"
    else:
       name = names[i]+" ( TV"
    name=name+" , "+groups[i]+" )"
    url=urls[i]
    logo=bilder[i]
    addLink(name, url, "playstream", "http://rps.christtvradio.de/lgs/"+logo)
   
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)        
   
def sprache():
    content=geturl("http://rps.christtvradio.de/groupsctrlist.m3u")
    groulist=[]
    gruppen=re.compile('group-title="(.+?)"', re.DOTALL).findall(content)
    for gruppe in gruppen:
      if not gruppe in groulist:
          addDir(gruppe, gruppe, "Gruppe","")
          groulist.append(gruppe)
       
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
    

# Haupt Menu Anzeigen      
if mode is '':
    addDir(translation(30001), translation(30001), "TV","")
    addDir(translation(30002), translation(30002), "Radio","")
    addDir(translation(30004), translation(30004), "sprache","")   
    addDir(translation(30003), translation(30003), "ALL","")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'TV':
          llist('radio=""')
  if mode == 'Gruppe':
          llist('group-title="'+ url+'"')          
  if mode == 'Radio':
          llist('radio="true"')              
  if mode == 'ALL':
          llist('')                 
  if mode == "playstream":
          playstream(url)
  if mode == "sprache":
          sprache()          