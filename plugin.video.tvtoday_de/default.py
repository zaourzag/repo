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
import datetime



global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])

args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()

mainurl="http://www.tvtoday.de"
# Lade Sprach Variablen
translation = addon.getLocalizedString
defaultBackground = ""



def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def addDir(name, url, mode, iconimage, desc="", id="0", add=0, dele=0): 
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)  
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  liz.setProperty("fanart_image", iconimage)
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',shortname="",zeit="",production_year="",abo=1,search=""):
  debug ("addLink abo " + str(abo))
  debug ("addLink abo " + str(shortname))
  cd=addon.getSetting("password")  
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage="", thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre,"Sorttitle":shortname,"Dateadded":zeit,"year":production_year })
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
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
  
  
def getUrl(url,data="x",header=""):        
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())        
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
             #print e.code   
             cc=e.read()  
             debug("Error : " +cc)
       
        opener.close()
        return content

def thema(thema):
   main=getUrl(mainurl+"/mediathek/")
   kurz_inhalt = main[main.find('<h3 class="h3 uppercase category-headline">'+thema+'</h3>')+1:]
   kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<h3 class="h3 uppercase category-headline">')]
   spl = kurz_inhalt.split('<div class="slide js-')     
   for i in range(0, len(spl), 1):
      element=spl[i]
      try:
        debug("Image")
        image=re.compile('data-lazy-load-src="(.+?)"', re.DOTALL).findall(element)[0]
        debug(image)
        debug("Thema")
        thema=re.compile('<p class="h7 name">(.+?)</p>', re.DOTALL).findall(element)[0]
        debug(thema)
        debug("Sender")
        sender=re.compile('<span class="h6 text">(.+?)</span>', re.DOTALL).findall(element)[0]                                                 
        debug(sender)
        debug("URL")  
        url=re.compile('<a href="([^\"]+?)" class="element js-hover', re.DOTALL).findall(element)[0]
        debug(url)
        debug("-------------")
        if not sender=="RTL" and  not sender=="VOX" and not sender=="ZDF" :
          addLink(thema, url, 'folge', image)                
      except:
        pass
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)        

def folge(url):
  main=getUrl(mainurl+url) 
  kurz_inhalt = main[main.find('<div class="img-wrapper stage">')+1:]
  url=re.compile('<a href="([^\"]+?)"', re.DOTALL).findall(kurz_inhalt)[0]
  debug ("Folge URL :"+url)
  if "ardmediathek" in url:      
      debug("URL ARD:"+ url)
      id=re.compile('documentId=([0-9]+)', re.DOTALL).findall(url)[0]
      debug("ID :"+id)
      import libArd
      videoUrl,subUrl = libArd.getVideoUrl(id)
      listitem = xbmcgui.ListItem(path=videoUrl)
      xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
  if "zdf.de" in url:
      #dialog = xbmcgui.Dialog()
      #dialog.ok("ZDF","Zdf fehlt die schnitstelle,bin bin Membrane dran")
      #import libZdf
      #xy=libZdf.libZdfGetVideoHtml('https://www.zdf.de/comedy/neo-magazin-mit-jan-boehmermann/neo-magazin-royale-vom-27-10-2016-102.html')
      #xy=libZdf.libZdfGetVideoHtml(url)      
      debug("Url: ")
      debug (xy)
      
  if "arte.tv" in url:   
   VID = re.compile("http://www.arte.tv/guide/de/([^/]+?)/", re.DOTALL).findall(url)[0]
   pluginID="plugin.video.arte_tv"
   plugin = xbmcaddon.Addon(id=pluginID)
   finalUrl = "plugin://"+plugin.getAddonInfo('id') +"/?mode=play-video&id="+VID
   listitem = xbmcgui.ListItem(path=finalUrl)
   xbmcplugin.setResolvedUrl(addon_handle, True, listitem)   

#  username=addon.getSetting("user")  

#country=re.compile('<meta property="og:url" content="http://www.daisuki.net/(.+?)/top.html"', re.DOTALL).findall(main)[0]
#          header = [('User-Agent', 'userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'),
#                    ("Referer", "http://www.daisuki.net/"+country+"/top.html")]      
#          content=getUrl("https://www.daisuki.net/bin/SignInServlet.html/input",data,header)                                  
#          for cookief in cj:
#            print cookief
#            if "key" in str(cookief):
#          struktur = json.loads(cxc) 
#                        cj.save(cookie,ignore_discard=True, ignore_expires=True)                
#cookie=temp+"/cookie.jar"
#cj = cookielib.LWPCookieJar();

#if xbmcvfs.exists(cookie):
#    cj.load(cookie,ignore_discard=True, ignore_expires=True)

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")


#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
      

       
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
#xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
#xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    #kurz_inhalt = content[content.find('<!-- moviesBlock start -->')+1:]
    #kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<!-- moviesBlock end  -->')]

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
    
if mode is '':
    main=getUrl(mainurl+"/mediathek/")
    Themen=re.compile('<h3 class="h3 uppercase category-headline">(.+?)</h3>', re.DOTALL).findall(main)
    debug("Themen :")
    debug(Themen)
    for thema in Themen:
      addDir(thema, thema, 'thema', "")                
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
else:         
  if mode == 'delserie':
          delserie(url)
  if mode == 'thema':
          thema(url)                 
  if mode == 'folge':
          folge(url)              