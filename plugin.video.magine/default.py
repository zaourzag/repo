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
import datetime
from tzlocal import get_localzone
#import pytz

try:
  tz = get_localzone()
  offset=tz.utcoffset(datetime.datetime.now()).total_seconds()
  _timezone_=int(offset)
except:  
  _timezone_ = int(__addon__.getSetting('time_offset'))*60*60 
print "_timezone_ :"+str(_timezone_)
# Setting Variablen Des Plugins
baseurl="https://magine.com"

cj = cookielib.CookieJar()


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
# Es geht um Videos
xbmcplugin.setContent(addon_handle, 'tvshows')
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
defaultBackground = ""
defaultThumb = ""

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")


user=addon.getSetting("user") 
password=addon.getSetting("password") 

xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)



if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)

def getUrl(url,data="x",header=[]):
   global cj
   content=""
   debug("URL :::::: "+url)
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   userAgent = "Coralie/1.7.2-2016081207(SM-G900F; Android; 6.0.1" 
   header.append(('User-Agent', userAgent))
   header.append(('Accept', "*/*"))
   header.append(('Content-Type', "application/json;charset=UTF-8"))
   header.append(('Accept-Encoding', "plain"))
   header.append(('Origin', baseurl))
   opener.addheaders = header
   try:
      if data!="x" :
         request=urllib2.Request(url)
         cj.add_cookie_header(request)
         content=opener.open(request,data=data).read()
      else:
         content=opener.open(url).read()
   except urllib2.HTTPError as e:
       debug ( e)
   opener.close()
   return content
   
   
def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',channelid="",times="",ids=0):
  u = base_url+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&channelid="+str(channelid)+"&times="+str(times)+"&ids="+str(ids)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)  
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
  #liz.setProperty("fanart_image", defaultBackground)
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  commands = []  
  link = "plugin://plugin.video.magine/?mode=mediathek_playvideo&channelid="+str(channelid)
  commands.append(( "Start from Beginning", 'XBMC.RunPlugin('+ link +')'))
  liz.addContextMenuItems( commands )

  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok
  
def addDir(name, url, mode, iconimage, desc="",year="",channelid="",times="",start="",ende="",id_such=""):
  u = base_url+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&channelid="+str(channelid)+"&times="+str(times)+"&start="+str(start)+"&ende="+str(ende)+"&id_such="+str(id_such)  
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)  
  liz.setProperty("fanart_image", iconimage)
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
    content=getUrl(baseurl+"/api/login/v1/auth/magine",data=data)
    struktur = json.loads(content)
    session=struktur['sessionId']
    userid=struktur['userId']
  except:
    session=-1
    userid=-1
  return session,userid

def getstreamtype():
  adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.adaptive", "properties": ["enabled"]}}')        
  sstruktur = json.loads(adaptivaddon) 
  is_type=""
  
  if not "error" in sstruktur.keys() :            
     if sstruktur["result"]["addon"]["enabled"]==True:
        is_type="inputstream.adaptive"
     if is_type=="":
        adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.mpd", "properties": ["enabled"]}}')        
        sstruktur = json.loads(adaptivaddon)           
        if not "error" in sstruktur.keys() :            
           if sstruktur["result"]["addon"]["enabled"]==True:
                is_type="inputstream.mpd"                
                
  if is_type=="":
     dialog = xbmcgui.Dialog()
     nr=dialog.ok("Inputstream", "Inputstream fehlt")
     return ""
  return is_type

def playdash(file,session,userid,channelid,ids,desc="",title="",is_type="",mediathek=0): 
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  content=getUrl(baseurl+"/api/time/v1",header=header)
  struktur = json.loads(content)  
  timestamp=int(struktur["nowUnixtime"])
  
  newurl=baseurl+"/api/airing/v2/"+str(ids)  
  content=getUrl(newurl,header=header)  
  struktur2 = json.loads(content)
  title=struktur2["title"]
  desc=struktur2["description"]
  try:
    stop=struktur["stopUnixtime"]
    dauer=stop-timestamp
  except:
    dauer=0
    stop=0
    
  listitem = xbmcgui.ListItem(path=file)        
  pin=addon.getSetting("pin")
  lic_header="|Authorization=Bearer%20"+session+"&UserId=" +userid+"&Magine-ChannelId=" +channelid+"&Magine-Md=PC-Awesomesauce"+"&Magine-ParentalControlPinCode="+pin+"&Magine-Mk=HTML5"+"&Magine-ClientId=c060c1bf-d805-4feb-74d4-d8241e27d836"+"&Magine-ProgramId="+ids+"|R{SSM}|" 
  listitem.setProperty(is_type+'.license_type', 'com.widevine.alpha')  
  listitem.setProperty(is_type+'.license_key', "https://magine.com/api/drm/v4/license/widevine"+lic_header)
  if mediathek==0:
    listitem.setProperty(is_type+'.license_data', base64.b64encode(b'\x08\x01\x12\x10'+'{KID}'+b'\x1A\x05'+'tvoli"'+chr(len('channel.'+channelid+'.'+ids))+'channel.'+channelid+'.'+ids+'*'+b'\x02'+'SD2'+b'\x00'))
  listitem.setProperty('inputstreamaddon', is_type)  
  listitem.setProperty(is_type+".manifest_type", "mpd")  
  listitem.setInfo( "video", { "Title" : title, "Plot" : desc} )    
  return listitem,dauer,stop  
   

def mediathek_channels(session,userid):
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  content=getUrl(baseurl+"/api/time/v1",header=header)
  struktur = json.loads(content)  
  timestamp=int(struktur["nowUnixtime"])
  content=getUrl(baseurl+"/api/channel/v1/users/"+userid,header=header)  
  struktur = json.loads(content)  
  channelid_arr=[]  
  name_arr=[]
  for element in struktur: 
      channelid_arr.append(element["id"])
      name_arr.append(element["name"])
  senderliste=",".join(channelid_arr)  
  now = datetime.datetime.utcfromtimestamp(timestamp)
  vontime = now - datetime.timedelta(hours=24)
  bistime = now 
  von=vontime.strftime("%Y%m%dT%H%M00Z")
  bis=bistime.strftime("%Y%m%dT%H%M00Z")
  debug("VON: "+von)
  debug("BIS: "+bis) 
  url=baseurl+"/api/content/v2/timeline/airings?channels="+senderliste+"&from="+von+"&to="+bis
  content=getUrl(url,header=header)  
  struktur_inhalt = json.loads(content)   
  for element1 in struktur_inhalt:        
    channel=element1
    channela=0
    for element in struktur_inhalt[element1]:      
      if element["rights"]["recorded"]["available"]==True:
            channel=element["channelId"]
            id=channelid_arr.index(channel)    
            channela=1 
            break
    if channela==1:            
      debug("BILD :"+"http://images.tvoli.com/channel-logos/"+str(channel) +".png?width=128&height=128")
      addDir(name_arr[id], "", "mediathek_selectdate", "http://images.tvoli.com/channel-logos/"+str(channel) +".png?width=128&height=128", channelid=str(channel))                   
  xbmcplugin.endOfDirectory(addon_handle)     
   
def mediathek_selectdate(session,userid,id_such):
   for i in xrange(0, 7):
        Tag=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(i),'%w')         
        datuma=translation(30130 + int(Tag))
        start=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(int(i)),'%Y%m%dT000000Z')
        ende=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(int(i))+datetime.timedelta(hours=24),'%Y%m%dT000000Z')
        addDir(datuma, "", "mediathek_filelist", "", start=start,ende=ende,id_such=id_such)                           
   xbmcplugin.endOfDirectory(addon_handle)
   
def mediathek_filelist(session,userid,id_such,start,ende):
  debug(".START. "+start)
  debug(".ENDE. "+ende)
  debug(".id_such. "+id_such)
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  content=getUrl(baseurl+"/api/time/v1",header=header)
  struktur = json.loads(content)  
  timestamp=int(struktur["nowUnixtime"])
  content=getUrl(baseurl+"/api/channel/v1/users/"+userid,header=header)  
  struktur = json.loads(content)  
  channelid_arr=[]  
  name_arr=[]
  for element in struktur: 
   channelid_arr.append(element["id"])
   name_arr.append(element["name"])
  senderliste=",".join(channelid_arr)
  
  now = datetime.datetime.utcfromtimestamp(timestamp)
  vontime = now - datetime.timedelta(hours=24)
  bistime = now 
  von=start
  bis=ende
  debug("VON: "+von)
  debug("BIS: "+bis) 
  url=baseurl+"/api/content/v2/timeline/airings?channels="+senderliste+"&from="+von+"&to="+bis
  content=getUrl(url,header=header)  
  struktur_inhalt = json.loads(content)   
  for element in struktur_inhalt:        
    channel=element
    for element in struktur_inhalt[element]:       
        #debug("----"+element["rights"]["recorded"]["available"])    
        if element["rights"]["recorded"]["available"]==True:
           debug("++++-")
           debug(element)
           title=element["title"]
           channel=element["channelId"]
           ids=element["id"]
           bild=element["image"]
           startzeit=element["startUnixtime"]- _timezone_  +3600
           #start = int(time.mktime(startzeit)) + _timezone_  # local timestamp
           start=datetime.datetime.fromtimestamp(startzeit).strftime('%d.%m. %H:%M')
           id=channelid_arr.index(channel) 
           title=start+" "+title+" ( "+name_arr[id]+" )"           
           if id_such==channel:
             addLink(title, "", "mediathek_playvideo", bild, channelid=channel,ids=ids)     
  xbmcplugin.endOfDirectory(addon_handle)
    
def mediathek_playvideo(session,userid,channelid,ids):
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  newurl=baseurl+"/api/contenturl/v1/channel/"+str(channelid)+"/airing/"+str(ids)  
  content=getUrl(newurl,header=header)  
  struktur = json.loads(content)
  debug("mediathek_playvideo struktur : ")
  debug(struktur)
  userAgent = "Coralie/1.7.2-2016081207(SM-G900F; Android; 6.0.1" 
  debug("List Item gesetzt")      
  is_type=getstreamtype()  
  if is_type=="":     
     return "" 
  debug("XXX YYYY")     
  debug(is_type)  
  listitem,dauer,stop=playdash(struktur["dash"],session,userid,channelid,ids,is_type=is_type,mediathek=1)
  xbmcplugin.setResolvedUrl(addon_handle, True, listitem)


def live_mytv(session,userid):
  anzeige=addon.getSetting("anzeige")   
  debug("anzeige")
  debug(anzeige)
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))  
  content=getUrl(baseurl+"/api/your-tv/v1/sections",header=header)  
  struktur = json.loads(content)     
  for element in struktur["sections"][0]["sectionItems"][0]["subsection"]["items"]: 
        debug("element :")
        debug(element)
        element=element["airing"]
        ids=element["id"]
        debug (element)
        bild=element["image"] 
        kanal_name=element["channel"]["name"]
        kanal_id=element["channel"]["id"]
        zeit=element["id"]        
        senung_name=element["title"]
        titel=kanal_name +" - "+senung_name
        if anzeige=="0":
          titel=kanal_name +" - "+senung_name
        if anzeige=="1":
          titel=senung_name +" - "+kanal_name 
        if anzeige=="2":
          titel=kanal_name
        if anzeige=="3":
          titel=senung_name          
        addLink(titel, "", "mediathek_playvideo", bild, channelid=str(kanal_id),ids=ids)
  xbmcplugin.endOfDirectory(addon_handle)  
  
def live_channels(session,userid):
  anzeige=addon.getSetting("anzeige")   
  debug("anzeige")
  debug(anzeige)
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))  
  content=getUrl(baseurl+"/api/channel/v1/users/"+userid,header=header)  
  struktur = json.loads(content)   
  bild_arr=[]
  kanal_name_arr=[]
  kanal_id_arr=[]
  kanalliste=""  
  for element in struktur: 
        debug("element :")       
        debug (element)
        bild_arr.append(element["logoDark"])
        kanal_name_arr.append(element["name"])
        kanal_id_arr.append(element["id"])  
        kanalliste=kanalliste+str(element["id"])+","
  kanalliste=kanalliste[:-1] 
  now = datetime.datetime.now()- datetime.timedelta(seconds=_timezone_)
  vontime = now - datetime.timedelta(hours=3)
  bistime = now + datetime.timedelta(hours=3)
  von=vontime.strftime("%Y%m%dT%H%M00Z")
  bis=bistime.strftime("%Y%m%dT%H%M00Z")
  urlb=baseurl+"/api/content/v2/timeline/airings?channels="+kanalliste+"&from="+von+"&to="+bis
  content=getUrl(urlb,header=header)  
  struktur = json.loads(content)   
  for i in range(0,len(kanal_id_arr),1):
     kanal_name=kanal_name_arr[i]
     bild=bild_arr[i]
     kanal_id=kanal_id_arr[i]
     senung_name=kanal_name_arr[i]
     for sendung in struktur[kanal_id]:
        bild=sendung["image"]
        start=datetime.datetime.utcfromtimestamp(int(sendung["startUnixtime"]))  
        stop=datetime.datetime.utcfromtimestamp(int(sendung["stopUnixtime"]))  
        senung_name=sendung["title"]
        if now> start and now < stop:
                      
            debug ("Gefunden :")
            debug(sendung)
            titel=sendung["title"]
            titel=kanal_name +" - "+senung_name
            if anzeige=="0":
              titel=kanal_name +" - "+senung_name
            if anzeige=="1":
              titel=senung_name +" - "+kanal_name
            if anzeige=="2":
              titel=kanal_name
            if anzeige=="3":
              titel=senung_name
            addLink(titel, "", "live_play", bild, channelid=str(kanal_id),ids="")
  xbmcplugin.endOfDirectory(addon_handle)

                
def live_play(url,session,userid,channelid,ids):      
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  debug("Start :"+ids)
  #https://magine.com/api/content/v2/feeds/channel-11245
  if ids=="":
    content=getUrl(baseurl+"/api/content/v2/feeds/channel-"+str(channelid),header=header)  
    struktur = json.loads(content)   
    debug("live_play Struktur Channel :")    
    debug(struktur)
    now = datetime.datetime.now()- datetime.timedelta(seconds=_timezone_)
    for element in struktur["items"]:
        start=datetime.datetime.utcfromtimestamp(int(element["startUnixtime"]))  
        stop=datetime.datetime.utcfromtimestamp(int(element["stopUnixtime"])) 
        if now> start and now < stop:               
           times=element["id"]           
  else:
    times=ids
  debug("TIMES :"+str(times))
  debug("live_play")
  playlist = xbmc.PlayList(1)
  playlist.clear() 
  item,title,next,dauer=live_leseclips(times,session,userid,channelid)
  playlist.add(title, item)  
  debug("NEXT :"+ str(next))  
  xbmc.Player().play(playlist)
  time.sleep(3)
  while xbmc.Player().isPlaying():  
    dauer=dauer-300
    if dauer<0:
      dauer=1
    time.sleep(dauer)    
    dauer=0
    try:
        item,title,next,dauer=live_leseclips(next,session,userid,channelid)  
    except:
         pass
    playlist.add(title, item) 
    #xbmc.executebuiltin('Container.Refresh')
  time.sleep(10000)
  #xbmc.executebuiltin('Container.Refresh')
  
    
def live_leseclips(url,session,userid,channelid):  
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  debug("leseclips")
  times=url
  path=str(times)[0:5]
  header=[]    
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))  
  
  content=getUrl(baseurl+"/api/contenturl/v1/channel/"+ channelid +"/airing/"+times,header=header)
  struktur= json.loads(content) 
  dash_file=struktur["dash"]
  debug(struktur)
 
  is_type=getstreamtype()  
  if is_type=="":     
     return ""  
  listitem,dauer,stop=playdash(dash_file,session,userid,channelid,times,is_type=is_type) 
  return listitem,dash_file,str(path)+str(stop),dauer

  
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
ids = urllib.unquote_plus(params.get('ids', ''))
times = urllib.unquote_plus(params.get('times', ''))
start = urllib.unquote_plus(params.get('start', ''))
ende = urllib.unquote_plus(params.get('ende', ''))
id_such= urllib.unquote_plus(params.get('id_such', ''))

session,userid=login()
# Haupt Menu Anzeigen      
if mode is '':
    if session==-1:
          dialog = xbmcgui.Dialog()
          nr=dialog.ok(translation(30138), translation(30137)) 
    else:          
        addDir(translation(30104) , url="-", mode="live_channels", iconimage="")    
        addDir(translation(30137) , url="-", mode="mediathek_channels", iconimage="") 
        addDir(translation(30146) , url="-", mode="live_mytv", iconimage="") 
    addDir(translation(30103), "", 'Settings', "")         
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  
if mode == 'live_play':
          live_play(url,session,userid,channelid,ids)     
if mode == 'live_channels':
          live_channels(session,userid)      
if mode == 'mediathek_channels':
          mediathek_channels(session,userid)   
if mode == 'live_mytv':
          live_mytv(session,userid)             
if mode == 'listchannel':
          listchannel(session,userid,channelid)    
if mode == 'mediathek_selectdate':
           mediathek_selectdate(session,userid,channelid)
if mode == 'mediathek_playvideo':
          mediathek_playvideo(session,userid,channelid,ids)    
if mode == 'mediathek_filelist':
          mediathek_filelist(session,userid,id_such,start,ende)         
if mode == 'Settings':
          addon.openSettings()          
