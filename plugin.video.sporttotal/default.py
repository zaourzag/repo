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
from bs4 import BeautifulSoup

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])

args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
defaultBackground = ""
defaultThumb = ""
cliplist=[]
filelist=[]
profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
mainurl="https://www.sporttotal.tv"

#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       
xbmcplugin.setContent(int(sys.argv[1]), 'musicvideos')
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

cachezeit=addon.getSetting("cachetime")   
cache = StorageServer.StorageServer("plugin.video.rtlnow", cachezeit) # (Your plugin name, Cache time in hours

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
  
    
def addDir(name, url, mode, iconimage, desc="",text="",page="",ffilter="",ttype=""):
    debug("FFILTER :"+ ffilter)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&text="+str(text)+"&page="+str(page)+"&name"+str(name)+"&ffilter="+urllib.quote_plus(ffilter)
    u=u+"&ttype="+urllib.quote_plus(ttype)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="",artist_id="",genre="",shortname="",production_year=0,zeit=0,liedid=0):  
  cd=addon.getSetting("password")  
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre,"Sorttitle":shortname,"Dateadded":zeit,"year":production_year })
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setArt({ 'fanart': iconimage })   
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok


def getUrl(url,data="x"):        
        debug("Get Url: " +url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        userAgent = "Dalvik/2.1.0 (Linux; U; Android 5.0;)"
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
             debug("ERROR : " + error)
             dialog = xbmcgui.Dialog()
             nr=dialog.ok("Error", error)
             return ""
             
        opener.close()
        return content


      #addDir(namenliste[i], namenliste[i], mode+datum,logoliste[i],ids=str(idliste[i]))
   #xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
  



params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
ffilter = urllib.unquote_plus(params.get('ffilter', ''))
ttype = urllib.unquote_plus(params.get('ttype', ''))
debug(params)

def playvideo(url):
  debug("URL PLAY : "+url)  
  content = getUrl(url)
  file=re.compile('file: "([^"]+?)"', re.DOTALL).findall(content)[0].replace("\n","")
  suchstring=re.compile('/(.+?)\.mp4', re.DOTALL).findall(file)[0]
  replacestring=urllib2.quote(suchstring)  
  debug("suchstring :"+suchstring)
  debug("replacestring :"+replacestring)
  file=file.replace(suchstring,replacestring)
  #file=urllib2.quote(file.encode("utf-8")).replace("%3A",":")  
  debug("-------------")
  debug(file)
  listitem = xbmcgui.ListItem(path=file)
  xbmcplugin.setResolvedUrl(addon_handle, True, listitem)

  
  
def live(url):
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
  content = getUrl(url)  
  htmlPage = BeautifulSoup(content, 'html.parser')   
  videoliste = htmlPage.find("div",{"class" :"col-sm-3 related-videos"})        
  liste = videoliste.findAll("li")        
  for element in liste: 
          debug(element)
          name=element.findAll("h4")[0].text
          datum=element.find("h4",{"class" :"date"}).text.encode("utf-8").strip()
          if "LIVE" in name:
            live=1
          else :
             live=0
          name=name.replace("LIVE","").encode("utf-8").strip()
          if live==1:
             name =" ( LIVE ) "+name 
          else:
              name = datum +" - "+name
          debug("NAME :"+name)          
          url=mainurl+ element.find("a")["href"]    
          addLink(name, url, 'playvideo',"")   
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)           

def highlite_filter(url,ffilter=""):
    debug("------------------------")
    debug("highlite_filter filter :"+ffilter)
    params = parameters_string_to_dict(ffilter)
    liga = urllib.unquote_plus(params.get('liga', ''))    
    saison = urllib.unquote_plus(params.get('saison', '')) 
    verein = urllib.unquote_plus(params.get('verein', ''))
    debug("LIGA :"+liga+"#")
    debug("saison :"+saison)
    debug("verein :"+verein)
    ligafilter=""
    saisonfilter=""
    vereinfilter=""
    if not liga=='' and not liga=="Alle Ligen":  
       ligafilter="&liga="+liga.replace(" ","+")
    if not saison=="" and not saison=="-- Saison --":        
       saisonfilter="&saison="+saison.replace(" ","+")         
    if not verein=="" and not verein=="-- Verein --":      
       vereinfilter="&verein="+verein.replace(" ","+")               
    if ligafilter=="":
      addDir("Liega", url, 'highlite',"",ffilter=ligafilter+saisonfilter+vereinfilter,ttype="liga")   
    if saisonfilter=="":    
        addDir("Saison", url, 'highlite',"",ffilter=ligafilter+saisonfilter+vereinfilter,ttype="saison")   
    if vereinfilter=="":    
        addDir("Verein", url, 'highlite',"",ffilter=ligafilter+saisonfilter+vereinfilter,ttype="verein")       
    addDir("Alle", url, 'subliste',"",ffilter=ligafilter+saisonfilter+vereinfilter)  
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)           

def highlite(url,ffilter="",ttype=""):
    debug("--------------------")
    debug("highlite ffilter :"+ffilter)    
    content = cache.cacheFunction(getUrl,url)  
    htmlPage = BeautifulSoup(content, 'html.parser')       
    #<select name="liga" class="form-control">
    listelement = htmlPage.find("select",{"name" :ttype})  
    debug(listelement)
    liste = listelement.findAll("option")     
    for element in liste:   
       name=element.text.encode("utf-8").strip()       
       debug("--- >"+ name +" : "+       "&liga="+name)
       addDir(name, url, 'highlite_filter',"",ffilter=ffilter+"&"+ttype+"="+name)   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  

def subliste(url,ffilter=""):
  print("URL Subliste :"+url+ffilter)
  content = cache.cacheFunction(getUrl,url+ffilter)  
  htmlPage = BeautifulSoup(content, 'html.parser')    
  liste = htmlPage.findAll("section",{"class" :"container home-tile"})     
  for element in liste:     
     rubrik = element.find("h2",{"class" :"section-title"}).text
     addDir(rubrik, url+ffilter, 'listvideo',"",ffilter=rubrik)   
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
  
def  listvideo( url,rubrik_suche):
  debug("listvideo  url:"+url)
  debug("listvideo  rubrik_suche:"+rubrik_suche)
  content = cache.cacheFunction(getUrl,url)
  htmlPage = BeautifulSoup(content, 'html.parser')    
  liste = htmlPage.findAll("section",{"class" :"container home-tile"})     
  for element in liste:     
     rubrik = element.find("h2",{"class" :"section-title"}).text
     if rubrik==rubrik_suche:
       liste2 = element.findAll("a",{"class" :"teaser-tile-clip"}) 
       for element2 in liste2:        
        urll=element2["href"]
        img=element2.find("img")["src"]
        datum=element2.find("h4",{"class" :"date"}).text        
        beschreibung1=element2.findAll("h4",{"class" :"caption"})[0].text.encode("utf-8").strip()     
        beschreibung2=element2.findAll("h4",{"class" :"caption"})[1].text.encode("utf-8").strip()      
        debug("URLL :"+urll)
        debug("img :"+img)
        debug("beschreibung1 :"+beschreibung1)
        debug("beschreibung2 :"+beschreibung2)
        addLink(beschreibung1+" - "+beschreibung2,mainurl+urll, 'playvideo',img)   
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  

def oberliegen(url):
    debug("--------------------")
    debug("highlite ffilter :"+ffilter)   
    content = cache.cacheFunction(getUrl,url)
    htmlPage = BeautifulSoup(content, 'html.parser')       
    #<select name="liga" class="form-control">
    listelement = htmlPage.find("select",{"name" :ttype})  
    debug(listelement)
    liste = listelement.findAll("option")     
    for element in liste:   
       name=element.text.encode("utf-8").strip()       
       debug("--- >"+ name +" : "+       "&liga="+name)
       addDir(name, url, 'highlite_filter',"",ffilter=ffilter+"&"+ttype+"="+name)   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  

def topclips(url):    
    content = cache.cacheFunction(getUrl,url)
    htmlPage = BeautifulSoup(content, 'html.parser')     
    listelement = htmlPage.find_all("a",{"class" :"dropdown-item"})  
    for element in listelement:
       debug("-----")
       debug(element)
       name=element.text.encode("utf-8").strip()   
       wert=element["data-target"]
       addDir(name, url, 'list_top_a',"",ffilter=wert)   
    listelement = htmlPage.findAll("h2",{"class" :"section-title"})  
    for element in listelement:
        name=element.text.encode("utf-8").strip()   
        addDir(name, url, 'list_top_b',"",ffilter=name)   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

def   list_top_a(url,rubrik)  :
   debug("URL : "+url)
   debug("Rubrik : "+rubrik)
   if rubrik==".related-content.clips":
       rubrik="related-content show clips"
   if rubrik==".related-content.vod":
       rubrik="related-content vod"      
   content = cache.cacheFunction(getUrl,url)
   htmlPage = BeautifulSoup(content, 'html.parser') 
   komplett = htmlPage.find("ul",{"class" :rubrik})  
   listelement = komplett.findAll("li")
   for element in listelement:    
     link = element.find("a")["href"]
     link =mainurl+link
     string = element.find("div",{"class" :"item-thumb"})["style"]     
     img=re.compile('url\((.+)', re.DOTALL).findall(string)[0]
     img=mainurl+img
     text = element.findAll("h4")[0].text.encode("utf-8").strip()
     datum = element.find("h4",{"class" :"date"}).text.encode("utf-8").strip()
     debug(link)
     debug("-------")
     addLink(text+" ( "+datum +" )",link,"playvideo",img)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

def   list_top_b(url,rubrik)   :
    rubrik=urllib.unquote_plus(rubrik)  
    content = cache.cacheFunction(getUrl,url)
    htmlPage = BeautifulSoup(content, 'html.parser') 
    komplett = htmlPage.findAll("section",{"class" :"container home-tile"})
    for liste in komplett:
       rubrikname = liste.find("h2",{"class" :"section-title"}).text.encode("utf-8").strip()
       debug( rubrik +"<--->"+rubrikname)
       if not rubrik in rubrikname:
          continue
       #
       videos = liste.findAll("a",{"class" :"teaser-tile-clip"})
       for video in videos:
           debug("----------------------")
           debug(video)
           link=mainurl+video["href"]
           img=video.find("img")["src"]
           title=video.findAll("h4",{"class" :"caption"})[1].text.encode("utf-8").strip()
           datum=video.find("h4",{"class" :"date"}).text.encode("utf-8").strip()
           addLink(title+" ( "+datum +" )",link,"playvideo",img)
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

   
if mode is '':
    addDir("Live", "https://www.sporttotal.tv/live/", 'live',"")   
    addDir("Highlights", "https://www.sporttotal.tv/highlights?x=1", 'highlite_filter',"",ffilter="")   
    addDir("Top Clips", "https://www.sporttotal.tv/topclips/", 'topclips',"")   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  if mode == 'live':
          live(url)
  if mode == 'playvideo':
          playvideo(url)
  if mode == 'highlite':
          highlite(url,ffilter=ffilter,ttype=ttype)   
  if mode == 'highlite_filter':
          highlite_filter(url,ffilter=ffilter)             
  if mode == 'subliste':
          subliste(url,ffilter=ffilter)   
  if mode == 'listvideo':
          listvideo(url,ffilter)        
  if mode == 'topclips':
          topclips(url)
  if mode == 'list_top_a':
            list_top_a(url,ffilter)
  if mode == 'list_top_b':
            list_top_b(url,ffilter)            