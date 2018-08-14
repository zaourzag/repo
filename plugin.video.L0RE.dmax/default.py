#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil, json
import time
import goldfinch

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString


xbmcplugin.setContent(addon_handle, 'movies')

baseurl="https://www.dmax.de"
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)


icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')


profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

if xbmcvfs.exists(temp):
  try:
    shutil.rmtree(temp)
  except:
     pass
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

def addDir(name, url, mode, thump, desc="",page=1,nosub=0,type="items",addtype=0): 
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&nosub="+str(nosub)+"&type="+str(type)
  ok = True
  liz = xbmcgui.ListItem(name)  
  liz.setArt({ 'fanart' : thump })
  liz.setArt({ 'thumb' : thump })
  liz.setArt({ 'banner' : icon })
  liz.setArt({ 'fanart' : icon })
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  if addtype==1:
    commands = []  
    updatestd=addon.getSetting("updatestd")
    link = "plugin://plugin.video.L0RE.dmax/?mode=tolibrary&url=%s&name=%s&stunden=%s"%(url,name,updatestd)
    debug(link.encode("utf-8"))
    commands.append(( "Add to library", 'XBMC.RunPlugin('+ link +')'))
    liz.addContextMenuItems( commands )
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

def liste():
    addDir("Alle Sendungen" , "https://www.dmax.de/api/search?query=*&limit=100&page=1", "videoliste","",nosub="recently-added",type="shows")
    addDir("Themen" , "", "themenliste","")            
    addDir("Featured" , "https://www.dmax.de/api/shows/highlights?limit=100&page=1", "videoliste","",nosub="featured") 
    addDir("Beliebteste" , "https://www.dmax.de/api/shows/beliebt?limit=100&page=1", "videoliste","",nosub="most-popular")    
    addDir("Neueste" , "https://www.dmax.de/api/shows/neu?limit=100&page=1", "videoliste","",nosub="recently-added")        
    #addDir("Letzt Chance" , "https://www.dmax.de/api/shows/leaving-soon?limit=100&page=1", "videoliste","",nosub="leaving-soon")    
    addDir("Settings","Settings","Settings","")
    inputstream=addon.getSetting("inputstream")
    if inputstream=="true":
        addDir("Inputstream Einstellungen", "", 'inputsettings', "")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

def themenliste():  
  addDir("Abenteuer" , "https://www.dmax.de/api/genres/abenteuer", "videoliste","",nosub="recently-added")          
  addDir("Auction" , "https://www.dmax.de/api/genres/auction", "videoliste","",nosub="recently-added")          
  addDir("Aufdrehen" , "https://www.dmax.de/api/genres/aufdrehen", "videoliste","",nosub="recently-added")          
  addDir("Tool Time" , "https://www.dmax.de/api/genres/tool-time", "videoliste","",nosub="recently-added")          
  addDir("Entertainment" , "https://www.dmax.de/api/genres/entertainment", "videoliste","",nosub="recently-added")          
  addDir("Lifestyle" , "https://www.dmax.de/api/genres/lifestyle", "videoliste","",nosub="recently-added")          
  addDir("Motor" , "https://www.dmax.de/api/genres/motor", "videoliste","",nosub="recently-added")          
  addDir("Survival" , "https://www.dmax.de/api/genres/survival", "videoliste","",nosub="recently-added")            
  addDir("Schatzsucher" , "https://www.dmax.de/api/genres/schatzsucher", "videoliste","",nosub="recently-added")            
  addDir("Traumautos" , "https://www.dmax.de/api/genres/traumautos", "videoliste","",nosub="recently-added")            
  addDir("Wissen" , "https://www.dmax.de/api/genres/wissen", "videoliste","",nosub="recently-added")            
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
def playvideo(idd): 
    debug("PLAYVIDEO")     
    content=geturl("https://www.dmax.de/")    
    for cookief in cj:
          debug( cookief)
          if "sonicToken" in str(cookief) :         
                key=re.compile('sonicToken=(.+?) ', re.DOTALL).findall(str(cookief))[0]
                break

    playurl="https://sonic-eu1-prod.disco-api.com/playback/videoPlaybackInfo/"+str(idd)
    header = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'),
                    ("Authorization", "Bearer "+key)]

    content=geturl(playurl,header=header)
    debug(content)
    struktur = json.loads(content)    
    videofile=struktur["data"]["attributes"]["streaming"]["hls"]["url"]
    debug(videofile)
    #debug(licfile)    
    listitem = xbmcgui.ListItem(path=videofile)    
    listitem.setProperty('IsPlayable', 'true')
    inputstream=addon.getSetting("inputstream")
    if inputstream=="true":     
        licfile=struktur["data"]["attributes"]["protection"]["schemes"]["clearkey"]["licenseUrl"]
        contentI=geturl(licfile,header=header)
        strukturI = json.loads(contentI)
        lickey=strukturI["keys"][0]["k"]        
        listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
        #listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        listitem.setProperty('inputstream.adaptive.license_key', lickey)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
referer = urllib.unquote_plus(params.get('referer', ''))
page = urllib.unquote_plus(params.get('page', ''))
nosub= urllib.unquote_plus(params.get('nosub', ''))
type= urllib.unquote_plus(params.get('type', ''))
name= urllib.unquote_plus(params.get('name', ''))
stunden= urllib.unquote_plus(params.get('stunden', ''))

def tolibrary(url,name,stunden):
    mediapath=addon.getSetting("mediapath")
    if mediapath=="":
      dialog = xbmcgui.Dialog()
      dialog.notification("Error", "Pfad setzen in den Settings", xbmcgui.NOTIFICATION_ERROR)
      return    
    urln="plugin://plugin.video.L0RE.dmax?mode=generatefiles&url="+url+"&name="+name
    urln=urllib.quote_plus(urln)
    debug("tolibrary urln : "+urln)
    xbmc.executebuiltin('XBMC.RunPlugin(plugin://service.L0RE.cron/?mode=adddata&name=%s&stunden=%s&url=%s)'%(name,stunden,urln))

def listserie(idd):
  url="https://www.dmax.de/api/show-detail/"+str(idd)
  debug("listserie :"+url)
  content=geturl(url)
  try:
    struktur = json.loads(content)
  except:
    dialog = xbmcgui.Dialog()
    dialog.notification("Fehler", 'Keine Video zu dieser Serie', xbmcgui.NOTIFICATION_ERROR)
    return
  subelement=struktur["videos"]["episode"]
  for number,videos in subelement.iteritems(): 
    for video in videos:
        idd=video["id"]
        title=video["title"]
        title=title.replace("{S}","S").replace(".{E}","E")
        desc=video["description"]
        duration=video["videoDuration"]
        duration=duration/1000
        image=video["image"]["src"]
        airdate=video["airDate"]
        addLink(title,idd,"playvideo",image,desc=desc,duration=duration)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

def generatefiles(idd,name):
  url="https://www.dmax.de/api/show-detail/"+str(idd)
  debug("generatefiles :"+url)
  content=geturl(url)
  try:
    struktur = json.loads(content)
  except:   
    return
  mediapath=addon.getSetting("mediapath") 
  ppath=mediapath+name.replace(" ","_").replace(":","_")
  debug(ppath)
  if os.path.isdir(ppath):
    shutil.rmtree(ppath)
  os.mkdir(ppath)  
  serie=struktur["show"]["name"]
  subelement=struktur["videos"]["episode"]
  for number,videos in subelement.iteritems(): 
    for video in videos:         
        idd=video["id"]
        debug("IDD VIDEO :"+str(idd))
        title=video["title"]
        title=title.replace("{S}","S").replace(".{E}","E")
        desc=video["description"]
        duration=video["videoDuration"]
        duration=duration/1000
        image=video["image"]["src"]
        airdate=video["airDate"]
        season=video["season"]
        episode=video["episode"]
        namef=goldfinch.validFileName(title)
        #debug(namef)
        filename=os.path.join(ppath,namef+".strm")
        #debug(filename)
        file = open(filename,"wt") 
        file.write("plugin://plugin.video.L0RE.dmax/?mode=playvideo&url="+str(idd))
        file.close()
        nfostring="""
          <tvshow>
            <title>%s</title>
            <season>%s</season>
            <episode>%s</episode>
            <showtitle>%s</showtitle>
            <plot>%s</plot>
            <runtime>%s</runtime>
            <thumb aspect="" type="" season="">%s</thumb>            
            <aired>%s</aired>            
          </tvshow>"""           
        nfostring=nfostring%(title.encode("utf-8"),str(season).encode("utf-8"),str(episode),serie.encode("utf-8"),desc.encode("utf-8"),str(duration),image.encode("utf-8"),airdate.encode("utf-8"))          
        nfofile=os.path.join(ppath,namef+".nfo")           
        file = xbmcvfs.File(nfofile,"w")  
        file.write(nfostring)
        file.close()
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

def videoliste(url,page=1,nosub="",type="items"):
  if not "http" in url:
    url="http://www.dmax.de/"+url
  content=geturl(url)
  debug("videoliste : "+content)
  struktur = json.loads(content) 
  elemente=struktur[type]
  for element in elemente:
    debug("#####-#####")
    debug(element)
    title=element["title"]
    idd=element["id"]
    desc=element["description"]
    image=element["image"]["src"]
    addDir(title,idd,"listserie",image,desc=desc,addtype=1)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
  
def inputsettings():
  xbmcaddon.Addon("inputstream.adaptive").openSettings()  

debug("#######"+mode)  
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
          videoliste(url,page,nosub,type)
  if mode == 'listserie':
           listserie(url)
  if mode == 'tolibrary':                      
           tolibrary(url,name,stunden)
  if mode == 'inputsettings':
          inputsettings()    
  if mode == 'themenliste':
          themenliste()  
  if mode == 'generatefiles':         
          generatefiles(url,name)