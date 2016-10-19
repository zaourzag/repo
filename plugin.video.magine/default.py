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
import md5
import hashlib
import time,cookielib
import base64
cj = cookielib.CookieJar()

def getUrl(url,data="x",header=[]):
   global cj
   content=""
   debug("URL :::::: "+url)
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   userAgent = 'Coralie/1.7.2-2016081207(SM-G900F; Android; 6.0.1; DeviceId c248c629af1fe0a8c46b95668064c1d2952a9e91d27bccc3c5d584c2f7553a; Token Tvoli/ec9ab8acf27f14cacfefbf1087463fd3aeacdca4; VersionCheck)'
   header.append(('User-Agent', userAgent))
   header.append(('Accept', "*/*"))
   header.append(('Content-Type', "application/json;charset=UTF-8"))
   header.append(('Accept-Encoding', "plain"))
   header.append(('Origin', "https://magine.com"))
   opener.addheaders = header
   try:
      if data!="x" :
         request=urllib2.Request(url)
         cj.add_cookie_header(request)
         content=opener.open(request,data=data).read()
      else:
         content=opener.open(url).read()
   except urllib2.HTTPError as e:
       print e
   opener.close()
   return content







#data="clientId="+ session +"&mk=HTML5&md=PC&userId="+ userid
#content=getUrl("https://magine.com/api/drm/v4/license/widevine",data=data,Authorization=session,userId=userid)

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
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
defaultBackground = ""
defaultThumb = ""

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")


user=addon.getSetting("user") 
password=addon.getSetting("password") 

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
    
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',channelid="",times=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&channelid="+str(channelid)+"&times="+str(times)
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
def addDir(name, url, mode, iconimage, desc="",year="",channelid="",times=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&channelid="+str(channelid)+"&times="+str(times)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground
    liz.setProperty("fanart_image", iconimage)
  else:
    liz.setProperty("fanart_image", defaultBackground)
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
def login():
  user=addon.getSetting("user") 
  password=addon.getSetting("password") 
  values = {
      'accessKey' : password,
      'identity' : user
    }
  data = json.dumps(values)  
  try:
    content=getUrl("https://magine.com/api/login/v1/auth/magine",data=data)
    struktur = json.loads(content)
    session=struktur['sessionId']
    userid=struktur['userId']
  except:
    session=-1
    userid=-1
  return session,userid

def mediatek(session,userid):
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  content=getUrl("https://magine.com/api/content/v2/timeline/channels",header=header)
  struktur = json.loads(content)
  for channel in struktur:
     debug("_-----")
     debug(channel)
     name = channel["name"]     
     id = channel["id"]
     logoDark = channel["logoDark"]
     viewRecorded=channel["rights"]["viewRecorded"]
     subscribed=channel["subscribed"]
     if viewRecorded==True  and subscribed==True :
       addLink(name, "", "listchannel", logoDark, channelid=id)
  xbmcplugin.endOfDirectory(addon_handle)

def listchannel(session,userid,channelid):
  header=[]
  header.append (("Authorization","Bearer "+session))
  content=getUrl("https://magine.com/api/content/v2/timeline/airings?channels="+channelid+"&from=20160908T010000Z&to=20160908T050000Z",header=header)
  header.append (("UserId",userid))
  debug("-----------------------")
  debug(content)
  struktur = json.loads(content)
  
  
def mainmenu(session,userid):
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  content=getUrl("https://magine.com/api/channel/v1/users/"+userid,header=header)
  struktur = json.loads(content) 
  for element in struktur: 
    channelid=element["id"]
    logoDark=element["logoDark"]
    name=element["name"]    
    addLink(name, "", "playlive", "http://images.tvoli.com/channel-logos/"+str(channelid) +".png?width=128&height=128", channelid=channelid)
  xbmcplugin.endOfDirectory(addon_handle)
  
def playlive(url,session,userid,channelid):    
  debug("Playlive")
  playlist = xbmc.PlayList(1)
  playlist.clear() 
  timelist=[]  
  playlist=leseclips(session,userid,channelid,playlist,timelist)  
  xbmc.Player().play(playlist)
  counter1=0
  counter2=0
  while counter1<4:
    while xbmc.Player().isPlaying():  
        if counter2==10:
           counter2=0 
           if playlist.size()<3 :              
              playlist=leseclips(session,userid,channelid,playlist,timelist)  
        counter=0
        while counter < 60 and xbmc.Player().isPlaying():
            time.sleep(1)
            counter=counter+1
        counter2=counter2+1
        counter1=0                
    time.sleep(1)
    counter1=counter1+1  
  
  
def leseclips(session,userid,channelid,playlist,timelist):  
  debug("leseclips")
  header=[]    
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))  
  urx="https://magine.com/api/content/v2/feeds/channel-"+channelid
  content=getUrl(urx,header=header)
  struktur = json.loads(content)
  laenge=0
  for element in struktur["items"]:
    if laenge > 2:
      break
    laenge=laenge+1    
    times=str(element["id"])
    if not times in timelist:
      timelist.append(times)
      desc=element["description"]
      title=element["title"]
      debug("-------------- :"+str(times))  
      newurl="https://magine.com/api/contenturl/v1/channel/"+str(channelid)+"/airing/"+str(times)
      content=getUrl(newurl,header=header)
      struktur = json.loads(content)        
      userAgent = "Coralie/1.7.2-2016081207(SM-G900F; Android; 6.0.1; DeviceId c248c629af1fe0a8c46b95668064c1d2952a9e91d27bccc3c5d584c2f7553a; Token Tvoli/ec9ab8acf27f14cacfefbf1087463fd3aeacdca4; VersionCheck)"
      listitem = xbmcgui.ListItem(path=struktur["dash"])        
      debug("List Item gesetzt")      
      pin=addon.getSetting("pin") 
      lic_header="|Authorization=Bearer%20"+session+"&UserId=" +userid+"&Magine-ChannelId=" +channelid+"&Magine-Md=PC-Awesomesauce"+"&Magine-ParentalControlPinCode="+pin+"&Magine-Mk=HTML5"+"&Magine-ClientId=c060c1bf-d805-4feb-74d4-d8241e27d836"+"&Magine-ProgramId="+times+"|R{SSM}|"
      listitem.setProperty('inputstream.mpd.license_type', 'com.widevine.alpha')
      listitem.setProperty('inputstream.mpd.license_key', "https://magine.com/api/drm/v4/license/widevine"+lic_header)
      listitem.setProperty('inputstream.mpd.license_data', base64.b64encode(b'\x08\x01\x12\x10'+'{KID}'+b'\x1A\x05'+'tvoli"'+chr(len('channel.'+channelid+'.'+times))+'channel.'+channelid+'.'+times+'*'+b'\x02'+'SD2'+b'\x00'))
      listitem.setProperty('inputstreamaddon', 'inputstream.mpd')   
      listitem.setInfo( "video", { "Title" : title, "Plot" : desc} )    
      playlist.add(struktur["dash"], listitem)   
  return playlist

  
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
  
    


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
channelid = urllib.unquote_plus(params.get('channelid', ''))
times = urllib.unquote_plus(params.get('times', ''))
showName = urllib.unquote_plus(params.get('showName', ''))
hideShowName = urllib.unquote_plus(params.get('hideshowname', '')) == 'True'
nextPage = urllib.unquote_plus(params.get('nextpage', '')) == 'True'
einsLike = urllib.unquote_plus(params.get('einslike', '')) == 'True'    

session,userid=login()
# Haupt Menu Anzeigen      
if mode is '':
    if session==-1:
          dialog = xbmcgui.Dialog()
          nr=dialog.ok("User/Password", "Bitte Korrekten User und Password in Einstellungen hinterlegen") 
    else:          
        addDir(translation(30104) , url="-", mode="mainmenu", iconimage="")    
        #addDir("Mediatek" , url="-", mode="mediatek", iconimage="") 
    addDir(translation(30103), translation(30102), 'Settings', "")         
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  
if mode == 'playlive':
          playlive(url,session,userid,channelid)     
if mode == 'mainmenu':
          mainmenu(session,userid)      
if mode == 'mediatek':
          mediatek(session,userid)   
if mode == 'listchannel':
          listchannel(session,userid,channelid)    
if mode == 'Settings':
          addon.openSettings()          
