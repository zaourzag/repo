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
  cd=addon.getSetting("password")  
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
  #liz.setProperty("fanart_image", defaultBackground)
  commands = []
  finaladd = "plugin://plugin.video.youtv/?mode=addit&url="+urllib.quote_plus(url)
  finaldel = "plugin://plugin.video.youtv/?mode=delit&url="+urllib.quote_plus(url)
  
  seriendel = "plugin://plugin.video.youtv/?mode=sdel&url="+urllib.quote_plus(url)
  serienadd = "plugin://plugin.video.youtv/?mode=sadd&url="+urllib.quote_plus(url)
  
  download = "plugin://plugin.video.youtv/?mode=download&url="+urllib.quote_plus(url)      
  commands.append(( 'Add to Archive', 'XBMC.RunPlugin('+ finaladd +')'))   
  commands.append(( 'Del from Archive', 'XBMC.RunPlugin('+ finaldel +')'))   
  commands.append(( 'Add to Serie', 'XBMC.RunPlugin('+ seriendel +')'))   
  commands.append(( 'Del from Serie', 'XBMC.RunPlugin('+ serienadd +')'))  
  if cd=="4921":
     commands.append(( 'Download', 'XBMC.RunPlugin('+ download +')'))     
  liz.addContextMenuItems( commands )
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok
def addLinkarchive(name, url, mode, iconimage, duration="", desc="", genre=''):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
  #liz.setProperty("fanart_image", defaultBackground)
  commands = []
  download = "plugin://plugin.video.youtv/?mode=download&url="+urllib.quote_plus(url)    
  finaldel = "plugin://plugin.video.youtv/?mode=delit&url="+urllib.quote_plus(url)    
  commands.append(( 'Del from Archive', 'XBMC.RunPlugin('+ finaldel +')'))   
  commands.append(( 'Download', 'XBMC.RunPlugin('+ download +')'))   
  liz.addContextMenuItems( commands )
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok
  
  
def addLinkSeries(name, url, mode, iconimage, duration="", desc="", genre=''):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
  #liz.setProperty("fanart_image", defaultBackground)
  commands = []
  seriendel = "plugin://plugin.video.youtv/?mode=sdeldirekt&url="+urllib.quote_plus(url)  
  commands.append(( 'Delete Serie', 'XBMC.RunPlugin('+ seriendel +')'))         
  liz.addContextMenuItems( commands )
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
   
def Genres():
   url="https://www.youtv.de/api/v2/genres.json?platform=ios"
   token=login()  
   content=getUrl(url,token=token)        
   struktur = json.loads(content)
   themen=struktur["genres"]   
   for name in themen:
      namen=unicode(name["name"]).encode("utf-8")
      id=name["id"]   
      addDir(namen, namen, "Subgeneres","",ids=str(id))
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
   
def subgenres(ids):
  debug("IDS: "+ ids)
  url="https://www.youtv.de/api/v2/genres.json?platform=ios"  
  token=login()  
  content=getUrl(url,token=token)        
  struktur = json.loads(content)
  themen=struktur["genres"]   
  for name in themen:
      id=name["id"]  
      debug("ID: "+ str(id))
      if str(id)==str(ids) :         
         subgen=name["genres"] 
         addDir("Alle", "Alle", "listgenres","",ids=str(id))         
         for subname in subgen:
            namen=unicode(subname["name"]).encode("utf-8")
            id=subname["id"]    
            addDir(namen, namen, "listgenres","",ids=str(id))
         break
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
   
def getThemen(url,filter):
   token=login()   
   if filter=="channels" :
     datuma=["Heute","Gestern"]     
     for i in xrange(2, 7):
        Tag=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(i),'%A')
        datuma.append(Tag)
     dialog = xbmcgui.Dialog()
     nr=dialog.select("Datum", datuma)
     tagit=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(nr),'%Y-%m-%d')
     datum="&date="+tagit
     
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
   content=getUrl("https://www.youtv.de/api/v2/subscription.json?platform=ios",token=token)
   struktur = json.loads(content) 
   tage=struktur["subscription"]["history_days"]
      
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
     
     st=unicode(name["starts_at"]).encode("utf-8")
     starttime=st
     match=re.compile('(.+?)\..+', re.DOTALL).findall(starttime)
     starttime=match[0]  
     timeString  = time.strptime(starttime,"%Y-%m-%dT%H:%M:%S")     
     starttime=time.mktime(timeString)
     
     nowtime=time.mktime(datetime.datetime.now().timetuple())
     diftime=nowtime-starttime
     diftime2=int(diftime/  84400)       
          
     match=re.compile('(.+?)-(.+?)-(.+?)T(.+?):(.+?):', re.DOTALL).findall(st)
     times=match[0][2] +"."+ match[0][1] +"."+ match[0][0] +" "+ match[0][3] +":"+match[0][4] +" "
          
     title=unicode(name["title"]).encode("utf-8")
     subtitle=unicode(name["subtitle"]).encode("utf-8")
     if subtitle!= "None":
       title=title+" ( "+subtitle +" )"
     id=str(name["id"])
     bild=unicode(name["image"][0]["url"]).encode("utf-8")
     duration=str(name["duration"])
     genres=unicode(name["genre"]["name"]).encode("utf-8") 
     if enttime < nowtime and diftime2<tage:
         if filter!="archived_broadcasts":
            addLink(times+title, id, "playvideo", bild, duration=duration, desc="", genre=genres)
         else:
            addLinkarchive(times+title  , id, "playvideo", bild, duration=duration, desc="", genre=genres)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

   
   
def download(id):  
  download_dir=addon.getSetting("download_dir")    
  if download_dir=="":
       dialog = xbmcgui.Dialog()
       dialog.ok("Error", "Es ist keine Download Ordner eingestellt")  
       return 0
  quaname=[]
  qalfile=[]
  qname=[]
  bitrate=addon.getSetting("bitrate")
  debug("ID :::"+ id)
  token=login()
  content=getUrl("https://www.youtv.de/api/v2/broadcast_files/"+ str(id) +".json?platform=ios",token=token)
  debug("+X+ :"+ content)
  struktur = json.loads(content) 
  qulitaet=struktur["files"]
  nq=""
  hq=""
  hd=""

  for name in qulitaet:  
     quaname.append(name["quality_description"])
     qalfile.append(name["file"])  

     # Normal 
     if name["quality"]=="nq" :        
        nq=name["file"]        

     # High Quality 
     if name["quality"]=="hq" :
        hq=name["file"]     

     # HD
     if name["quality"]=="hd" :
        hd=name["file"]

  #MAX      
  if hd!="":
      max=hd
  elif hq!="":
      max=hq
  else :
      max=nq  
  #MIN
  if nq!="":
    min=nq
  elif hq!="":
    min=hq
  else:
    min=hd
  if bitrate=="Min":
    file=min      
  if bitrate=="Max":
     file=max
  if bitrate=="Select":
     dialog = xbmcgui.Dialog()
     nr=dialog.select("Bitrate", quaname)      
     file=qalfile[nr]  
     
  file_name = file.split('/')[-1]     
  progress = xbmcgui.DialogProgress()
  progress.create("Youtv","Downloading File",file_name)
  u = urllib2.urlopen(file)
  f = open(download_dir + file_name, 'wb')
  meta = u.info()
  file_size = int(meta.getheaders("Content-Length")[0])
  #print "Downloading: %s Bytes: %s" % (file_name, file_size)

  file_size_dl = 0
  block_sz = 16384
  while True:
    buffer = u.read(block_sz)
    if not buffer:
        break

    file_size_dl += len(buffer)
    f.write(buffer)
    process= int( file_size_dl * 100. / file_size)
    progress.update(process)
    if progress.iscanceled():         
        progress.close()
        f.close()
        break
  f.close()
  
  
  
  progress.create('Progress', 'This is a progress bar.')     
  #urllib.urlretrieve (file, temp+"/mp3.mp3")
  print("####"+   content)
   
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
ids = urllib.unquote_plus(params.get('ids', ''))
genid = urllib.unquote_plus(params.get('genid', ''))

   
   
#List Serien Einträge   
def Series(url,filter):
   
   token=login()
   content=getUrl(url,token=token) 
   debug("+X:"+ content)
   struktur = json.loads(content)   
   themen=struktur[filter]   
   for name in themen:
     #2016-02-26T21:15:00.000+01:00       
     title=unicode(name["title"]).encode("utf-8")
     id=str(name["id"])     
     addLinkSeries(title, id, "", "", duration="", desc="", genre="")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
   

def playvideo(id):  
  quaname=[]
  qalfile=[]
  qname=[]
  bitrate=addon.getSetting("bitrate")
  debug("ID :::"+ id)
  token=login()
  content=getUrl("https://www.youtv.de/api/v2/broadcast_files/"+ str(id) +".json?platform=ios",token=token)
  debug("+X+ :"+ content)
  struktur = json.loads(content) 
  qulitaet=struktur["files"]
  nq=""
  hq=""
  hd=""

  for name in qulitaet:  
     quaname.append(name["quality_description"])
     qalfile.append(name["file"])  

     # Normal 
     if name["quality"]=="nq" :        
        nq=name["file"]        

     # High Quality 
     if name["quality"]=="hq" :
        hq=name["file"]     

     # HD
     if name["quality"]=="hd" :
        hd=name["file"]

  #MAX      
  if hd!="":
      max=hd
  elif hq!="":
      max=hq
  else :
      max=nq  
  #MIN
  if nq!="":
    min=nq
  elif hq!="":
    min=hq
  else:
    min=hd
  if bitrate=="Min":
    file=min      
  if bitrate=="Max":
     file=max
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
genid = urllib.unquote_plus(params.get('genid', ''))

def search(url=""):
   filter="broadcasts"
   dialog = xbmcgui.Dialog()
   d = dialog.input(translation(30010), type=xbmcgui.INPUT_ALPHANUM)
   token=login()
   content=getUrl("https://www.youtv.de/api/v2/broadcasts/search.json?q="+ d +"&platform=ios",token=token)
   debug("Content")
   struktur = json.loads(content)   
   themen=struktur[filter]   
   for name in themen:
     title=unicode(name["title"]).encode("utf-8")
     subtitle=unicode(name["subtitle"]).encode("utf-8")
     if subtitle!= "None":
       title=title+" ( "+subtitle +" )"
     id=str(name["id"])
     bild=unicode(name["image"][0]["url"]).encode("utf-8")
     duration=str(name["duration"])
     genres=unicode(name["genre"]["name"]).encode("utf-8") 
     addLink(title, id, "playvideo", bild, duration=duration, desc="", genre=genres)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
# Haupt Menu Anzeigen      

def addit(id):
  token=login()                  
#  content=getUrl("https://www.youtv.de/api/v2/broadcasts/"+ str(id) +".json?platform=ios",token=token)
#  debug(content)  
#  struktur = json.loads(content) 
#  sendung=struktur["broadcast"]  
#https://www.youtv.de/api/v2/archived_broadcasts.json?platform=ios		  archived_broadcast[id]:  299501
  values = {
         'archived_broadcast[id]' : id         
  }
  data = urllib.urlencode(values)
  content=getUrl("https://www.youtv.de/api/v2/archived_broadcasts.json?platform=ios",token=token,data=data)

def delit(id):
  token=login() 
  mytoken="Token token="+ token
  userAgent = "YOUTV/1.2.7 CFNetwork/758.2.8 Darwin/15.0.0"  
  query_url = "https://www.youtv.de/api/v2/archived_broadcasts/"+ str(id)+".json?platform=ios"
  headers = {
      'User-Agent': userAgent,
      'Authorization': mytoken
  }        
  debug(headers)  
  opener = urllib2.build_opener(urllib2.HTTPHandler)
  req = urllib2.Request(query_url, None, headers)
  req.get_method = lambda: 'DELETE' 
  url = urllib2.urlopen(req) 
  xbmc.executebuiltin("Container.Refresh")


  def serienadd(ids):
    token=login()   
    content=getUrl("https://www.youtv.de/api/v2/broadcasts/"+ str(ids) +".json?platform=ios",token=token)
    debug("content :"+content)
    struktur = json.loads(content)   
    serien=struktur["broadcast"]   
    serie=serien["series_id"]
    if serie==None:
       dialog = xbmcgui.Dialog()
       dialog.ok("Error", "Es ist keine Serie")    
    else:
       serienadd_direkt(serie)    
    
def serienadd_direkt(serie)    :    
      token=login()
      values = {
         'archived_series[id]' : serie
      } 
      data = urllib.urlencode(values)
      content=getUrl("https://www.youtv.de/api/v2/archived_series.json?platform=ios",token=token,data=data)

      
def seriendel(ids):
    token=login()                
    content=getUrl("https://www.youtv.de/api/v2/broadcasts/"+ str(ids) +".json?platform=ios",token=token)
    debug("content :"+content)
    struktur = json.loads(content)   
    serien=struktur["broadcast"]   
    serie=serien["series_id"]
    seriendel_direkt(serie)
    
def seriendel_direkt(serie):
    token=login()
    query_url = "https://www.youtv.de/api/v2/archived_series.json?id="+ str(serie)  +"&platform=ios"
    userAgent = "YOUTV/1.2.7 CFNetwork/758.2.8 Darwin/15.0.0"  
    mytoken="Token token="+ token
    headers = {
        'User-Agent': userAgent,
        'Authorization': mytoken
    }     
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    req = urllib2.Request(query_url, None, headers)
    req.get_method = lambda: 'DELETE' 
    url = urllib2.urlopen(req) 
    xbmc.executebuiltin("Container.Refresh")


if mode is '':
    addDir(translation(30103), translation(30001), 'TOP', "")
    addDir(translation(30104), translation(30005), 'Genres',"")
    addDir(translation(30105), translation(30006), 'Sender', "")   
    addDir(translation(30107), translation(30107), 'Search', "")  
    addDir(translation(30108), translation(30108), 'Archive',"")  
    addDir("Serien Aufnamen", "Serien Aufnamen", 'Series',"")  
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
          Genres()  
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
  if mode == 'Series':
          #date=2016-02-26&
          Series("https://www.youtv.de/api/v2/archived_series.json?platform=ios","archived_series")                                
  if mode == 'playvideo':  
          playvideo(url)  
  if mode == 'Search':  
          search(url)           
  if mode == 'addit':  
          addit(url)
  if mode == 'delit':  
          delit(url)          
  if mode == 'Subgeneres':  
          subgenres(ids)
  if mode == 'sadd':  
          seriendel(url)
  if mode == 'sdel':  
          serienadd(url)    
  if mode == 'sadddirekt':  
          serienadd_direkt(url) 
  if mode == 'sdeldirekt':              
          seriendel_direkt(url)
  if mode == 'download':              
          download(url)

          
