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

baseurl="https://www.mtv.de"
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
    

  
def addDir(name, url, mode, thump, desc="",seite=1,anz=0,serienname=0,stattfolgen=0):   
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&seite="+str(seite)+"&anz="+str(anz)+"&serienname="+str(serienname)+"&stattfolgen="+str(stattfolgen)
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


    

   
def getvideourl(url)  : 
    content=geturl(url)
    idd=re.compile('"itemId":"(.+?)"', re.DOTALL).findall(content)[0]                  
    mediaurl="http://media.mtvnservices.com/pmt/e1/access/index.html?uri=mgid:arc:episode:mtv.de:"+idd+"&configtype=edge"              
    content=geturl(mediaurl,referer=url)
    debug("++")
    struktur = json.loads(content)
    debug(struktur)
    ende=struktur["feed"]["items"][0]["group"]["content"]
    ende=ende.replace("&device={device}","")
    ende=ende+"&format=json&acceptMethods=hls"
    debug("ENDE :"+ende)
    content=geturl(ende)
    struktur = json.loads(content)
    try:
        videourl=struktur["package"]["video"]["item"][0]["rendition"][0]["src"]
    except:
        videourl=""
    debug("+++++++++++++++++++")
    debug(videourl)
    return(videourl)
  
def playvideo(url):      
    videourl=getvideourl(url)
    listitem = xbmcgui.ListItem(path=videourl)    
    #listitem.setProperty('IsPlayable', 'true')
    #listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
    #listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    #listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
    #listitem.setProperty('inputstream.adaptive.license_key', licfile)
    
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
referer = urllib.unquote_plus(params.get('referer', ''))
seite = urllib.unquote_plus(params.get('seite', ''))
anz= urllib.unquote_plus(params.get('anz', ''))
serienname= urllib.unquote_plus(params.get('serienname', ''))
stattfolgen= urllib.unquote_plus(params.get('stattfolgen', ''))
def serien(url):
 content=geturl(url)
 struktur = json.loads(content)    
 for buchstabe in struktur["result"]["shows"]:
   for serie in buchstabe["value"]:
      title=serie["title"]
      url=serie["url"]
      idd=serie["itemId"]      
      bild="https://mtv-intl.mtvnimages.com/uri/mgid:arc:content:mtv.de:"+idd+"?ep=mtv.de&stage=live&format=jpg&quality=0.8&&quality=0.85&width=400&height=225&crop=true"
      addDir(title,url,"serie",bild)
 xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
def serie(url):
 urlx="http://www.mtv.de/feeds/triforce/manifest/v8?url="+urllib.quote_plus(url)
 content=geturl(urlx)
 struktur = json.loads(content) 
 newurl=struktur["manifest"]["zones"]["t2_lc_promo1"]["feed"]  
 content=geturl(newurl)
 struktur = json.loads(content) 
 seasons=struktur["result"]["data"]["seasons"] 
 for season in seasons:
    idd=season["id"]
    title=season["eTitle"]
    desc=season["description"]
    url=season["canonicalURL"]    
    addDir(title,url,"folgen","",desc=desc)
 xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
def folgen(url,anz=0,seite=1):
    urlx="http://www.mtv.de/feeds/triforce/manifest/v8?url="+urllib.quote_plus(url)
    content=geturl(urlx)
    struktur = json.loads(content) 
    newurl=struktur["manifest"]["zones"]["t4_lc_promo1"]["feed"] 
    folgenteil(newurl) 
 
def folgenteil(url,anz=0,seite=1,serienname=0,stattfolgen=0):
 newurl=url
 content=geturl(newurl+"&pageNumber="+str(seite))
 struktur = json.loads(content) 
 folgen=struktur["result"]["data"]["items"]
 for folge in folgen:
    url=folge["canonicalURL"]
    try:
        desc=folge["description"]
    except:
         desc=""
    bild=folge["images"]["url"]
    title=folge["contentLabel"]
    if int(serienname)==1:
      if title=="Show":
        title=""
      title=folge["title"]+" "+title
    if int(stattfolgen)==0:
        addLink(title,url,"playvideo",bild,desc=desc)
    else:
        addDir(title,url,"serie",bild,desc=desc)
    anz=int(anz)+1
 try:
    if int(anz)<int(struktur["result"]["data"]["itemCount"]):
        newpage=int(seite)+1
        addDir("Seite "+str(newpage),newurl,"folgenteil","",anz=anz,seite=str(newpage))
 except:
    pass
 xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
def tvshow(url):    
  content=geturl(url)
  htmlPage = BeautifulSoup(content, 'html.parser')
  element = htmlPage.find("div",attrs={"id":"t7_lc_promo1"})  
  addDir("A-Z",element["data-tffeed"],"serien","")
  element = htmlPage.find("div",attrs={"id":"t4_lc_promo1"})
  addDir("Neueste",element["data-tffeed"],"folgenteil","",serienname=1)
  element = htmlPage.find("div",attrs={"id":"t5_lc_promo1"})
  addDir("Highlights",element["data-tffeed"],"folgenteil","",stattfolgen=1,serienname=1)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
  
def charts(url):
  content=geturl(url)
  htmlPage = BeautifulSoup(content, 'html.parser')
  element = htmlPage.find("div",attrs={"class":"headline-bar slickPad"})
  links=element.findAll("a")
  for link in links:
     url=link["href"]
     title=link.text
     if not "Album" in title:
        addDir(title,url,"chart","")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      

def chart(url):
    urlx="http://www.mtv.de/feeds/triforce/manifest/v8?url="+url
    content=geturl(urlx)
    struktur = json.loads(content) 
    newurl=struktur["manifest"]["zones"]["t4_lc_promo1"]["feed"] 
    chartteil(newurl) 
    
def chartteil(url):
    content=geturl(url)  
    struktur = json.loads(content)   
    substrukt=struktur["result"]
    for item in substrukt["data"]["items"]:
      debug("---")
      debug(item)
      try:
       lied=item["title"]
       debug(lied)
       kuenster=item["shortTitle"]
       debug(kuenster)
       chartpos=item["chartPosition"]["current"]
       debug(chartpos)
       image=item["images"][0]["url"]   
       debug(image)
       videourl=item["videoUrl"]
       debug(videourl)
       title=str(chartpos) +". "+ lied + " ( "+kuenster+" )"
       addLink(title,videourl,"playvideo",image)
      except:
       pass       
    try:   
        nexturl=substrukt["nextPageURL"]
        chartteil(nexturl)
    except:
        pass
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   


def playplaylist(url):
  content=geturl(url)
  htmlPage = BeautifulSoup(content, 'html.parser')
  element = htmlPage.find("div",attrs={"id":"t1_lc_promo1"})
  playlisteurl=element["data-tffeed"]
  content=geturl(playlisteurl)
  struktur = json.loads(content) 
  playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
  playlist.clear()
  x=0
  title_ar=[]
  videourl_arr=[]
  image_arr=[]
  for item in struktur["result"]["data"]["items"]:
    debug("=====================")
    vurl=item["canonicalURL"]         
    videourl=getvideourl(vurl)
    videourl_arr.append(videourl)
    title=item["title"].encode("utf-8")
    title_ar.append(title)
    image=item["images"]["url"]
    image_arr.append(image)
  for i in range(0, len(videourl_arr), 1):
    debug(title_ar[i])
    item = xbmcgui.ListItem(path=videourl_arr[i],label=title_ar[i],iconImage=image_arr[i])         
    playlist.add(videourl_arr[i], item)
    if i==0:
        xbmc.Player().play(playlist)
#    if i==0:
#       break

  #xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   


def playlists(url):
    urlx="http://www.mtv.de/feeds/triforce/manifest/v8?url="+url
    content=geturl(urlx)
    struktur = json.loads(content) 
    newurl=struktur["manifest"]["zones"]["t4_lc_promo1"]["feed"] 
    playlistspart(newurl) 
    
def playlistspart(url):
    content=geturl(url)  
    struktur = json.loads(content)   
    substrukt=struktur["result"]
    for item in substrukt["data"]["items"]:
       debug("---")
       debug(item)
      
       title=item["title"].encode("utf-8")     
       debug(title)
       image=item["images"]["url"]   
       debug(image)
       videourl=item["canonicalURL"]
       debug(videourl)     
       addLink(title,videourl,"playplaylist",image)
      
    try:   
        nexturl=substrukt["nextPageURL"]
        playlistspart(nexturl)
    except:
        pass
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      
    
def music():
    addDir("Playlists" , "http://www.mtv.de/playlists", "playlists","")    
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      
    
def liste():      
    addDir("TVshows" , baseurl+"/shows", "tvshow","")     
    addDir("Charts" , baseurl+"/charts", "charts","")     
    addDir("Music" , "", "music","")     
    addDir("Settings","Settings","Settings","")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
    
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
  if mode == 'serien':
          serien(url)
  if mode == 'serie':
          serie(url) 
  if mode == 'folgen':
           folgen(url,anz,seite)          
  if mode == 'tvshow':
          tvshow(url)
  if mode == 'listserie':
           listserie(url)
  if mode == 'folgenteil':
            folgenteil(url,anz,seite,serienname,stattfolgen)
  if mode == 'music':
            music()
  if mode == 'charts':
            charts(url)
  if mode == 'chart':
            chart(url)
  if mode == 'chartteil':
            chartteil(url)
  if mode =="playlists":
            playlists(url)
  if mode =="playlistspart":
            playlistspart(url)
  if mode =="playplaylist":
            playplaylist(url)  
