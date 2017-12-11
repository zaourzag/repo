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
import base64
import requests
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser
import streamlink.session


pluginhandle = int(sys.argv[1])

icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')



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
   
  
def addDir(name, url, mode, thump, desc="",page=1,nosub=0):   
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&nosub="+str(nosub)
  ok = True
  liz = xbmcgui.ListItem(name)  
  liz.setArt({ 'fanart' : thump })
  liz.setArt({ 'thumb' : thump })
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
  

def getUrl(url,data="x"):    
        print("#"+url+"#")            
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        userAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 10_2_1 like Mac OS X) AppleWebKit/602.4.6 (KHTML, like Gecko) Version/10.0 Mobile/14D27 Safari/602.1"
        opener.addheaders = [('User-Agent', userAgent)]        
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
             dialog = xbmcgui.Dialog()
             nr=dialog.ok("Error", error)
             return ""
             
        opener.close()
        return content

def resolve(url, quality='best'):

    try:

        session = streamlink.session.Streamlink()
        # session.set_loglevel("debug")
        # session.set_logoutput(sys.stdout)
        plugin = session.resolve_url(url)
        debug("------------> ")
        debug(plugin)
        streams = plugin.get_streams()
        debug("----->")
        debug(streams)
        streams = repr(streams[quality])
        link = streams.partition('(\'')[2][:-3]

        return link

    except:
        pass
        

def listvideos(url):
    content=getUrl(url)
    videourl=re.compile('"requestPath":"(.+?)"', re.DOTALL).findall(content)[0]    
    content=getUrl(videourl.replace("\/","/"))
    debug(content)
    content=re.compile('pageContent":"(.+)"', re.DOTALL).findall(content)[0]    
    content=content.replace("\\t","\t").replace("\\n","\n").replace('\\"',"").replace("\\/","/")
    debug(content)
    htmlPage = BeautifulSoup(content, 'html.parser')  
    debug("++++++----")
    debug(    htmlPage)
    videos=htmlPage.find_all("div",{"class" :"item"})  
    for video in videos:
      bild = video.find("img")["src"]
      links=video.find("a",{"class":"media-data"})
      title = links.text
      link="http://www.ustream.tv"+ video.find("a")["href"]
      #link = links["data-mediaid"]
      try:
        LIVE=video.find("span",{"class":"badge-live"}).text      
      except:
        LIVE=""
      if "Live" in LIVE:
         title=title +" ( Live )"
      addLink(title,link,"play",bild)
      debug("--------->")
      debug(video)
    xbmcplugin.endOfDirectory(pluginhandle)          
    
def play(url):
  debug(url)
  urlv=resolve(url)
  debug("XYXYXYXYXYXY")
  debug(urlv)
  listitem = xbmcgui.ListItem(path=urlv)   
  addon_handle = int(sys.argv[1])  
  xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
def liste():
   url="http://www.ustream.tv/explore/all"
   content=getUrl(url)
   htmlPage = BeautifulSoup(content, 'html.parser')   
   themen=htmlPage.find("div",{"class" :"submenu"})   
   elemente=themen.findAll("a")
   for element in elemente:
      addDir(element.text.strip("\t\n").strip(),element["href"],"listvideos","")
   xbmcplugin.endOfDirectory(pluginhandle)          


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
referer = urllib.unquote_plus(params.get('referer', ''))
page = urllib.unquote_plus(params.get('page', ''))
nosub= urllib.unquote_plus(params.get('nosub', ''))

   
if mode is '':
     liste()   
if mode == 'Settings':
          addon.openSettings()
if mode == 'playvideo':
          playvideo(url)
if mode == 'listvideos':
          listvideos(url)
if mode == 'play':
          play(url)  