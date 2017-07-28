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
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok
  
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


        

def playlive(url):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()    
    listitem = xbmcgui.ListItem("Teil1", thumbnailImage="")        
    playlist.add("http://discintlhdflash-f.akamaihd.net/byocdn/media/1659832546/1659832546_1331791774001_swamploggers-310-1.mp4", listitem)                    
    listitem = xbmcgui.ListItem("Teil2", thumbnailImage="")    
    playlist.add("http://discintlhdflash-f.akamaihd.net/byocdn/media/1659832546/1659832546_1331791774001_swamploggers-310-2.mp4", listitem)                         
    xbmc.Player().play(playlist)
  

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
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok   

def getUrl(url, cookie=None):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')
    if cookie != None:
        req.add_header('Cookie', cookie)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

       
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
 starturl='http://api.tvnow.de/v3/formats?filter='
 filter=urllib.quote_plus('{"Disabled": "0", "Station":"' + name +'"}')
 url=starturl+filter+'&fields=title,station,title,titleGroup,seoUrl,categoryId,*&maxPerPage=5000&page='+str(page)
 debug(url)
 content=getUrl(url)
 serienliste = json.loads(content)
 for serieelement in serienliste["items"]:
  title=serieelement["title"].encode('utf-8')
  debug(title)
  seoUrl=serieelement["seoUrl"]
  if serieelement["hasFreeEpisodes"]==True:
    addDir(title , url=str(seoUrl), mode="rubrik", iconimage="",duration="",desc="")   
 xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)    

def rubrik(name) :
  #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
  #http://api.tvnow.de/v3/formats/seo?fields=*,.*,formatTabs.*,formatTabs.headline&name=chicago-fire
  basurl="http://api.tvnow.de/v3/formats/seo?fields="
  div=urllib.quote_plus("*,.*,formatTabs.*,formatTabs.headline")
  endeurl="&name="+name
  url=basurl+div+endeurl
  debug(url)
  content=getUrl(url)
  kapitelliste = json.loads(content)
  if (kapitelliste["formatTabs"]["total"]==1):
     idd=kapitelliste["formatTabs"]["items"][0]["id"]   
     staffel(str(idd))
  else:
    for kapitel in kapitelliste["formatTabs"]["items"]:
      debug(kapitel)
      idd=kapitel["id"]
      name=kapitel["headline"]
      addDir(name , url=str(idd), mode="staffel", iconimage="",duration="",desc="")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
  
def staffel(idd) :    
   #http://api.tvnow.de/v3/formatlists/41018?maxPerPage=9&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures&page=1http://api.tvnow.de/v3/formatlists/41016?maxPerPage=9&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures&page=1
       url="http://api.tvnow.de/v3/formatlists/"+idd+"?maxPerPage=9&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures&page=1http://api.tvnow.de/v3/formatlists/41016?maxPerPage=9&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures&page=1"
       debug("staffel :"+url)
       content=getUrl(url)
       folgen = json.loads(content)
       liste=folgen["formatTabPages"]["items"]
       debug(liste)
       for element in liste:
          try:
             elemente2=element["container"]["movies"]["items"]
          except:
              continue              
          for folge in elemente2:          
            debug("++")
            debug(folge["free"])
            debug(folge["isDrm"])
            if folge["isDrm"]==False and folge["free"]==True:
              debug("--")
              name=folge["title"].encode('utf-8')          
              idd=folge["id"]
              bild="https://ais.tvnow.de/tvnow/movie/"+str(idd)+"/600x600/title.jpg"
              stream=folge["manifest"]["dashclear"]
              laenge=folge["duration"]
              staffel=str(folge["season"])
              folgenr=str(folge["episode"])                           
              zusatz=""
              if int(folgenr)>0:
                 zusatz=" S"+staffel+"E"+folgenr
              listitem = xbmcgui.ListItem(path=stream,label=name+zusatz,iconImage=bild,thumbnailImage=bild)
              listitem.addStreamInfo('video', {'duration': laenge})
              listitem.setProperty(u'IsPlayable', u'true')
              #listitem.setInfo(type='video')
              listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
              listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
              ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=stream, listitem=listitem)
              #addLink(name, stream, "playvideo", bild) 
       xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def playvideo(url):
   debug("#######")
   debug("playvideo :"+ url)
   listitem = xbmcgui.ListItem(url)  
   listitem.setProperty(u'IsPlayable', u'true')
   listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
   listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
   
   xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
       
   
# Haupt Menu Anzeigen      
if mode is '':  
    content=getUrl("https://api.tvnow.de/v3/settings")
    settings = json.loads(content)
    aliases=settings["settings"]["nowtv"]["production"]["stations"]["aliases"]    
    for name,value in aliases.items():
       if not name=="toggoplus" :
          addDir(value , url=name, mode="serien", iconimage="",duration="",desc="")         
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:  
  if mode == 'serien':
          serien(url)     
  if mode == 'rubrik':
          rubrik(url)             
  if mode == 'staffel':
          staffel(url)             
  if mode == 'playvideo':
          playvideo(url) 