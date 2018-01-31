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

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString


xbmcplugin.setContent(addon_handle, 'movies')

baseurl="https://tv.hsv.de/"
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)


icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')


profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)
cookie=os.path.join( temp, 'cookie.jar')
cj = cookielib.LWPCookieJar();

if xbmcvfs.exists(cookie):
    cj.load(cookie,ignore_discard=True, ignore_expires=True)                  

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    

  
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
  
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict


def geturl(url,data="x",header="",referer=""):
        global cj
        debug("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))        
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        if header=="":
          opener.addheaders = [('User-Agent', userAgent)]        
        else:
          opener.addheaders = header        
        if not referer=="":
           opener.addheaders = [('Referer', referer)]

        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #debug( e.code )  
             cc=e.read()  
             debug("Error : " +cc)
             content=""
       
        opener.close()
        cj.save(cookie,ignore_discard=True, ignore_expires=True)               
        return content


    

   
   
def login():
  username=addon.getSetting("user")
  password=addon.getSetting("pass")  
  values = {'force_login' : '1',
  'password' : password,
        'username' : username, 
        'login_user': 'Anmelden'        
  }
  headers = {'User-Agent':         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
   'X-Requested-With':              'XMLHttpRequest',
   'Referer':                      baseurl,
   'Content-Type':                  'application/x-www-form-urlencoded; charset=UTF-8',
   'Origin':                        baseurl,
   'Accept-Encoding':'gzip, deflate, br',
   'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7'
   }
  data = urllib.urlencode(values)
  debug("Data : "+data)
  content = requests.post(baseurl+"/user/login",data=data, allow_redirects=False,verify=False,cookies=cj,headers=headers)
  debug(content.text.encode("utf-8"))  
  if "Sie sind jetzt eingeloggt" in content.text.encode("utf-8"):
    return 0
  else:
    return -1
  
def liste():
  #ret=login()  
  ret=0
  if ret==-1:
     dialog = xbmcgui.Dialog()
     dialog.notification("Error", 'Error keine Lgoin Daten', xbmcgui.NOTIFICATION_ERROR)
     addon.openSettings()
  else:
    #quality=addon.getSetting("quality")
#    auswahl_qual="source_"+quality
    addDir("Settings","Settings","Settings","")
    content=geturl(baseurl)
    htmlPage = BeautifulSoup(content, 'html.parser')
    elemente = htmlPage.find_all("a",attrs={"class":"teaser"})
    addDir("Budnesliega", baseurl+"/video/bundesliga", "subrubrik","")
    for element in elemente:
       title= element["title"]
       if not "bundesliga" in element["href"]:         
        addDir(title, baseurl+element["href"], "subrubrik","")
    addDir("Alle" , element["href"], "videoliste","")       
    xbmcplugin.endOfDirectory(addon_handle) 
def subrubrik(url):
  content=geturl(url)
  htmlPage = BeautifulSoup(content, 'html.parser')
  subliste = htmlPage.find("ul",attrs={"class":"level_2"})
  elemente  = subliste.find_all("a",attrs={"class":"teaser"})
  try:
      auswahl=subliste.find("strong")  
      new=auswahl["title"]
      addDir(new,url,"videoliste","")
      for element in elemente :
        title= element["title"]        
        addDir(title, baseurl+element["href"], "videoliste","")
      addDir("Videos", url, "videoliste","")
      xbmcplugin.endOfDirectory(addon_handle) 
  except:
       videoliste(url,nosub=1)
  
def playvideo(url):      
    playlist=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()    
    quality=addon.getSetting("quality")    
    content=geturl(url)
    newurl=re.compile('<meta name="player.init" content="(.+?)" />', re.DOTALL).findall(content)[0]
    newurl=baseurl+newurl
    content=geturl(newurl)
    struktur = json.loads(content)     
    for subelement in struktur["startVideo"]["segments"]:
       for element in subelement["assets"]:
            if element["profile"]==quality:                
                playurl=element["html5"]
                listitem = xbmcgui.ListItem(path=playurl)
                playlist.add(playurl, listitem)  
                debug("ADD: "+playurl)                     
            else:
                debug("Qualtity :"+element["profile"]  +" false")
    debug(playlist)
    xbmc.Player().play(playlist)
    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
referer = urllib.unquote_plus(params.get('referer', ''))
page = urllib.unquote_plus(params.get('page', ''))
nosub= urllib.unquote_plus(params.get('nosub', ''))

def videoliste(url,page=1,nosub=0):  
  if page>1:
    if int(nosub)==1:
      nexturl=url+"/0/"+str(page)
    else:
      nexturl=url+"/"+str(page)
  else:
    nexturl=url
  content=geturl(nexturl)
  htmlPage = BeautifulSoup(content, 'html.parser')
  subliste = htmlPage.find("ul",attrs={"id":"teaser_items"})
  elemente  = subliste.find_all("li",attrs={"class":"tooltip_item"})
  for element in elemente:
       link = element.find("a",attrs={"class":"playlist"})["href"]
       link=baseurl+link
       bild = element.find("img")["src"]
       bild=baseurl+bild
       title = element.find("span",attrs={"class":"teams"}).text
       datum = element.find("span",attrs={"class":"date"}).text       
       addDir(title+" ( "+datum +" )",link,"playvideo",bild)
  addDir("Next",url,"videoliste","",page=int(page)+1,nosub=nosub)
  xbmcplugin.endOfDirectory(addon_handle)
# Haupt Menu Anzeigen      
if mode is '':
     liste()   
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'playvideo':
          playvideo(url)
  if mode == 'subrubrik':
          subrubrik(url)
  if mode == 'videoliste':
          videoliste(url,page,nosub)