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
import base64
import ssl


# Setting Variablen Des Plugins

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
cj = cookielib.LWPCookieJar();
xbmcplugin.setContent(addon_handle, 'tvshows')  

    

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")



def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 


cert=addon.getSetting("cert")
debug("##")
debug(cert)
if cert=="false":
  try:
      debug("#######")      
      _create_unverified_https_context = ssl._create_unverified_context
  except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
      pass
  else:
    # Handle target environment that doesn't support HTTPS verification
      ssl._create_default_https_context = _create_unverified_https_context


try:
   import StorageServer
except:
   import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("plugin.video.rtlnow", 12) # (Your plugin name, Cache time in hours

     
def addLink(name, url, mode, iconimage, duration="", desc="", genre=''):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage="", thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
	#liz.setProperty("fanart_image", defaultBackground)
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  return u,liz,True
	#ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	#return ok
  
def getUrl(url,data="x",header=""):
        global cj
        debug("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
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
             #debug( e.code   )
             cc=e.read()
             debug("Error : " +cc)

        opener.close()
        return content    

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
  
def addDir(name, url, mode, iconimage, desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({ 'fanart': iconimage })
    liz.setArt({ 'thumb': iconimage })
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    #ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return u,liz,True



       
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
showName = urllib.unquote_plus(params.get('showName', ''))
hideShowName = urllib.unquote_plus(params.get('hideshowname', '')) == 'True'
nextPage = urllib.unquote_plus(params.get('nextpage', '')) == 'True'
einsLike = urllib.unquote_plus(params.get('einslike', '')) == 'True'    
def serien(name,page=1):
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
  menu=[]
  debug("Serien New Menu")
  starturl='http://api.tvnow.de/v3/formats?filter='
  filter=urllib.quote_plus('{"Disabled": "0", "Station":"' + name +'"}')
  url=starturl+filter+'&fields=title,station,title,titleGroup,seoUrl,categoryId,*&maxPerPage=5000&page='+str(page)
  debug(url)  
  content = cache.cacheFunction(getUrl,url) 
  serienliste = json.loads(content)
  freeonly=addon.getSetting("freeonly") 
  items=[]
  for serieelement in serienliste["items"]:
    title=serieelement["title"].encode('utf-8')
    debug(title)
    seoUrl=serieelement["seoUrl"]
    if serieelement["hasFreeEpisodes"]==True or freeonly=="false" :
      menu.append(addDir(title , url=str(seoUrl), mode="rubrik", iconimage="",duration="",desc=""))
  xbmcplugin.addDirectoryItems(addon_handle,menu)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)    

def rubrik(name) :
  menu=[]
  debug("Rubrik New Menu")
  #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)   
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
  #http://api.tvnow.de/v3/formats/seo?fields=*,.*,formatTabs.*,formatTabs.headline&name=chicago-fire
  basurl="http://api.tvnow.de/v3/formats/seo?fields="
  div=urllib.quote_plus("*,.*,formatTabs.*,formatTabs.headline")
  endeurl="&name="+name
  url=basurl+div+endeurl
  debug(url)
  content = cache.cacheFunction(getUrl,url)      
  kapitelliste = json.loads(content)    
  if (kapitelliste["formatTabs"]["total"]==1):
    idd=kapitelliste["formatTabs"]["items"][0]["id"]   
    staffel(str(idd))
  else:
    for kapitel in kapitelliste["formatTabs"]["items"]:
      debug(kapitel)       
      idd=kapitel["id"]
      name=kapitel["headline"]      
      urlx="http://api.tvnow.de/v3/formatlists/"+str(idd)+"?maxPerPage=9&fields=formatTabPages.container.movies.free&page=1"      
      content2 = cache.cacheFunction(getUrl,urlx)    
      if '"free":true' in content2:
      #      debug(staffelinfo)
          menu.append(addDir(name , url=str(idd), mode="staffel", iconimage="",duration="",desc=""))        
  xbmcplugin.addDirectoryItems(addon_handle,menu)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)
def get_min(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s) /60
        
def staffel(idd) :    
  menu=[]
  xy=[]
  global cache
  debug("Lade staffel neu")
  #http://api.tvnow.de/v3/formatlists/41018?maxPerPage=9&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures&page=1http://api.tvnow.de/v3/formatlists/41016?maxPerPage=9&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures&page=1
  url="http://api.tvnow.de/v3/formatlists/"+idd+"?maxPerPage=9&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures&page=1http://api.tvnow.de/v3/formatlists/41016?maxPerPage=9&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures&page=1"
  debug("staffel :"+url)
  content = cache.cacheFunction(getUrl,url) 
  folgen = json.loads(content)
  liste=folgen["formatTabPages"]["items"]
  debug(liste)
  menu=[]
  for element in liste:
      try:
        elemente2=element["container"]["movies"]["items"]
      except:
        continue              
      for folge in elemente2:          
        debug("++")
        debug(folge["free"])
        debug(folge["isDrm"])
        freeonly=addon.getSetting("freeonly")
        if folge["isDrm"]==False and folge["free"]==True or freeonly=="false":
          debug("--")
          name=folge["title"].encode('utf-8')          
          idd=folge["id"]
          bild="https://ais.tvnow.de/tvnow/movie/"+str(idd)+"/600x600/title.jpg"
          stream=folge["manifest"]["dashclear"]
          laenge=get_sec(folge["duration"])          
          laengemin=get_min(folge["duration"])          
          staffel=str(folge["season"])
          folgenr=str(folge["episode"]) 
          plot=folge["articleLong"].encode('utf-8')  
          plotshort=folge["articleShort"].encode('utf-8')  
          startdate=folge["broadcastStartDate"]  .encode('utf-8')   
          tagline=folge["teaserText"]  .encode('utf-8')   
          type=folge["format"]["categoryId"]
          ftype="episode"
          if type=="serie":
            ftype="episode"
          zusatz=""
          if int(folgenr)>0:
             zusatz=" ("+startdate+ " )"
          listitem = xbmcgui.ListItem(path=stream,label=name+zusatz,iconImage=bild,thumbnailImage=bild)
          listitem.setProperty('IsPlayable', 'true')
          listitem.addStreamInfo('video', {'duration': laenge,'plot' : plot,'plotoutline' : plotshort,'tagline':tagline,'mediatype':ftype })
          listitem.setInfo(type="Video", infoLabels={'duration': laenge,"Title": name, "Plot": plot,'plotoutline': plotshort,'tagline':tagline,'mediatype':ftype ,"episode": folgenr, "season":staffel})          
          listitem.setProperty(u'IsPlayable', u'true')
          #listitem.setInfo(type='video')
          listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
          listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
          xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=stream, listitem=listitem)
          #addLink(name, stream, "playvideo", bild)          
          xbmcplugin.addDirectoryItems(addon_handle,menu)              
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)


       
def  login():
  debug("Start login")
  username=addon.getSetting("user")
  password=addon.getSetting("pass")
  if username=="" and password=="":
     debug("Kein Password")
     addon.setSetting("freeonly", "true")
     return 0
  url="https://api.tvnow.de/v3/backend/login"
  values = {'password' : "test1t",
        'email' : "andreas@vogler.name",        
    }
  data = urllib.urlencode(values)
  debug("######")
  debug(data)
  try:
    content = getUrl(url,data=data)         
    userdata = json.loads(content)
    debug(userdata)
    if userdata["subscriptionState"]==5:      
      debug("Login ok")
      addon.setSetting("freeonly", "false")
      return 1
    else :
      debug("Login No Subscription")
      addon.setSetting("freeonly", "true")
      return 0
  except:
      debug("Wrong Login")
      addon.setSetting("freeonly", "true")
      return 0
  debug(content)

def index():
    debug("START")    
    menu=[]
    debug("New MENU")
    ret=login()
    content = cache.cacheFunction(getUrl,"https://api.tvnow.de/v3/settings")      
    settings = json.loads(content)
    aliases=settings["settings"]["nowtv"]["production"]["stations"]["aliases"]    
    for name,value in aliases.items():
      if not name=="toggoplus" :
          menu.append(addDir(value , url=name, mode="serien", iconimage="",duration="",desc=""))   
    menu.append(addDir("Settings", "", 'Settings', ""))    
    xbmcplugin.addDirectoryItems(addon_handle,menu)
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)    
    
# Haupt Menu Anzeigen      
if mode is '':     
    index()    
else:  
  if mode == 'serien':
          serien(url)     
  if mode == 'rubrik':
          rubrik(url)             
  if mode == 'staffel':
          staffel(url)             
  if mode == 'playvideo':
          playvideo(url) 
  if mode == 'Settings':
          addon.openSettings()          