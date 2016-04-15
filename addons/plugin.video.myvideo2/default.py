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
from StringIO import StringIO
import xml.etree.ElementTree as ET
import binascii
import time
from datetime import datetime
import hashlib
import random

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
baseurl="http://www.myvideo.de"
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
defaultBackground = ""
defaultThumb = ""


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
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground
    liz.setProperty("fanart_image", iconimage)
  else:
    liz.setProperty("fanart_image", defaultBackground)
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',id=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  if id != "" :
    u=u+"&id="+str(id)
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

def abisz():
  letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
  for letter in letters:
    if letter=="a":
     lettern=""
    else:
      lettern=letter
    url="http://www.myvideo.de/serien/alle_serien_a-z/"+lettern
    addDir(letter.lower(), url, 'Buchstabe', "")
  addDir("0-9", "0-9", 'Buchstabe', "")
  xbmcplugin.endOfDirectory(addon_handle)
  
def Buchstabe(url):
  debug(url)
  content=geturl(url)
  try:      
      match=re.compile('<a href="([^"]+)" class="button as-prev">', re.DOTALL).findall(content)
      zurueck=match[0]
      addDir("Zurueck", "http://www.myvideo.de"+zurueck, 'Buchstabe',"")
  except:
      pass
  match=re.compile('window.MV.contentListTooltipData = {(.+?)};', re.DOTALL).findall(content)
  jsonf=match[0]
  struktur = json.loads("{"+jsonf+"}") 
  videos=struktur["items"]
  for video in videos:
    url= video["linkTarget"]
    try :
      desc= unicode(video["description"]).encode("utf-8")
    except:
      desc=""
    title=unicode(video["title"]).encode("utf-8")
    thump= video["thumbnail"]
    thump=thump.replace("ez","mv")
    addDir(title, "http://www.myvideo.de"+url, 'Staffel', thump,desc)
  try:            
      match=re.compile('<a href="([^"]+)" class="button as-next">', re.DOTALL).findall(content)
      vor=match[0]
      addDir("Vor", "http://www.myvideo.de"+vor, 'Buchstabe',"")
  except:
      pass
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

  
def Staffel(url):
    content=geturl(url)
    match=re.compile('data-list-name="season_tab([^"]+)" data-url="(.+?)"', re.DOTALL).findall(content)
    for staffel,url in match:      
       try:
          xy=int(staffel)
          staffel= "Staffel "+staffel
       except:
          pass
       addDir(staffel, "http://www.myvideo.de"+url, 'Serie',"","")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
def Serie(url):
  content=geturl(url)
  debug("URL :" + url)
  folgen = content.split('<div class="videolist--item">')
  for i in range(1, len(folgen), 1):
    folge=folgen[i]                   
    match=re.compile('href="(.+?)"', re.DOTALL).findall(folge)  
    url=match[0]
    match=re.compile('title="(.+?)"', re.DOTALL).findall(folge)
    name=match[0]
    match=re.compile('src="(.+?)"', re.DOTALL).findall(folge)
    thumnail=match[0]
    match=re.compile('"thumbnail--subtitle">(.+?)</div>', re.DOTALL).findall(folge)   
    sub=match[0]
    addLink(name + " ( "+ sub +" )", "http://www.myvideo.de"+url, 'playvideo',thumnail,"")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
  
def playvideo(url):  
 
 debug("-----------")
 debug(" URL : "+url)
 match=re.compile('.+?-m-(.+)', re.DOTALL).findall(url)
 video_id=match[0]
 salt = "dfCc3ca+3baf2e8%beGa508!cbcdbG0f"
 client_location = urllib.quote_plus(url)
 access_token = "MVKolibri"
 client_name = "kolibri-2.6.16"
 #callback = "_player1_mvas0"
 
 url = "https://mls.myvideo.de/mvas/videos?access_token="+ access_token+"&client_location="+client_location+"&client_name="+client_name+"&ids="+video_id+"&callback="
 content=geturl(url)
 debug(content)
 struktur = json.loads(content)
 title = struktur[0]["title"];
 struct=struktur[0]["sources"]
 debug(struct)
 ids =""
 for element in struct:
    ids=ids + str(element["id"])
    ids=ids +","
 ids=ids[:-1]
	
 debug("ids : "+ ids)
 m1 = hashlib.sha1()
 m1.update(video_id + salt + access_token + client_location + salt +client_name)
 name=m1.hexdigest()
 client_id =  salt[0:2] + name
 newurl="https://mls.myvideo.de/mvas/videos/"+ video_id +"/server?access_token="+ access_token +"&client_location="+ client_location+"&client_name="+ client_name +"&client_id="+ client_id +"&callback="
 content=geturl(newurl)
 struktur = json.loads(content)
 server_id=struktur["server_id"]
 m2 = hashlib.sha1()
 m2.update(salt +  video_id + access_token +server_id + client_location+ ids + salt + client_name)
 name=m2.hexdigest()
 client_id = salt[0:2] +name
 url="https://mls.myvideo.de/mvas/videos/"+ video_id +"/sources?access_token="+ access_token +"&client_location="+ client_location +"&client_name="+ client_name +"&client_id="+ client_id +"&server_id="+ server_id +"&ids="+ ids +"&callback="
 content=geturl(url)
 struktur = json.loads(content)
 struct=struktur["sources"]
 urlm3u8=""
 for name in struct:
     if name["mime_type"]=="application/x-mpegURL" :
        urlm3u8=name["url"]
 if urlm3u8=="":
   for name in struct:
      debug(name)
      debug("-----")
      if name["mime_type"]=="video/mp4" or name["mime_type"]=="video/x-flv" :
         stream=name["url"]
         reg_str = re.compile('rtmpe?://(.*?)/(.*?)/(.*)', re.DOTALL).findall(stream)         
         server=reg_str[0][0]
         pfad=reg_str[0][1]
         datei=reg_str[0][2]
         swf = "http://component.p7s1.com/kolibri/2.12.9/myvideo/premium/kolibri.swf";
         urlm3u8="rtmp://"+ server +"/"+pfad +"/ swfVfy=1 swfUrl=" + swf +" playpath="+ datei
         debug("-+-+-+")
         debug(urlm3u8)
         
   
 listitem = xbmcgui.ListItem(title, path=urlm3u8, thumbnailImage="")
 xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
 debug(" ENDE : "+ urlm3u8)

  
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
id = urllib.unquote_plus(params.get('id', ''))
# Haupt Menu Anzeigen      

if mode is '':
    addDir("Alle Serien", "Alle Serien", 'abisz', "")
    #addDir("Alle Film", "Alle Film", 'allfilms', "")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'abisz':
          abisz()
  if mode == 'Buchstabe':
          Buchstabe(url)
  if mode == 'Serie':
          Serie(url)
  if mode == 'Staffel':
          Staffel(url)          
  if mode == 'playvideo':
          playvideo(url)
