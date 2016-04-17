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
   
def addDir(name, url, mode, iconimage, desc="",offset="",tab=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  if offset!="":
     u=u+"&offset="+str(offset)
  if tab!="":
     u=u+"&tab="+str(tab)
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
   
def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()    
    return title
    
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
    debug("Staffel : "+ url)
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
    name=cleanTitle(match[0])
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
      if name["mime_type"]=="video/x-flv" :
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

def allfilms(url):
 content=geturl(url)
 try:      
      match=re.compile('<a href="([^"]+)" class="button as-prev">', re.DOTALL).findall(content)
      zurueck=match[0]
      addDir("Zurueck", "http://www.myvideo.de"+zurueck, 'allfilms',"")
 except:
      pass
 folgen = content.split('<div class="grid--item as-dvd-cover is-video">')
 for i in range(1, len(folgen), 1):
     try:
      debug("-----")
      folge=folgen[i]
      match=re.compile('<img class="thumbnail--pic" src=".+?" data-src="(.+?)"', re.DOTALL).findall(folge) 
      thump=match[0]
      match=re.compile('<a href="(.+?)" class="grid--item-title">(.+?)</a> ', re.DOTALL).findall(folge) 
      name=cleanTitle(match[0][1])
      url=match[0][0]
      try:
        match=re.compile('<use xlink:href="#icon-duration">.+?([0-9]+?)h ([0-9]+?)m</div>', re.DOTALL).findall(folge) 
        std=match[0][0]
        min=match[0][1]
        laenge=int(std)*60*60 + int(min)*60     
      except:
        laenge=""
      addLink(name , "http://www.myvideo.de"+url, 'playvideo',thump,duration=laenge)
     except:
       pass
 try:            
      match=re.compile('<a href="([^"]+)" class="button as-next">', re.DOTALL).findall(content)
      vor=match[0]
      addDir("Vor", "http://www.myvideo.de"+vor, 'allfilms',"")
 except:
      pass
 xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     

def  top100():
  addDir("Top Music Genres", "Top Music Genres", 'topgenres', "")
  addDir("Top100 Music Clips", "http://www.myvideo.de/top_100/top_100_musik_clips", 'top_zeit', "")  
  addDir("Top 25 Single Charts", "http://www.myvideo.de/top_100/top_100_single_charts", 'topliste', "")  
  addDir("Top 100 Entertainment", "http://www.myvideo.de/top_100/top_100_entertainment", 'top_zeit', "")
  addDir("Top 100 Serien", "http://www.myvideo.de/top_100/top_100_serien", 'top_zeit', "")
  addDir("Top 100 Filme", "http://www.myvideo.de/filme/top_100_filme", 'allfilms', "")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
def topgenres():
  addDir("Top 100 Pop", "http://www.myvideo.de/top_100/top_100_pop", 'topliste', "")
  addDir("Top 100 Rock", "http://www.myvideo.de/top_100/top_100_rock", 'topliste', "")
  addDir("Top 100 Hip Hop", "http://www.myvideo.de/top_100/top_100_hiphop", 'topliste', "")
  addDir("Top 100 Electro", "http://www.myvideo.de/top_100/top_100_elektro", 'topliste', "")
  addDir("Top 100 Schlager", "http://www.myvideo.de/top_100/top_100_schlager", 'topliste', "")
  addDir("Top 100 Metal", "http://www.myvideo.de/top_100/top_100_metal", 'topliste', "")
  addDir("Top 100 RnB", "http://www.myvideo.de/top_100/top_100_rnb", 'topliste', "")
  addDir("Top 100 Indie", "http://www.myvideo.de/top_100/top_100_indie", 'topliste', "")
  addDir("Top 100 Jazz", "http://www.myvideo.de/top_100/top_100_jazz", 'topliste', "")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def filme_menu():
   addDir("Alle Filme", "http://www.myvideo.de/filme/alle_filme", 'allfilms', "")
   addDir("Alle Filme - Datum", "http://www.myvideo.de/filme/alle_filme/datum", 'allfilms', "")
   addDir("Top Filme", "http://www.myvideo.de/filme/top_100_filme", 'allfilms', "")
   addDir("Kino Trailer", "http://www.myvideo.de/filme/kino-dvd-trailer", 'mischseite', "")
   addDir("Film Genres", "Film Genres", 'filmgenres', "")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
def filmgenres():
   addDir("Action", "http://www.myvideo.de/filme/action", 'allfilms', "")
   addDir("Horror", "http://www.myvideo.de/filme/horror", 'allfilms', "")
   addDir("Sci-Fi", "http://www.myvideo.de/filme/sci-fi", 'allfilms', "")
   addDir("Thriller", "http://www.myvideo.de/filme/thriller", 'allfilms', "")
   addDir("Drama", "http://www.myvideo.de/filme/drama", 'allfilms', "")
   addDir("Comedy", "http://www.myvideo.de/filme/comedy", 'allfilms', "")
   addDir("Western", "http://www.myvideo.de/filme/western", 'allfilms', "")
   addDir("Dokumentationen", "http://www.myvideo.de/filme/dokumentation", 'allfilms', "")
   addDir("Erotik", "http://www.myvideo.de/filme/erotik", 'allfilms', "")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
def top_zeit(url):
  addDir("Heute", url, 'topliste', "")
  addDir("Woche", url+"/woche", 'topliste', "")
  addDir("Monat",  url+"/monat", 'topliste', "")
  addDir("Ewig",  url+"/ewig", 'topliste', "")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def topliste(url):  
   content=geturl(url)
   videos = content.split('<div class="chartlist--videolist-item">')
   for i in range(1, len(videos), 1):
     video=videos[i]
     debug("-------------->")
     debug(video)
     debug("-------------->")
     match=re.compile('<div class="chartlist--videolist-item-position"> (.+?) </div>', re.DOTALL).findall(video) 
     nr=match[0]
     match=re.compile('href="(.+?)"', re.DOTALL).findall(video) 
     url=match[0]
     match=re.compile('title="(.+?)"', re.DOTALL).findall(video) 
     title=cleanTitle(match[0])
     match=re.compile('data-src="(.+?)"', re.DOTALL).findall(video) 
     thump=match[0]
     try:
       match=re.compile('</svg>Zur Serie: (.+?) </a>', re.DOTALL).findall(video) 
       serie=cleanTitle(match[0])
     except:
       serie=""
     try:
        match=re.compile('icon-duration"></use> </svg> ([0-9]+?):([0-9]+?) </span>', re.DOTALL).findall(video) 
        min=match[0][0]
        sek=match[0][1]
        laenge=int(min)*60 + int(sek)        
     except:
         laenge=""    
     if  not "http://www.myvideo.de" in url:
       url="http://www.myvideo.de"+url
     if serie!="":
       addLink(nr +". "+serie +" ( "+ title +" )" , url, 'playvideo',thump,duration=laenge)
     else:
       addLink(nr +". "+title , url, 'playvideo',thump,duration=laenge)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
   
def mischseite(url):
   debug("URL: mischseite"+url)
   content=geturl(url)
   namen=re.compile('>([^>]+?)</a> <span class="tabs--tab', re.DOTALL).findall(content)      
   if len(namen)==0:
      namen=re.compile('<span class="tabs--tab.+?> ([^<]+?) </span>', re.DOTALL).findall(content)      
   debug(namen)
   nr=0
   liste=[]
   for name in namen:
       if "{{{" in name:
         continue
       if "Facebook" in name:
         continue        
       if not name in liste:         
         liste.append(name)       
         addDir(name, url, 'misch_tab', "",tab=nr)
         nr=nr+1  
   match2=re.compile('</use> </svg>([^<]+?)</h3> <div class="videolist.+?data-url="(.+?)"', re.DOTALL).findall(content)    
   for name, urll in match2:
      addDir(cleanTitle(name), "http://www.myvideo.de"+ urll, 'misch_cat_auto', "",offset=0)
   match=re.compile('sushibar.+?-url="(.+?)"', re.DOTALL).findall(content)     
   for urll in match:
      if "_partial"in urll:
         debug("--- URLL :"+urll)
         content2=geturl( "http://www.myvideo.de"+urll)
         match=re.compile('<h2 class="sushi--title">(.+?)</h2>', re.DOTALL).findall(content2)           
         name=cleanTitle(match[0])
         if "sushi--title-link" in name:
           match=re.compile('>(.+?)</a>', re.DOTALL).findall(name)           
           name=cleanTitle(match[0])
         if "</svg>" in name:
            match=re.compile('\<\/svg\>(.+)', re.DOTALL).findall(name)       
            name=match[0]            
         if "icon-label-live" in name:
             continue
         if not name in liste:
           liste.append(name) 
           if  not "http://www.myvideo.de" in urll:
              urll="http://www.myvideo.de"+urll
           addDir(name, urll, 'misch_cat', "",offset=0)

   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def misch_tab(url,tab): 
   debug(" misch_tab url "+ url)
   debug(" misch_tab tab "+ str(tab))
   content=geturl(url)   
   if '<div class="tabs--content' in content:
       Tabs = content.split('<div class="tabs--content">')
   else:
       Tabs = content.split('<div class="videolist')   
   liste=Tabs[int(tab)]
   if '<a class="thumbnail is-video sushi--item' in liste:
      videos = liste.split('<a class="thumbnail is-video sushi--item')
   else :
      videos = liste.split('<div class="videolist--item">')   
   for i in range(1, len(videos), 1): 
         url_reg=re.compile('href="(.+?)"', re.DOTALL).findall(videos[i])            
         url=url_reg[0]
         thump_reg=re.compile('src="(.+?)"', re.DOTALL).findall(videos[i])   
         thump=thump_reg[0]
         namen=re.compile('<div class="thumbnail--maintitle">(.+?)</div>', re.DOTALL).findall(videos[i])   
         name=cleanTitle(namen[0])
         try:
           subt_reg=re.compile('<div class="thumbnail--subtitle">(.+?)</div> ', re.DOTALL).findall(videos[i])   
           sub=cleanTitle(subt_reg[0])
           name=name +" ( "+ sub +" )"
         except:
           pass
         if  not "http://www.myvideo.de" in url:
             url="http://www.myvideo.de"+url
         if "-m-" in url:
           addLink(name , url, 'playvideo',thump)
         else:
           addDir(name , url, 'mischseite',thump)
         

   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   #<div class="sushibar
   #data-url="/_partial/sushibar/11932"
   #<h2 class="sushi--title"> DVD/BluRay </h2>
def misch_cat_auto(url,offset):
   urln=url+"?ajaxoffset="+ offset
   debug("URL misch_cat_auto: "+ urln)
   content=geturl(urln)
   folgen = content.split('<a class')
   i=0
   for i in range(1, len(folgen), 1):
        folge=folgen[i]
        match=re.compile('href="(.+?)" title="(.+?)"', re.DOTALL).findall(folge)
        urlname=match[0][0]
        name=cleanTitle(match[0][1])
        try:
          match=re.compile('src="(.+?)"', re.DOTALL).findall(folge)
          thump=match[0]
        except:
          thump=""        
        if  not "http://www.myvideo.de" in urlname:
            urlname="http://www.myvideo.de"+urlname
        if "-m-" in urlname:
           addLink(name , urlname, 'playvideo',thump)
        else:
           addDir(name , urlname, 'mischseite',thump)
   addDir("Next" , url, 'misch_cat_auto',"",offset=str(int(offset)+i+1))
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
   
def misch_cat(url,offset):
   urln=url+"?ajaxoffset="+ offset
   debug("misch_cat URL : "+ urln)
   content=geturl(urln)
   match=re.compile('data-preloaded="(.+?)"', re.DOTALL).findall(content)   
   anz=int(match[0])
   folgen = content.split('<a class=')
   i=0
   for i in range(1, len(folgen), 1):
        debug("---------")
        debug(folgen[i])
        debug("---------")
        folge=folgen[i]
        match=re.compile('href="(.+?)"', re.DOTALL).findall(folge)
        urlname=match[0]
        try:
          match=re.compile('alt="(.+?)"', re.DOTALL).findall(folge)        
          name=cleanTitle(match[0])
        except:
           continue
        try:
          match=re.compile('data-src="(.+?)"', re.DOTALL).findall(folge)
          thump=match[0]
        except:
          thump=""
        try:
          match=re.compile('<div class="thumbnail--subtitle">(.+?)</div>', re.DOTALL).findall(folge)
          sub=cleanTitle(match[0])
          name= name +" ( "+ sub +" )"        
        except:
          pass           
        if  not "http://www.myvideo.de" in urlname:
            urlname="http://www.myvideo.de"+urlname
        if "-m-" in urlname:
           addLink(name , urlname, 'playvideo',thump)
        else:
           addDir(name , urlname, 'mischseite',thump)
   if i>=anz:
        addDir("Next" , url, 'misch_cat',"",offset=str(int(offset)+i+1))
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def tvmenu():
    addDir("Alle Serien", "Alle Serien", 'abisz', "")
    addDir("Anime", "http://www.myvideo.de/serien/anime_tv", 'mischseite', "")
    addDir("Top 100 Serien", "http://www.myvideo.de/top_100/top_100_serien", 'top_zeit', "")
    addDir("Serien Highlight", "http://www.myvideo.de/serien/weitere_serien", 'mischseite', "")    
    addDir("Serien in OV", "http://www.myvideo.de/serien/serien-in-ov", 'mischseite', "") 
    addDir("Kids", "http://www.myvideo.de/serien/kids", 'mischseite', "") 
    addDir("BBC", "http://www.myvideo.de/serien/bbc", 'mischseite', "")    
    addDir("Pro 7", "http://www.myvideo.de/serien/prosieben", 'mischseite', "")    
    addDir("Sat 1", "http://www.myvideo.de/serien/sat_1", 'mischseite', "")    
    addDir("Sixx", "http://www.myvideo.de/serien/sixx", 'mischseite', "")    
    addDir("Pro 7 Maxx", "http://www.myvideo.de/serien/prosieben_maxx", 'mischseite', "")    
    addDir("Pro 7 Maxx Anime", "http://www.myvideo.de/serien/prosieben_maxx_anime", 'mischseite', "")    
    addDir("Kabel Eins", "http://www.myvideo.de/serien/kabel_eins", 'mischseite', "")    
    addDir("Sat 1 Gold", "http://www.myvideo.de/serien/sat_1_gold", 'mischseite', "")    
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
def themenmenu():
    addDir("WWE", "http://www.myvideo.de/themen/wwe", 'mischseite', "")
    addDir("Webstars", "http://www.myvideo.de/webstars", 'mischseite', "")
    addDir("Fußball", "http://www.myvideo.de/themen/sport/fussball", 'mischseite', "")
    addDir("Fashion", "http://www.myvideo.de/themen/videofashion", 'mischseite', "")    
    addDir("Auto &Motor", "http://www.myvideo.de/themen/auto-und-motor", 'mischseite', "")
    addDir("TV und Film", "http://www.myvideo.de/themen/tv-und-film", 'mischseite', "")
    addDir("Games", "http://www.myvideo.de/games", 'mischseite', "")
    addDir("Infotainment", "http://www.myvideo.de/themen/infotainment", 'mischseite', "")
    addDir("Sport", "http://www.myvideo.de/themen/sport", 'mischseite', "")
    addDir("Comedy", "http://www.myvideo.de/themen/comedy", 'mischseite', "")
    addDir("Webisodes", "http://www.myvideo.de/themen/webisodes", 'mischseite', "")
    addDir("Telente", "http://www.myvideo.de/themen/talente", 'mischseite', "")
    addDir("Livestyle", "http://www.myvideo.de/themen/lifestyle", 'mischseite', "")
    addDir("Sexy", "http://www.myvideo.de/themen/sexy", 'mischseite', "")
    addDir("Erotik", "http://www.myvideo.de/Erotik", 'mischseite', "")
    #addDir("Rock", "http://www.myvideo.de/musik/rock", 'mischseite', "")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
id = urllib.unquote_plus(params.get('id', ''))
offset = urllib.unquote_plus(params.get('offset', ''))
tab = urllib.unquote_plus(params.get('tab', ''))
# Haupt Menu Anzeigen      

if mode is '':    
    addDir("Filme", "Filme", 'filme_menu', "")
    addDir("Top Listen", "Top 100", 'top100', "top10")
    addDir("TV & Serien", "TV & Serien", 'tvmenu', "")   
    addDir("Themen", "Themen", 'themenmenu', "")          
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
  if mode == 'allfilms':
          allfilms(url)          
  if mode == 'top100':
          top100()               
  if mode == 'topliste':
          topliste(url)   
  if mode == 'topgenres':
          topgenres()                       
  if mode == 'top_zeit':
          top_zeit(url)       
  if mode == 'filme_menu':
          filme_menu()                 
  if mode == 'filmgenres':
          filmgenres()    
  if mode == 'mischseite':
          mischseite(url)    
  if mode == 'misch_cat':
          misch_cat(url,offset) 
  if mode == 'misch_cat_auto':
          misch_cat_auto(url,offset)                   
  if mode == 'misch_tab':
          misch_tab(url,tab)   
  if mode == 'tvmenu':
          tvmenu()       
  if mode == 'themenmenu':
          themenmenu()               