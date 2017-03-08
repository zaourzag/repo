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
import dailymotion
import YDStreamExtractor



import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

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


#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       
xbmcplugin.setContent(int(sys.argv[1]), 'musicvideos')
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
username=addon.getSetting("User")



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
  
    
def addDir(name, url, mode, iconimage, desc="",page="1"):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)
  ok = True
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
  commands = []
  listartist = "plugin://plugin.video.ampya/?mode=songs_from_artist&url="+urllib.quote_plus(str(artist_id))  
  listsimilar = "plugin://plugin.video.ampya/?mode=list_similar&url="+urllib.quote_plus(str(liedid))  
  commands.append(( translation(30109) , 'ActivateWindow(Videos,'+ listartist +')'))
  commands.append(( translation(30110) , 'ActivateWindow(Videos,'+ listsimilar +')'))
  liz.addContextMenuItems( commands )  
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
  


page="1"   
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
page = urllib.unquote_plus(params.get('page', ''))

def channels():
  d = dailymotion.Dailymotion()
  videos=d.get('/channels')
  for element in videos["list"]:
    addDir(element["name"], element["id"], 'channelmenu', "",desc=element["description"])  
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  
  
def channelmenu(id,page="1") :  
  addDir("Most Recent", '/channel/'+id+"/videos?sort=recent"  , 'channel', "")    
  addDir("Most Viewed", '/channel/'+id+"/videos?sort=visited"  , 'channeldate', "")     
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  

def channeldate(url,page="1"):
  debug("URL channeldate: "+ url)
  addDir("Hour", url+"-hour"  , 'channel', "")   
  addDir("Today", url+"-today"  , 'channel', "")   
  addDir("Week", url+"-week"  , 'channel', "")   
  addDir("Month", url+"-month" , 'channel', "")   
  addDir("All Time", url  , 'channel', "") 
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
  
def channel(url,page="1"):
  debug("URL channel: "+ url)
  debug("Page :"+page)
  d = dailymotion.Dailymotion()
  channel=d.get(url+"&page="+page)
  for element in channel["list"]:
    addLink(element["title"], element["id"], 'video', "http://www.dailymotion.com/thumbnail/video/"+element["id"])  
  page=int(page)+1
  debug("nextpage :"+str(page))
  addDir("Next", url, "channel","",page=str(page))   
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     
  
def video(id)  :
  Quality=addon.getSetting("Quality") 
  debug("Quality :"+Quality)
  d = dailymotion.Dailymotion()
  video=d.get('/video/'+id+'?fields=url')
  url=video["url"]
  vid = YDStreamExtractor.getVideoInfo(url,quality=Quality) #quality is 0=SD, 1=720p, 2=1080p and is a maximum
  try:
      stream_url = vid.streamURL() #This is what Kodi (XBMC) will play
      stream_url=stream_url.split("|")[0]
      debug("stream_url :"+stream_url)
      listitem = xbmcgui.ListItem(path=stream_url)  
      xbmcplugin.setResolvedUrl(addon_handle,True, listitem) 
  except:
     xbmc.executebuiltin('XBMC.Notification("VideoURL not found","VideoURL not found")')
     xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     


def search(id,page="1"):
   dialog = xbmcgui.Dialog()
   dd= dialog.input("Search", type=xbmcgui.INPUT_ALPHANUM)
   displaypage('/videos?fields=id,thumbnail_720_url,title,url,&search='+dd,page)

def displaypage(url,page="1"):   
   d = dailymotion.Dailymotion()
   video=d.get(url+'&page='+page)
   for element in video["list"]:
     addLink(element["title"], element["id"], 'video', element["thumbnail_720_url"])  
   page=int(page)+1
   debug("nextpage :"+str(page))
   addDir("Next", url, "displaypage","",page=str(page))        
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     
def user():
    addDir("Most Popular", "/users?fields=avatar_720_url,id,username&mostpopular=1"  , 'userpage', "",page=1)    
    addDir("Recomanded", "/users?fields=avatar_720_url,id,username&recommended=1"  , 'userpage', "",page=1)    
    addDir("Official", "/users?fields=avatar_720_url,id,username&verified=1"  , 'userpage', "",page=1)    
    addDir("All", "/users?fields=avatar_720_url,id,username"  , 'userpage', "",page=1)    
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
def playlist(id):
    url="https://api.dailymotion.com/playlist/"+id+"/videos?fields=id,thumbnail_720_url,title,url"
    displaypage(url,page="1")
    
def playlistenmenu():
    addDir("Most Popular", "/playlists?fields=id,name,thumbnail_720_url,&sort=most"  , 'playlisten', "",page=1)   
    addDir("Neueste", "/playlists?fields=id,name,thumbnail_720_url,&sort=recent"  , 'playlisten', "",page=1)   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def playlisten(url,page):
   d = dailymotion.Dailymotion()
   video=d.get(url+'&page='+page)
   for element in video["list"]:
     addDir(element["name"], element["id"], 'playlist', element["thumbnail_720_url"])  
   page=int(page)+1
   debug("nextpage :"+str(page))
   addDir("Next", url, "playlisten","",page=str(page))        
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     
    
def userpage(url,page="1") :   
  d = dailymotion.Dailymotion()
  channel=d.get(url+"&page="+page)
  for element in channel["list"]:
      addDir(element["username"], element["id"], 'uservideo', element["avatar_720_url"])  
  page=int(page)+1
  debug("nextpage :"+str(page))
  addDir("Next", url, "userpage","",page=str(page))   
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     
  
def uservideo(id,page="1")  :
  debug(":uservideo:")  
  debug(":ID:"+id)  
  d = dailymotion.Dailymotion()
  channel=d.get("/user/"+str(id)+"/videos?fields=id,thumbnail_720_url,title&page="+str(page))
  for element in channel["list"]:
      addLink(element["title"], element["id"], 'video', element["thumbnail_720_url"])  
  page=int(page)+1
  debug("nextpage :"+str(page))
  addDir("Next", id, "uservideo","",page=str(page))   
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     

def mystuff():
  addDir("Recomendation", "/user/"+username+"/recommended?fields=avatar_720_url,id,username,", 'userpage', "")    
  addDir("Following", "/user/"+username+"/following?fields=avatar_720_url,id,username,", 'userpage', "")    
  addDir("Subscription", "/user/"+username+"/subscriptions?fields=id,thumbnail_720_url,title", 'displaypage', "")    
  addDir("Likes", "/user/"+username+"/likes?fields=id,thumbnail_720_url,title", 'displaypage', "")    
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  
  
if mode is '':
    if not username=="":
      addDir("My Stuff", "", 'mystuff', "")  
    addDir("Channels", "", 'channels', "")  
    addDir("User", "", 'user', "")  
    addDir("Live", "https://api.dailymotion.com/videos?fields=id,thumbnail_720_url,title,url,&live=1&sort=recent", 'displaypage', "")  
    addDir("Playlisten", "https://api.dailymotion.com/videos?fields=id,thumbnail_720_url,title,url,&live=1&sort=recent", 'playlistenmenu', "")  
    addDir("Search", '','search',"")    
    addDir("Einstellungen", "", 'Settings', "")        
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'channels':
          channels() 
  if mode == 'channel':
          channel(url,page) 
  if mode == 'channelmenu':
          channelmenu(url,page)           
  if mode == 'video':
          video(url)   
  if mode == 'search':
          search(url,page) 
  if mode == 'displaypage':
          displaypage(url,page)     
  if mode == 'channeldate':
          channeldate(url,page)         
  if mode == 'user':
          user()       
  if mode == 'userpage':
          userpage(url,page)    
  if mode == 'uservideo':
          uservideo(url,page)                                      
  if mode == 'playlistenmenu':
          playlistenmenu()                            
  if mode == 'playlisten':
          playlisten(url,page)      
  if mode == 'playlist': 
        playlist(url)      
  if mode == 'mystuff':
        mystuff()  