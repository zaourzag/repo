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
#from subtitles import download_subtitles
import time
import datetime
import _strptime
from collections import OrderedDict


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
baseurl="http://www.br.de"
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
defaultBackground = ""
defaultThumb = ""
global bitrate
bitrate=addon.getSetting("bitrate")
global kurzvideos
kurzvideos=addon.getSetting("kurzvideos")

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
    
   
def addDir(name, url, mode, iconimage, desc="",subrubrik=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&subrubrik="+str(subrubrik)
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
    
def date2timeStamp(date, format):
    try:
        dtime = datetime.datetime.strptime(date, format)
    except TypeError:
        dtime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(date, format)))
    return dtime
  
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
        global cj
        debug("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"
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
             #debug( e.code   )
             cc=e.read()
             debug("Error : " +cc)

        opener.close()
        return content    

def abisz(url):
   content=getUrl(url)
   liste = json.loads(content)  
   url=liste["_links"]["broadcastSeriesAz"]["href"]
   content=getUrl(url)
   liste = json.loads(content)  
   for name,link in liste["az"]["_links"].iteritems():
      addDir(name, link["href"], 'buchstabe', "")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      

def epg(url):
   content=getUrl(url)
   liste = json.loads(content,object_pairs_hook=OrderedDict)  
   url=liste["_links"]["epg"]["href"]
   content=getUrl(url)
   liste = json.loads(content,object_pairs_hook=OrderedDict)     
   for name,link in liste["epgDays"]["_links"].items():
       d=date2timeStamp(name,'%Y-%m-%d')   
       jetzt=datetime.datetime.now()
       if jetzt >d:
               addDir(name, link["href"], 'channels', "")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)         

def live(url):
   content=getUrl(url)
   liste = json.loads(content,object_pairs_hook=OrderedDict)  
   url=liste["_links"]["home"]["href"]
   content=getUrl(url)
   liste = json.loads(content,object_pairs_hook=OrderedDict)     
   endurl=""
   for link in liste["_embedded"]["teasers"]:
      links=link["_links"]["boxIndexPage"]["href"]
      debug(links)
      if "livestreams" in links:
         endurl=links
         break 
   content=getUrl(endurl)
   liste = json.loads(content,object_pairs_hook=OrderedDict)              
   for link in liste["_embedded"]["teasers"]:
      debug(link)     
      links=link["_links"]["self"]["href"]
      try:
        title=link["regionTitle"]
      except:
         tittle=""
      subtitle=link["headline"]
      image=link["teaserImage"]["_links"]["original"]["href"]
      endate=link["broadcastEndDate"]
      startdate=link["broadcastStartDate"]
      date_format = '%Y-%m-%dT%H:%M:%S'  
      xy=startdate.split("+")
      startdate=xy[0]
      xy=endate.split("+")
      endate=xy[0]
      startstamp=date2timeStamp(startdate, date_format)
      endstamp=date2timeStamp(endate, date_format)
      jetzt=datetime.datetime.now()
      if jetzt > startstamp and jetzt < endstamp:
         addLink(title +" - "+subtitle,links,"playlive",image)     
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)         
   
   
def search(url):
   content=getUrl(url)
   liste = json.loads(content,object_pairs_hook=OrderedDict)  
   url=liste["_links"]["search"]["href"]
   dialog = xbmcgui.Dialog()
   d = dialog.input(translation(30010), type=xbmcgui.INPUT_ALPHANUM)
   url=url.replace("{term}",d)
   serievideo(url)

   
def channels(url):
   content=getUrl(url)
   liste = json.loads(content)  
   for name,link in liste["channels"].iteritems():
       title=link["channelTitle"]
       addDir(title, url, 'channel', "",subrubrik=name)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)          
def channel(url,sub):
   debug("Channel sub :"+sub)
   content=getUrl(url)
   liste = json.loads(content)    
   for sendung in liste["channels"][sub]["broadcasts"]:
      try:
        debug(sendung)
        date_format = '%Y-%m-%dT%H:%M:%S' 
 #                   2017-10-28T20:00:00+0200    
        st=sendung["documentProperties"]["br-core:broadcastStartDate"]
        xy=st.split("+")
        #st=xy[0]+"+"+xy[1].replace(":","")
        st=xy[0]
        debug(st)
        zeit=date2timeStamp(st, date_format)
        debug("++")
        debug(zeit)
        start=zeit.strftime("%H:%M")
        debug(sendung)
        title=sendung["headline"]
        subTitle=sendung["subTitle"]
        if subTitle=="":
           name=start +" : "+title
        else:
            name=start +" : "+title+" - "+subTitle
        link=sendung["_links"]["video"]["href"]
        addLink(name, link, 'play', "")
      except:
        pass
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)             

     
def buchstabe(url):
   content=getUrl(url)
   liste = json.loads(content)  
   serien=liste["_embedded"]["teasers"]   
   for serie in serien:
    debug(serie)
    title=serie["documentProperties"]["br-core:azHeadline"]
    bild=serie["teaserImage"]["_links"]["original"]["href"]
    link=serie["_links"]["self"]["href"]
    addDir(title, link, 'serie', bild)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
def serie(url):
   content=getUrl(url)
   liste = json.loads(content)  
   newurl=liste["_links"]["latestVideos"]["href"]
   serievideo(newurl)
   
def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)
    
def serievideo(url):   
   content=getUrl(url)
   liste = json.loads(content) 
   for folge in liste["_embedded"]["teasers"]:
     debug(folge)
     link=folge["_links"]["self"]["href"]
     name=folge["headline"]
     image=folge["teaserImage"]["_links"]["original"]["href"]
     duration=get_sec(folge["documentProperties"]["br-core:duration"])
     if kurzvideos=="true" or duration>900:
        addLink(name, link, 'play', image,duration=duration)
   try: 
     next=liste["_embedded"]["_links"]["next"]["href"]
     debug("NEXT :"+next)
     addDir("Weiter", next, 'serievideo', "")
   except:
     pass

   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     

   
def play(url):
    content=getUrl(url)
    liste = json.loads(content) 
    min=99999999
    mistream=""
    max=0    
    maxstream=""
    streaml=""
    streamliste=[]
    namenslistge=[]
    debug("Start PLAY")
    debug(bitrate)        
    for stream in liste["assets"]:       
       try:
            link=stream["_links"]["download"]["href"]
            bitrates=stream["bitrateVideo"]
            name=stream["recommendedBandwidth"]
            namenslistge.append(name)
            streamliste.append(link)
            if bitrates<min :
                min=bitrates
                minstream=link
            if bitrates>max:
                max=bitrates
                maxstream=link          
       except: 
         pass
    if bitrate=="Min":
        streaml=mistream
    if bitrate=="Max":
        streaml=maxstream
    if bitrate=="Select":
        dialog = xbmcgui.Dialog()
        nr=dialog.select("Bitrate", namenslistge)
        streaml=streamliste[nr]                   
    listitem = xbmcgui.ListItem(path=streaml)
    xbmcplugin.setResolvedUrl(addon_handle,True, listitem)
def playlive(url):
    content=getUrl(url)
    liste = json.loads(content) 
    stream=""
    for element in liste["assets"]:
      if element["type"]=="HLS" and element["geozone"]=="DEUTSCHLAND":
          stream=element["_links"]["stream"]["href"]
          break
    debug(stream)
    content=getUrl(stream)
    urlv=re.compile('(https:[^:]+=on)', re.DOTALL).findall(content)
    streaml=urlv[-3]
    all=streaml.split("?")
    streaml=all[0]
    listitem = xbmcgui.ListItem(path=streaml)
    xbmcplugin.setResolvedUrl(addon_handle,True, listitem)   
    
    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
subrubrik = urllib.unquote_plus(params.get('subrubrik', ''))

cj = cookielib.LWPCookieJar();
start="https://www.br.de/system/halTocJson.jsp"
content=getUrl(start)
startliste = json.loads(content)  
rubriken=startliste["medcc"]["version"]["1"]["href"]

debug(rubriken)

# Haupt Menu Anzeigen      
if mode is '':
    addDir(translation(30001), rubriken, 'A-Z', "")
    addDir(translation(30005), rubriken, 'EPG', "")
    addDir(translation(30011), rubriken, 'Search', "")
    addDir(translation(30007), rubriken, 'live', "")
    addDir(translation(30002), translation(30002), 'Settings', "")       
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'A-Z':
          abisz(url)
  if mode == "buchstabe":
            buchstabe(url)
  if mode == "serie":
            serie(url)            
  if mode == "serievideo":
            serievideo(url)                 
  if mode == "play":
            play(url)                             
  if mode == "EPG":
            epg(url)  
  if mode == "channels":
            channels(url)  
  if mode == "channel":
            channel(url,subrubrik)              
  if mode == "channelfile":
            channelfile(url)                          
  if mode == 'Search':
          search(url)            
  if mode == "live":
            live(url)   
  if mode == "playlive":
            playlive(url)  