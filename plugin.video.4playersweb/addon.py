#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon,xbmcplugin
import xbmcgui,xbmcvfs
import json,urllib2,re,urlparse,os
from bs4 import BeautifulSoup
from datetime import datetime    
import urllib
import requests
from cookielib import LWPCookieJar

addon = xbmcaddon.Addon()

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
session = requests.session()

defaultThumb = ""
defaultBackground = ""
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
addon_handle = int(sys.argv[1])


type=addon.getSetting("Type") 
if  type=="Alle Systeme":
    type="videos"
if type=="PC":
   type="PC-CDROM"
if type=="XBox One":
   type=="XboxOne"
if type=="Playstation 4":
   type="PlayStation4"
if type=="XBox 360":
   type="PlayStation4"
if type=="360":
   type="PlayStation3"
if type=="Switch":
   type="Switch"
if type=="Wii U":
   type="Wii_U"   
if type=="Select":
   type="-1"       
newtype=addon.getSetting("NEWType") 
if  newtype=="Alle":
    newtype=""
if newtype=="Top":
   newtype="/TopRated/Top"
if newtype=="Meistgesehen":
   newtype=="/TopViews/Meistgesehen"
if newtype=="PC":
   newtype="/PC-CDROM/PC"
if newtype=="One":
   newtype="/XboxOne/One"
if newtype=="PS4P":
   newtype="/PlayStation4/PS4"
if newtype=="Switch":
   newtype="/Switch/Switch"
if newtype=="Handhelds":
   newtype="/Handhelds/Handhelds"   
if newtype=="PSVR":
   newtype="/PlayStationVR/PSVR"
if newtype=="PS4P":
   newtype="/PlayStation4Pro/Alle"   
if newtype=="PC-VR":
   newtype="/PC-VR/PC-VR"     
if newtype=="Select":
   newtype="-1"       

if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
def addDir(name, url, mode, iconimage, desc="",ffilter=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&ffilter="+urllib.quote_plus(str(ffilter))+"&mode="+str(mode)
  debug(" U :"+u)
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})  
  liz.setArt({ 'fanart': defaultBackground })    
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
  
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
  
  
def geturl(url,header=""): 
    debug("GETURL : "+url)
    headers = {'User-Agent':         'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0', 
    }        
    ip=addon.getSetting("ip")
    port=addon.getSetting("port")    
    if not ip=="" and not port=="":
      px="http://"+ip+":"+str(port)
      proxies = {
        'http': px,
        'https': px,
      }    
      content = session.get(url, allow_redirects=True,verify=False,headers=headers,proxies=proxies)    
    else:
      content = session.get(url, allow_redirects=True,verify=False,headers=headers)    
    return content.text

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
ffilter = urllib.unquote_plus(params.get('ffilter', ''))
debug("## F :"+sys.argv[2])


def index():
  content=geturl("http://www.4players.de/4players.php/browsevideostv/videos/")
  htmlPage = BeautifulSoup(content, 'html.parser')
  element = htmlPage.find("select",attrs={'name':'FILTER'})
  spalten = element.find_all('option')
  addDir("Settings", "", 'Settings', "")
  if not newtype=="-1":
    addDir("Neueste Videos", "http://www.4players.de/4players.php/browsevideostv###/Trailer_Videos_TV.html#pagetop", 'listrubrik', "",ffilter=newtype)   
  else:     
    addDir("Neueste Videos", "http://www.4players.de/4players.php/browsevideostv###/Trailer_Videos_TV.html#pagetop", 'newvideos', "",ffilter=newtype)     
  debug("TYPE :"+type)
  for spalte in spalten: 
   if type=="-1":       
      addDir(spalte.text, spalte["value"], 'listrubriken', "")   
   else:
       addDir(spalte.text, spalte["value"], 'listrubrik', "",ffilter=type)   
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   

  
def newvideos(url,ffilter):
    addDir("Alle", url, 'listrubrik', "",ffilter="")  
    addDir("Top", url, 'listrubrik', "",ffilter="/TopRated/Top")  
    addDir("Meistgesehen", url, 'listrubrik', "",ffilter="/TopViews/Meistgesehen")  
    addDir("PC", url, 'listrubrik', "",ffilter="/PC-CDROM/PC")  
    addDir("One", url, 'listrubrik',"", ffilter="/XboxOne/One")  
    addDir("PS4", url, 'listrubrik', "",ffilter="/PlayStation4/PS4")  
    addDir("PSVR", url, 'listrubrik', "",ffilter="/PlayStationVR/PSVR")  
    addDir("PS4P", url, 'listrubrik',"", ffilter="/PlayStation4Pro/Alle")  
    addDir("PC-VR", url, 'listrubrik', "",ffilter="/PC-VR/PC-VR")  
    addDir("Switch", url, 'listrubrik', "",ffilter="/Switch/Switch")  
    addDir("Handhelds", url, 'listrubrik',"",ffilter= "/Handhelds/Handhelds")  
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
   
  
def listrubriken(url):
   debug("listrubriken url :"+url)
   content=geturl("http://www.4players.de/4players.php/browsevideostv/videos/"+url+"/")
   htmlPage = BeautifulSoup(content, 'html.parser')
   element = htmlPage.find("select",attrs={'name':'SYSTEM'})
   spalten = element.find_all('option')
   for spalte in spalten:        
      addDir(spalte.text, url, 'listrubrik', "",ffilter=spalte["value"])
      debug(spalte["value"])
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      
def listrubrik(url,ffilter)   :
  if not "http:" in url:
    geturll=  "http://www.4players.de/4players.php/browsevideostv/"+ffilter+"/"+url+"/Trailer_Videos_TV.html"
  else:
     geturll=url.replace("###",ffilter)
  debug("geturll :"+geturll)
  debug("url :"+url)
  debug("ffilter :"+ffilter)
  content=geturl(geturll)
  htmlPage = BeautifulSoup(content, 'html.parser')
  elemente = htmlPage.find_all("div",attrs={'class':'tv-aktuell-box index-system-hauptthema'})
  for element in elemente:        
    link=element.find("a")["href"]
    img=element.find("div",attrs={'class':'skim'})["data-skimimageurl"].replace("skimimage.jpg","thumb300x168.jpg")
    debug("IMG :"+img)
    title=element.find("a")["title"]
    spiel=element.find("div",attrs={'class':'spielname left'}).text
    beschreibung=element.find("div",attrs={'class':'einleitung'}).text.strip()
    datum=element.find("div",attrs={'class':'tv-aktuell-datum'}).text
    views=element.find("div",attrs={'class':'tv-aktuell-views'}).text
    laufzeit=element.find("div",attrs={'class':'laufzeit'}).text
    name=spiel+" - "+title
    addLink(name, link, "playvideo", img,desc=beschreibung,duration=laufzeit)          
  try:
    nexlink=re.compile('<a href="([^"]+?)" class="pagenavi">Nächste Seite</a>', re.DOTALL).findall(content.encode('utf-8'))[0]
    debug("#####++++")
    addDir("Naechste Seite", nexlink, 'listrubrik', "")  
  except:
    pass  
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
 
  
def playvideo(url):
  content=geturl(url)
  newlink=re.compile("playlist:[^']+'(.+?)'", re.DOTALL).findall(content)[0]
  content=geturl(newlink)
  htmlPage = BeautifulSoup(content,"html.parser")
  videos = htmlPage.find_all('jwplayer:source')
  listename=[]
  listeurl=[]
  for video in videos:
    file=video["file"]
    quali=video["label"]
    listename.append(quali)
    listeurl.append(file)
  dialog = xbmcgui.Dialog()
  nr=dialog.select("Qualität", listename)
  listitem = xbmcgui.ListItem(path=listeurl[nr])
  xbmcplugin.setResolvedUrl(addon_handle, True, listitem)


    
    
    


  
if mode=="":
    index()      
if mode=="listrubriken":
   listrubriken(url)
if mode=="listrubrik":
   listrubrik(url,ffilter)
if mode=="playvideo":
   playvideo(url)   
if mode == 'Settings':
          addon.openSettings()       
if mode=="newvideos":
    newvideos(url,ffilter)
    