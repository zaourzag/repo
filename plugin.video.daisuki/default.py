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
import rsa
import pyaes
import base64
import ttml2srt



# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])

args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()

mainurl="http://www.daisuki.net/"
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

def holejson(url):  
  content=getUrl(url)
  if content=="":
    return empty
  else:
    struktur = json.loads(content) 
    return struktur

def addDir(name, url, mode, iconimage, desc=""): 
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  liz.setProperty("fanart_image", iconimage)
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',shortname="",zeit="",production_year="",abo=1,search=""):
  debug ("addLink abo " + str(abo))
  debug ("addLink abo " + str(shortname))
  cd=addon.getSetting("password")  
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
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
  
  
def getUrl(url,data="x"):
        https=addon.getSetting("https")
        if https=="true":
           url=url.replace("https","http")
        print("Get Url: " +url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"
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


 
  
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))


def listserien():
    main=getUrl(mainurl)
    country=re.compile('<meta property="og:url" content="http://www.daisuki.net/(.+?)/top.html"', re.DOTALL).findall(main)[0]
    print "Country : "+ country
    url="http://www.daisuki.net/bin/wcm/searchAnimeAPI?api=anime_list&searchOptions=&currentPath=/content/daisuki/"+country
    struktur=holejson(url)
    for name in struktur["response"]:
     title=name["title"]
     image="http://www.daisuki.net"+name["imageURL_s"]
     beschreibung=name["synopsis"]
     url="http://www.daisuki.net"+name["animeURL"]
     addDir(title,url, 'serie', image,desc=beschreibung) 
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      
def serie(url):
    debug("Url Serie :"+url)
    content=getUrl(url)
    kurz_inhalt = content[content.find('<!-- moviesBlock start -->')+1:]
    kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<!-- moviesBlock end  -->')]
    print kurz_inhalt
    spl=kurz_inhalt.split('<div id')
    for element in spl:
      try:
        nr=re.compile('/([0-9]+)/movie.jpg', re.DOTALL).findall(element)[0]
        image=re.compile('delay="(.+?)"', re.DOTALL).findall(element)[0]
        try:        
          folge=re.compile('false;">([^<]+)</a></p>', re.DOTALL).findall(element)[0]
        except:
          folge=re.compile('<p class="episodeNumber">([0-9]+?)</p>', re.DOTALL).findall(element)[0]        
        urln=url.replace(".html","."+str(nr)+".html").replace("detail.","watch.")
        addLink("Episode "+folge,urln, 'stream', "http://www.daisuki.net"+image) 
        debug("image :"+ image)
      except:
        pass
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      
      
def getstream(url):
 
  urljs="http://www.daisuki.net/etc/designs/daisuki/clientlibs_anime_watch.min.js"
  content=getUrl(urljs)
  match=re.compile('publickeypem="(.+?)"', re.DOTALL).findall(content)
  key=match[0]
  pubkey_pem = key.replace("\\n", "\n")
  params = {
            "cashPath":int(time.time()*1000)
  }
  content=getUrl(url)
  match=re.compile('var flashvars = {(.+?)}', re.DOTALL).findall(content)
  flash=match[0]
  api_params = {}
  s=re.compile('\'s\':"(.+?)"', re.DOTALL).findall(content)[0]
  initi=re.compile('\'init\':\'(.+?)\'', re.DOTALL).findall(content)[0]
  api_params["device_cd"]=re.compile('device_cd":"(.+?)"', re.DOTALL).findall(content)[0]
  api_params["ss1_prm"]=re.compile('ss1_prm":"(.+?)"', re.DOTALL).findall(content)[0]
  api_params["ss2_prm"]=re.compile('ss2_prm":"(.+?)"', re.DOTALL).findall(content)[0]
  api_params["ss4_prm"]=re.compile('ss3_prm":"(.+?)"', re.DOTALL).findall(content)[0]
  api_params["mv_id"]=re.compile('mv_id":"(.+?)"', re.DOTALL).findall(content)[0]

  aeskey = os.urandom(32)
  #aeskey = "This_key_for_demo_purposes_only!"
  pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(pubkey_pem)
  crypton = base64.b64encode(rsa.encrypt(aeskey, pubkey))

  encrypter = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(aeskey))
  ciphertext=""
  plaintext=json.dumps(api_params)
  for line in plaintext:
    ciphertext += encrypter.feed(line)

  # Make a final call to flush any remaining bytes and add paddin
  ciphertext += encrypter.feed()
  
  ciphertext = base64.b64encode(ciphertext)
  params = {
            "s": s,
            "c": api_params["ss4_prm"],
            "e": url,
            "d": ciphertext,
            "a": crypton
  }
  data = urllib.urlencode(params)
  res = getUrl("http://www.daisuki.net"+initi+"?"+data)
  struktur=json.loads(res) 
  rtn= struktur["rtn"]
  rtn=base64.b64decode(rtn)
  decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(aeskey))
  decrypted = decrypter.feed(rtn)
  #decrypted += decrypter.feed(rtn[len(ciphertext) / 2:])
  debug("Decrypt :"+decrypted)
  playurl=re.compile('"play_url":"(.+?)"', re.DOTALL).findall(decrypted)[0]  
  debug("Playurl :"+playurl)
  sub=re.compile('"caption_url":"(.+?)"', re.DOTALL).findall(decrypted)[0]  
  title=re.compile('"title_str":"(.+?)"', re.DOTALL).findall(decrypted)[0]    
  return playurl,sub,title

def stream(url):     
   urls,sub,title=getstream(url)
   debug ("Streamurl :"+url)
   debug ("Streamurlsub :"+sub)
   listitem = xbmcgui.ListItem(path=urls)
   listitem.setInfo('video', { 'title': title })
   subcontent=getUrl(sub)
   subcontent='<?xml version="1.0" encoding="UTF-8"?>\n'+subcontent
   sprachen=subcontent.split("<div xml:lang=")
   listsubs=[]
   for i in range(1,len(sprachen),1):
     element=sprachen[i]
     element=sprachen[0]+"<div xml:lang="+sprachen[i]
     lang=re.compile('lang="(.+?)"', re.DOTALL).findall(element)[0]      
     text_file = open(temp+lang+".xml", "w")
     text_file.write(element)
     text_file.close()      
     ttml2srt.ttml2srt(temp+lang+".xml", True,temp+lang+".srt")
     listsubs.append(temp+lang+".srt")
     print "-----------"
     print element   
     print "-----------"
   listitem.setSubtitles(listsubs)
   #text_file = open(temp+"daisuki.xml", "w")
   #text_file.write(subcontent)
   #text_file.close()
   #ttml2srt.ttml2srt(temp+"daisuki.xml", True,temp+"daisuki.srt")
   #listitem.setSubtitles([temp+"daisuki.srt"])
   xbmcplugin.setResolvedUrl(addon_handle,True, listitem) 
   
if mode is '':
    addDir("Liste Serien","Liste Serien", 'listserien', "")    
    addDir(translation(30108), translation(30108), 'Settings', "")        
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'listserien':
          listserien()                      
  if mode == 'serie':
          serie(url)      
  if mode == 'stream':
          stream(url)                