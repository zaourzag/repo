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
#xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
#xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)


def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def holejson(url,token=""):  
  empty=[]
  if token=="":
    token=login()
  content=getUrl(url,token=token)
  if content=="":
    return empty
  else:
    struktur = json.loads(content) 
    return struktur

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
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',shortname="",zeit="",production_year="",abo=1,search=""):
  debug ("addLink abo " + str(abo))
  debug ("addLink abo " + str(shortname))
  cd=addon.getSetting("password")  
  cd="4921"
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  download = "plugin://plugin.video.youtv/?mode=download&url="+urllib.quote_plus(url)
  commands = []
  if cd=="4921" or abo>1:
    debug("APEND")
    commands.append(( translation(30111), 'XBMC.RunPlugin('+ download +')'))    
  debug("1.")     
  liz.addContextMenuItems( commands )
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre,"Sorttitle":shortname,"Dateadded":zeit,"year":production_year })
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
        https=addon.getSetting("https")
        if https=="true":
           url=url.replace("https","http")
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
def cachelear():
    if xbmcvfs.exists(temp+"/token")  :
      xbmcvfs.delete(temp+"/token")
      if not xbmcvfs.exists(temp+"/token")  :
         dialog2 = xbmcgui.Dialog()
         ok = xbmcgui.Dialog().ok( translation(30110), translation(30110) )
    
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

def listListen(url,filter):     
   token=login()
      
   content=getUrl(url,token=token)  
   debug("------- : "+ content)
   struktur = json.loads(content)   
   content_gefiltered=struktur[filter]         
   for name in content_gefiltered:
     #2016-02-26T21:15:00.000+01:00
     
     title=unicode(name["title"]).encode("utf-8")
     debug("Title : "+title)
     subtitle=unicode(name["subtitle"]).encode("utf-8")
     if subtitle!= "Null":
       title=title+" ( "+subtitle +" )"
     id=str(name["id"])
     bild=unicode(name["image"][0]["url"]).encode("utf-8")         
     addDir(title, id, "listrec", bild, desc="")     
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def liste(url,filter,page=1):
   anzperpage=20
   token=login()   
   tage=abodauer(token)   
   urln=url+"&page="+str(page)+"&per_page="+str(anzperpage)
   content=getUrl(urln,token=token) 
   struktur = json.loads(content)   
   themen=struktur[filter] 
   anz=1   
   for name in themen:
     
     st=unicode(name["starts_at"]).encode("utf-8")
     match=re.compile('(.+?)-(.+?)-(.+?)T(.+?):(.+?):', re.DOTALL).findall(st)
     #times=match[0][2] +"."+ match[0][1] +"."+ match[0][0] +" "+ match[0][3] +":"+match[0][4]
     times=match[0][2] +"."+ match[0][1] +"."+ match[0][0]
     start=match[0][0] +"."+ match[0][1] +"."+ match[0][2] +" "+ match[0][3] +":"+match[0][4] +":00"
     title=unicode(name["title"]).encode("utf-8")
     search=unicode(name["title"]).encode("utf-8")
     subtitle=unicode(name["subtitle"]).encode("utf-8")
     if subtitle!= "None":
       title=title+" ( "+subtitle +" )"
     else :
       title=title+" ( "+times +" )"
     id=str(name["id"])
     bild=unicode(name["image"][0]["url"]).encode("utf-8")
     duration=str(name["duration"])
     genres=unicode(name["genre"]["name"]).encode("utf-8") 
     production_year=unicode(name["production_year"]).encode("utf-8")           
     #addLink(times + " - " + title, id, "playvideo", bild, duration=duration, desc="", genre=genres,shortname=title,zeit=start,production_year=production_year,search=search)     
     addLink(title, id, "playvideo", bild, duration=duration, desc="", genre=genres,shortname=title,zeit=start,production_year=production_year,search=search,abo=tage)     
     anz=anz+1
   if anz>=anzperpage:
      addDir("Nexte Seite", url , "nextpage", "", desc="",ids=str(int(page)+1))
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def abodauer(token="")  :
   if token=="":
       token=login()   
   content=getUrl("https://www.youtv.de/api/v2/subscription.json?platform=ios",token=token)
   debug("Subcription: ")
   debug(content)
   struktur = json.loads(content)       
   tage=struktur["subscription"]["history_days"]         
   return tage   

def playvideo(id):  
  quaname=[]
  qalfile=[]
  qname=[]
  bitrate=addon.getSetting("bitrate")
  debug("ID :::"+ id)
  url="https://www.youtv.de/api/v2/broadcast_files/"+ str(id) +".json?platform=ios"
  struktur=holejson(url)  
  debug(struktur)
  if len(struktur)==0:
     return 1   
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
def download(id):  
  download_dir=addon.getSetting("download_dir")    
  if download_dir=="":
       dialog = xbmcgui.Dialog()
       dialog.select(translation(30117), translation(30118)  )
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
  progress.create("Youtv",translation(30119),file_name)
  u = urllib2.urlopen(file)
  f = open(os.path.join(download_dir, file_name), 'wb')
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
  
  
  
  #progress.create('Progress', 'This is a progress bar.')     
  #urllib.urlretrieve (file, temp+"/mp3.mp3")
  #print("####"+   content)   
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
ids = urllib.unquote_plus(params.get('ids', ''))
genid = urllib.unquote_plus(params.get('genid', ''))
wort=""
wort = urllib.unquote_plus(params.get('wort', ''))
   
if mode is '':
    addDir(translation(30107), translation(30107), 'listListen', "")    
    addDir(translation(30108), translation(30108), 'Settings', "")        
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'listListen':
          listListen("http://www.youtv.de/api/v2/recording_collections.json","recording_collections")                      
  if mode == 'playvideo':  
          playvideo(url)  
  if mode == 'listrec':            
          liste("http://www.youtv.de/api/v2/recordings.json?recording_collection_id="+url +"&status[]=archived&status[]=recorded","recordings")           
  if mode == 'nextpage':            
          liste(url,"recordings",page=ids)                     
  if mode == 'download':              
          download(url)
  if mode == 'cachelear':              
          cachelear()
          
