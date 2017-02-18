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
from StringIO import StringIO
import xml.etree.ElementTree as ET
import time
from datetime import datetime
try:
    import urllib.parse as compat_urllib_parse
except ImportError:  # Python 2
    import urllib as compat_urllib_parse

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString

# Es geht um Videos
xbmcplugin.setContent(addon_handle, 'movies')

baseurl="http://www.7tv.de"
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')


profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")



cookie=temp+"/cookie.jar"
cj = cookielib.LWPCookieJar();

if xbmcvfs.exists(cookie):
    cj.load(cookie,ignore_discard=True, ignore_expires=True)


#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       

favdatei   = xbmc.translatePath( os.path.join(temp,"favorit.txt") ).decode("utf-8")


def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
def addDir(name, url, mode, iconimage, desc="",sendername="",offset="",limit="",type="",bild="",title=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&sendername="+str(sendername)+"&offset="+str(offset)+"&limit="+str(limit)+"&type="+str(type)+"&iconimage="+bild+"&title="+title
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  iconimage = ""
  liz.setProperty("fanart_image", iconimage)	
  liz.setProperty("fanart_image", "")
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok


 
def geturl(url,data="x",header=""):
        global cj
        print("Get Url: " +url)
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
             #print e.code   
             cc=e.read()  
             debug("Error : " +cc)
       
        opener.close()
        return content

   
def addLink(name, url, mode, iconimage, duration="", desc="", genre=''):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage="", thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
	liz.setProperty('IsPlayable', 'true')
	liz.addStreamInfo('video', { 'duration' : duration })
	liz.setProperty("fanart_image", iconimage)
	#liz.setProperty("fanart_image", "")
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
 
       
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
sendername = urllib.unquote_plus(params.get('sendername', ''))
offset = urllib.unquote_plus(params.get('offset', ''))
limit = urllib.unquote_plus(params.get('limit', ''))
type = urllib.unquote_plus(params.get('type', ''))
title = urllib.unquote_plus(params.get('title', ''))
bild = urllib.unquote_plus(params.get('iconimage', ''))



def senderlist():
    inhalt = geturl(baseurl) 
    image_url=re.compile('<link rel="stylesheet" type="text/css" href="(.+?)">', re.DOTALL).findall(inhalt)
    
    kurz_inhalt = inhalt[inhalt.find('<ul class="site-nav-submenu">')+1:]
    kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</nav>')]  
    match=re.compile('<a href="([^"]+)" [^>]+>([^<]+)</a>', re.DOTALL).findall(kurz_inhalt)
    for id,name in match:
      newurl=baseurl+id      
      debug("#### : "+newurl)
      addDir(name, newurl, "sender", "")      
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def sender(url):
    addDir("Beliebteste Sendungen", url, "belibtesendungen", "")      
    addDir("Neue Ganze Folgen", url, "ganzefolgensender", "")           
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
def belibtesendungen(url):
  inhalt = geturl(url) 
  kurz_inhalt = inhalt[inhalt.find('<h3 class="row-headline">Beliebte Sendungen</h3>')+1:]
  kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<div class="row ">')]  
  spl=kurz_inhalt.split('<article class')
  for i in range(1,len(spl),1):
    try:
      entry=spl[i]
      debug(" ##### ENTRY ####")
      debug(entry)
      urlt=re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
      img=re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0]
      title=re.compile('teaser-formatname">(.+?)<', re.DOTALL).findall(entry)[0]
      urlv=baseurl+urlt
      debug("belibtesendungen addurl :"+urlv)
      addDir(title, urlv, "serie", img,bild=img,title=title)      
    except:
      pass
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def ganzefolgensender(url):
  inhalt = geturl(url) 
  kurz_inhalt = inhalt[inhalt.find('</h3>')+1:]
  kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<h3 class="row-headline">Ihre Favoriten</h3>')]  
  spl=kurz_inhalt.split('<article class')
  for i in range(1,len(spl),1):
    try:
      entry=spl[i]
      if "class-clip" in entry:
        debug(" ##### ENTRY ####")
        debug(entry)
        urlt=re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
        img=re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0]
        serie=re.compile('<h4 class="teaser-formatname">(.+?)</h4>', re.DOTALL).findall(entry)[0]
        folge=re.compile('<h5 class="teaser-title">(.+?)</h5>', re.DOTALL).findall(entry)[0]
        title=serie + " - " + folge
        urlv=baseurl+urlt
        debug("belibtesendungen addurl :"+urlv)
        addLink(title, urlv, "getvideoid", img)      
    except:
      pass
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def favadd(url,title,bild):
  debug(" favadd url :"+url)
  textfile=url+"###"+title+"###"+bild+"\n"
  try:
    f=open(favdatei,'r')
    for line in f:
      textfile=textfile+line
    f.close()
  except:
    pass
  f=open(favdatei,'w')
  f.write(textfile)
  f.close()
  xbmc.executebuiltin('Notification("Hinzufufügen",title+" hinzugefügt")')
  xbmc.executebuiltin("Container.Refresh")
    

def favdel(url):
  debug(" FAVDEL url :"+url)
  textfile=""
  f=open(favdatei,'r')
  for line in f:
     if not url in line and not line=="\n":
      textfile=textfile+line
  f.close()
  f=open(favdatei,'w')
  f.write(textfile)
  f.close()
  xbmc.executebuiltin('Notification("Löschen","Serie wurde gelöscht")')
  xbmc.executebuiltin("Container.Refresh")  

def listfav()  :
    if xbmcvfs.exists(favdatei):
        f=open(favdatei,'r')
        for line in f:
          spl=line.split('###')       
          addDir(name=spl[1], url=spl[0], mode="serie", iconimage=spl[2].strip(), desc="",title=spl[1],bild=spl[2].strip())
        f.close()
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
  
def  serie(url,bild="",title=""):
    debug("serie :"+url)
    debug("title :"+title)
    addDir("Alle Clips", url+"/alle-clips", "listvideos", "")      
    addDir("Ganze Folgen", url+"/ganze-folgen", "listvideos", "")
    found=0
    if xbmcvfs.exists(favdatei):
      f=open(favdatei,'r')     
      for line in f:
           if url in line:
              found=1
    if found==0:           
             addDir("Adde Favorites", url, mode="favadd", iconimage="", desc="",title=title,bild=bild)      
    else :
             addDir("Delete Favorites", url, mode="favdel", iconimage="", desc="")         
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def sendungsmenu():
    addDir("Sender", "sixx", "allsender", "")      
    addDir("Generes", "Anime", "allsender", "")   
    addDir("Alle Sendungen", baseurl+"/queue/format", "abisz", "")   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
def abisz(url):
  url=url.replace(" ","+")
  debug("abisz URL :"+url)
  inhalt = geturl(url) 
  struktur = json.loads(inhalt) 
  debug("struktur --------")
  debug(struktur)
  for buchstabe in sorted(struktur["facet"], key=lambda str: (str=="#", str)):
     if   buchstabe=="#" :  
        ubuchstabe="0-9"
     else:
         ubuchstabe=buchstabe
     addDir(buchstabe.title(), url+"/(letter)/"+ubuchstabe, "jsonfile", "")  
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def jsonfile(url):
   debug("jsonfile url :"+url)
   inhalt = geturl(url) 
   struktur = json.loads(inhalt) 
   for element in struktur["entries"]:
     urlv=element["url"]
     image=element["images"][0]["url"]
     title=element["title"]
     addDir(title, baseurl+"/"+urlv, "serie", image,bild=image,title=title)       
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
def allsender(begriff):
  debug("allsender url :"+begriff)
  url="http://www.7tv.de/sendungen-a-z"    
  inhalt = geturl(url) 
  inhalt = inhalt[:inhalt.find('<div class="tvshow-list" data-type="bentobox">')] 
  debug("####### "+inhalt)
  spl=inhalt.split('<ul class="tvshow-filter">')
  for i in range(1,len(spl),1):   
      entry=spl[i]
      debug("Entry :"+ entry)
      if not begriff in entry:
         debug("Nicht gefunden")
         continue
      filter=re.compile('<a href="#tvshow-all" data-href="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
      for url,name in filter:
         url=baseurl+url
         addDir(name, url, "abisz", "")      
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
  
def listvideos(url):
  inhalt = geturl(url) 
  kurz_inhalt = inhalt[inhalt.find('<div class="main-zone">')+1:]
  kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<!--googleoff: index-->')]  
  spl=kurz_inhalt.split('<article class')
  for i in range(1,len(spl),1):
    try:
      entry=spl[i]
      debug(" ##### ENTRY ####")
      debug(entry)
      urlv=re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
      img=re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0]
      title=re.compile('teaser-title">(.+?)</h5>', re.DOTALL).findall(entry)[0]
      urlv=baseurl+urlv
      try:
        match=re.compile('<p class="teaser-info">([0-9]+):([0-9]+) Min.</p>', re.DOTALL).findall(entry)
        zeit=int(match[0][0])*60+ int(match[0][1])
      except:
        zeit=0
        pass
      addLink(title, urlv, "getvideoid", img,duration=zeit)      
    except:
      pass
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

def getvideoid(client_location):
  debug("getvideoid client_location :"+client_location)
  inhalt = geturl(client_location)
  video_id=re.compile('"clip_id": "(.+?)"', re.DOTALL).findall(inhalt)[0]  

  source_id = None
  videos = playvideo(video_id, client_location,  source_id)

  
  

def playvideo(video_id,  client_location, source_id=None):
        from hashlib import sha1

        adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.adaptive", "properties": ["enabled"]}}')        
        struktur = json.loads(adaptivaddon) 
        debug("adaptivaddon struktur :")
        debug(struktur)
        is_type=""
        if not "error" in struktur.keys() :            
            if struktur["result"]["addon"]["enabled"]==True:
                is_type="inputstream.adaptive"
        if is_type=="":
          adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.mpd", "properties": ["enabled"]}}')        
          struktur = json.loads(adaptivaddon)           
          if not "error" in struktur.keys() :            
            if struktur["result"]["addon"]["enabled"]==True:
                is_type="inputstream.mpd"                
        if is_type=="":
            access_token = 'h''b''b''t''v'  
            salt = '0''1''r''e''e''6''e''L''e''i''w''i''u''m''i''e''7''i''e''V''8''p''a''h''g''e''i''T''u''i''3''B'
            client_name='h''b''b''t''v'
        else:
          access_token = 'seventv-web'  
          salt = '01!8d8F_)r9]4s[qeuXfP%'
          client_name=''
#          dialog = xbmcgui.Dialog()
          #nr=dialog.ok("Inputstream", "Inputstream fehlt")
          #return ""
        print "is_type :"+is_type
        if source_id is None:
            source_id=0 
            json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s?' \
                       'access_token=%s&client_location=%s&client_name=%s' \
                       % (video_id, access_token, client_location, client_name)
            json_data = geturl(json_url)
            json_data = json.loads(json_data) 
            print json_data
            print "........................"
            if not is_type=="":
              for stream in json_data['sources']:
                if  stream['mimetype']=='application/dash+xml': 
                  if int(source_id) <  int(stream['id']):               
                    source_id = stream['id']
              print source_id
            else:
              #debug("Protected : "+json_data["is_protected"])
              if json_data["is_protected"]==True:
                xbmc.executebuiltin('Notification("Inputstream", "DRM geschützte Folgen gehen nur mit Inputstream")')
                return
              else:
                for stream in json_data['sources']:
                  if  stream['mimetype']=='video/mp4':           
                    if int(source_id) <  int(stream['id']):                                   
                        source_id = stream['id']
                print source_id
        client_id_1 = salt[:2] + sha1(
            ''.join([str(video_id), salt, access_token, client_location, salt, client_name]).encode(
                'utf-8')).hexdigest()
           
        json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources?' \
                   'access_token=%s&client_location=%s&client_name=%s&client_id=%s' \
                   % (video_id, access_token, client_location, client_name, client_id_1)            
        json_data = geturl(json_url)
        json_data = json.loads(json_data) 
        print json_data
        print "........................"
        server_id = json_data['server_id']
        
        #client_name = 'kolibri-1.2.5'    
        client_id = salt[:2] + sha1(''.join([salt, video_id, access_token, server_id,client_location, str(source_id), salt, client_name]).encode('utf-8')).hexdigest()
        url_api_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources/url?%s' % (video_id, compat_urllib_parse.urlencode({
            'access_token': access_token,
            'client_id': client_id,
            'client_location': client_location,
            'client_name': client_name,
            'server_id': server_id,
            'source_ids': str(source_id),
        }))
        print "url_api_url :"+url_api_url
        json_data = geturl(url_api_url)
        json_data = json.loads(json_data) 
        debug ("---------------------------")
        debug( json_data)
        debug( "........................")
        max_id=0
        for stream in json_data["sources"]:
            ul=stream["url"]
            try:
                sid=re.compile('-tp([0-9]+).mp4', re.DOTALL).findall(ul)[0]
                id=int(sid)
                if max_id<id:
                    max_id=id
                    data=ul
            except:
              data=ul                                 
        #data=json_data["sources"][-1]["url"]               
        userAgent = 'user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
        addon_handle = int(sys.argv[1])
        listitem = xbmcgui.ListItem(path=data+"|"+userAgent)         
        #listitem.setProperty('inputstream.mpd.license_type', 'com.widevine.alpha')
        #listitem.setProperty('inputstream.mpd.license_type', 'com.widevine.alpha')
        listitem.setProperty(is_type+".license_type", "com.widevine.alpha")
        listitem.setProperty(is_type+".manifest_type", "mpd")
        listitem.setProperty('inputstreamaddon', is_type)
        try:
          lic=json_data["drm"]["licenseAcquisitionUrl"]        
          token=json_data["drm"]["token"]                
          listitem.setProperty(is_type+'.license_key', lic +"?token="+token+"|"+userAgent+"|R{SSM}|")            
        except:
           pass
        #listitem.setProperty('inputstreamaddon', 'inputstream.mpd')        
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
  
        #print "Daten lic :"+lic
        #print "Daten token :"+token
        #print "Daten data :"+data        
        return ""

def verpasstdatum():
  #http://www.7tv.de/missedshows/data/20161215
   dialog = xbmcgui.Dialog()
   d = dialog.input(translation(30009), type=xbmcgui.INPUT_DATE)
   d=d.replace(' ','0')  
   d= d[6:] +  d[3:5] + d[:2]
   xbmc.executebuiltin('ActivateWindow("Videos","plugin://plugin.video.7tvneu?url='+d+'&mode=verpasstdatummenu")') 

def verpasstdatummenu(d):
   url=baseurl+"/missedshows/data/"+d
   json_data = geturl(url)
   json_data = json.loads(json_data) 
   for sendername in json_data["entries"].keys():
     debug("sender "+sendername)
     addDir(sendername, url, "listdatum", "",sendername=sendername)  
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
     
def  listdatum(url,sendername):
   debug("listdatum ulr :"+url)
   debug("listdatum sender :"+ sendername)
   json_data = geturl(url)
   json_data = json.loads(json_data) 
   senderliste=json_data["entries"][sendername]
   for element in senderliste:
     title=element["title"]
     urlv=baseurl+element["url"]     
     dur=int(element["duration"]) /1000     
     serie=element["metadata"]["tvShowTitle"]
     time=element["airtime"]
     name=time + " " + serie + " - " + title
     
     addLink(name, urlv, "getvideoid", "") 
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   debug("senderliste")
   debug(senderliste)

def search():
   dialog = xbmcgui.Dialog()
   d = dialog.input(translation(30010), type=xbmcgui.INPUT_ALPHANUM)
   d=d.replace(" ","+")
   debug("XYXXX :::")   
   #xbmc.executebuiltin('Notification("Inputstream", "DRM geschützte Folgen gehen nur mit Inputstream")')
   xbmc.executebuiltin('ActivateWindow("Videos","plugin://plugin.video.7tvneu?url='+d+'&mode=searchmenu")') 
   debug("WWWW :::")
   
def searchmenu(d):
   #/type/episode/offset/1/limit/5
   d=d.replace(" ","+")
   addDir("Serien", url=baseurl +"/7tvsearch/search/query/"+ d , mode="searchtext", iconimage="" ,offset=0,limit=5,type="format")           
   addDir("Ganze Folgen", url=baseurl +"/7tvsearch/search/query/"+ d , mode="searchtext", iconimage="" ,offset=0,limit=5,type="episode")   
   addDir("Clips", url=baseurl +"/7tvsearch/search/query/"+ d , mode="searchtext", iconimage="" ,offset=0,limit=5,type="clip")   
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)         
  

def searchtext(url,offset,limit,type): 
   debug("Type :"+type) 
   urlx=url+"/type/"+ type + "/offset/"+offset +"/limit/"+limit
   debug("Searchtext ---------")
   debug(urlx)
   content = geturl(urlx)
   spl=content.split('<article class')
   for i in range(1,len(spl),1):
      entry=spl[i]  
      urlt=re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
      urlt=baseurl+urlt
      img=re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0]
      title=re.compile('title="(.+?)"', re.DOTALL).findall(entry)[0]      
      if  type=="format":
        addDir(title, urlt, "serie", img,bild=img,title=title) 
      else:
        addLink(title, urlt, "getvideoid", img) 
   if i>5:
     addDir("Next", url, mode="searchtext", iconimage="" ,offset=str(int(offset)+7),limit=limit,type=type)   
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
# Haupt Menu Anzeigen      
if mode is '':
    addDir("Sender", "Sender", 'senderlist', "") 
    addDir("Sendungen A-Z", url+"/ganze-folgen", "sendungsmenu", "")  
    addDir("Sendungen nach Datum", "", "verpasstdatum", "")  
    addDir("Suche","","search","")
    addDir("Favoriten", "Favoriten", 'listfav', "") 
    addDir("Einstellungen", "", 'Settings', "")   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'senderlist':
          senderlist()
  if mode == 'sender':
          sender(url)
  if mode == 'belibtesendungen':
          belibtesendungen(url)
  if mode == 'serie':
          serie(url,bild,title)       
  if mode == 'listvideos':
          listvideos(url)       
  if mode == 'getvideoid':
          getvideoid(url)     
  if mode == 'ganzefolgensender':
          ganzefolgensender(url)                      
  if mode == 'sendungsmenu':
          sendungsmenu()                  
  if mode == 'allsender':
          allsender(url)                          
  if mode == 'abisz':
          abisz(url)                                             
  if mode == 'jsonfile':
          jsonfile(url)                                                               
  if mode == 'verpasstdatum':
          verpasstdatum()   
  if mode == 'listdatum':
          listdatum(url,sendername) 
  if mode == 'search':
          search()
  if mode ==  'searchtext':
          searchtext(url,offset,limit,type)
  if mode ==  'searchmenu':
          searchmenu(url)
  if mode ==  'verpasstdatummenu':
          verpasstdatummenu(url)          
  if mode == 'favadd':          
          favadd(url,title,bild)          
  if mode == 'favdel':          
          favdel(url)                             
  if mode == 'listfav':          
          listfav()     