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
from datetime import datetime



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
profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)

icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"


def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def addDir(name, url, mode, iconimage, desc="",ids=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&ids="+str(ids)
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
  
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
  
  
def getUrl(url,data="x",token=""):
        print("Get Url: " +url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        userAgent = "YOUTV/1.2.7 CFNetwork/758.2.8 Darwin/15.0.0"
        if token!="":
           mytoken="Token token="+ token
           opener.addheaders = [('User-Agent', userAgent),
                                ('Authorization', mytoken)]
        else:
           opener.addheaders = [('User-Agent', userAgent)]
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             print e
        opener.close()
        return content

def login():
   global addon   
   if xbmcvfs.exists(temp+"/token")  :
     f=xbmcvfs.File(temp+"/token","r")   
     token=f.read()
   else:
      user=addon.getSetting("user")        
      password=addon.getSetting("pw") 
      debug("User :"+ user)
      values = {
         'auth_token[password]' : password,
         'auth_token[email]' : user
      }
      data = urllib.urlencode(values)
      content=getUrl("https://www.youtv.de/api/v2/auth_token.json?platform=ios",data=data)
      struktur = json.loads(content)   
      token=struktur['token']
      f = open(temp+"token", 'w')           
      f.write(token)        
      f.close()    
   
   return token
        
def getThemen(url,filter):
   token=login()
   if filter=="channels" :
     dialog = xbmcgui.Dialog()
     d = dialog.input(translation(30009), type=xbmcgui.INPUT_DATE)
     d=d.replace(' ','0')  
     d= d[6:] + "-" + d[3:5] + "-" + d[:2]
     datum="&date="+d
   else:
     datum=""
   content=getUrl(url,token=token)     
   debug("+X:"+ content)
   struktur = json.loads(content)
   themen=struktur[filter]   
   for name in themen:
      namen=unicode(name["name"]).encode("utf-8")
      id=name["id"]
      if filter=="filters" :
         mode="listtop"
         logo=""
      if filter=="genres" :
         mode="listgenres"
         logo=""
      if filter=="channels" :
         mode="listtv"       
         logo=name["logo"][0]["url"]
      addDir(namen, namen, mode+datum,logo,ids=str(id))
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def liste(url,filter):
   datums = urllib.unquote_plus(params.get('date', ''))
   if  datums!="":
     url=url+"&date="+ datums
   debug("+++- :"+ url)
   token=login()
   content=getUrl(url,token=token) 
   debug("+X:"+ content)
   struktur = json.loads(content)   
   themen=struktur[filter]   
   for name in themen:
     #2016-02-26T21:15:00.000+01:00
     
     endtime=unicode(name["ends_at"]).encode("utf-8")     
     match=re.compile('(.+?)\..+', re.DOTALL).findall(endtime)
     endtime=match[0]
     timeString  = time.strptime(endtime,"%Y-%m-%dT%H:%M:%S")
     enttime=time.mktime(timeString)
     
     starttime=unicode(name["starts_at"]).encode("utf-8")
     match=re.compile('(.+?)-(.+?)-(.+?)T(.+?):(.+?):', re.DOTALL).findall(starttime)
     times=match[0][2] +"."+ match[0][1] +"."+ match[0][0] +" "+ match[0][3] +":"+match[0][4] +" "


     
     nowtime=time.mktime(datetime.now().timetuple())
     title=unicode(name["title"]).encode("utf-8")
     id=str(name["id"])
     bild=unicode(name["image"][0]["url"]).encode("utf-8")
     duration=str(name["duration"])
     genres=unicode(name["genre"]["name"]).encode("utf-8") 
     if enttime < nowtime:
         addLink(times+title, id, "playvideo", bild, duration=duration, desc="", genre=genres)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def playvideo(id):  
  quaname=[]
  qalfile=[]
  bitrate=addon.getSetting("bitrate")
  debug("ID :::"+ id)
  token=login()
  content=getUrl("https://www.youtv.de/api/v2/broadcast_files/"+ str(id) +".json?platform=ios",token=token)
  debug("+X+ :"+ content)
  struktur = json.loads(content) 
  qulitaet=struktur["files"]  
  for name in qulitaet:  
     quaname.append(name["quality_description"])
     qalfile.append(name["file"])
  if bitrate=="Min":
    file=qalfile[0]
  if bitrate=="Max":
    file=qalfile[-1]
  if bitrate=="Select":
     dialog = xbmcgui.Dialog()
     nr=dialog.select("Bitrate", quaname)      
     file=qalfile[nr]  
  listitem = xbmcgui.ListItem(path=file)  
  xbmcplugin.setResolvedUrl(addon_handle,True, listitem)  
  print("####"+   content)
   
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
ids = urllib.unquote_plus(params.get('ids', ''))
def search(url=""):
   filter="broadcasts"
   dialog = xbmcgui.Dialog()
   d = dialog.input(translation(30010), type=xbmcgui.INPUT_ALPHANUM)
   token=login()
   content=getUrl("https://www.youtv.de/api/v2/broadcasts/search.json?q="+ d +"&platform=ios",token=token)
   struktur = json.loads(content)   
   themen=struktur[filter]   
   for name in themen:
     title=unicode(name["title"]).encode("utf-8")
     id=str(name["id"])
     bild=unicode(name["image"][0]["url"]).encode("utf-8")
     duration=str(name["duration"])
     genres=unicode(name["genre"]["name"]).encode("utf-8") 
     addLink(title, id, "playvideo", bild, duration=duration, desc="", genre=genres)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
# Haupt Menu Anzeigen      
if mode is '':
    addDir(translation(30103), translation(30001), 'TOP', "")
    addDir(translation(30104), translation(30005), 'Genres',"")
    addDir(translation(30105), translation(30006), 'Sender', "")   
    addDir(translation(30107), translation(30107), 'Search', "")  
    addDir(translation(30108), translation(30108), 'Archive',"")  
    addDir(translation(30106), translation(30106), 'Settings', "")        
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'TOP':
          getThemen("https://www.youtv.de/api/v2/filters.json?platform=ios","filters")
  if mode == 'Genres':
          getThemen("https://www.youtv.de/api/v2/genres.json?platform=ios","genres")   
  if mode == 'Sender':
          getThemen("https://www.youtv.de/api/v2/channels.json?platform=ios ","channels")             
  if mode == 'listtv':
          #date=2016-02-26&
          liste("https://www.youtv.de/api/v2/channels/"+ ids +"/broadcasts.json?platform=ios","broadcasts")                 
  if mode == 'listgenres':
          #date=2016-02-26&
          liste("https://www.youtv.de/api/v2/genres/"+ ids +"/broadcasts.json?platform=ios","broadcasts")                 
  if mode == 'listtop':
          #date=2016-02-26&
          liste("https://www.youtv.de/api/v2/filters/"+ ids +"/broadcasts.json?platform=ios","broadcasts")                           
  if mode == 'Archive':
          #date=2016-02-26&
          liste("https://www.youtv.de/api/v2/archived_broadcasts.json?platform=ios","archived_broadcasts")                      
  if mode == 'playvideo':  
          playvideo(url)  
  if mode == 'Search':  
          search(url)           
      