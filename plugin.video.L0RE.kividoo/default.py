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
import base64
import requests
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser
import requests
import xml.etree.ElementTree as ET
import YDStreamExtractor

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString


xbmcplugin.setContent(addon_handle, 'movies')

baseurl="https://bvbtotal.de/"
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)


icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')


profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)
cookie=os.path.join( temp, 'cookie.jar')
cj = cookielib.LWPCookieJar();


deviceid="A01_kodi0EI5ioJvOCffIzU%2BA%3D%3D"
deviceid_ucoded="A01_kodi0KEI5ioJvOCffIzU+A=="
htype="J_android_big"
name="samsung"
modell="GT-P5210"
login="https://srv01.kividoo.de/SRTL_ServiceInterface/v1/anonymSignon.ashx?"
androidversion="4.4.4"
build="eng..20170901.104702"
produkt=modell
idd="KTU84P"
hardware=modell
appversion="1.5.9.RL"
username=addon.getSetting("user")
password=addon.getSetting("pass")
tokenfile=os.path.join(temp,"token.txt")
header={'Content-Type':"text/xml",
'User-Agent':"Dalvik/1.6.0 (Linux; U; Android 4.4.4; GT-P5210 Build/KTU84P)",
}




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
    

  
def addDir(name, url, mode, thump, desc="",page=1,nosub=0):   
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&nosub="+str(nosub)
  ok = True
  liz = xbmcgui.ListItem(name)  
  liz.setArt({ 'fanart' : thump })
  liz.setArt({ 'thumb' : thump })
  liz.setArt({ 'banner' : icon })
  liz.setArt({ 'fanart' : icon })
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	
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



def geturl(url,data="x",header=""):
        debug(url)
        if not data=="x":
           r = requests.post(url, headers=header, data=data)
        else:
           r = requests.get(url, headers=header, data=data)
        return r.text

def get_anonsession():
        debug("start get_anonsession")
        string="d_id="+deviceid+"&d_type="+htype+"&m_type=xml&lang=de&swipe_type=receiver"
        data="<cmt_anonymSignOn><device_type_info><manufacturer>"+name+"</manufacturer><model>"+modell+"</model><release_version>"+androidversion+"</release_version><build_version>"+build+"</build_version><product>"+produkt+"</product><id>"+idd+"</id><device_HW>"+hardware+"</device_HW></device_type_info><app_version>"+appversion+"</app_version><login_info><d_id>"+deviceid_ucoded+"</d_id><d_type>"+htype+"</d_type></login_info></cmt_anonymSignOn>"
        content=geturl(login+string,data=data,header=header)
        session=re.compile('<s_id>(.+?)</s_id>', re.DOTALL).findall(content)[0]
        return session

def get_onetime():
        debug("Start Get Onetime")
        url="https://srv01.kividoo.de/SRTL_ServiceInterface/v4/login.ashx?m_type=xml&swipe_type=receiver"
        data="<cmt><device_type_info><manufacturer>"+name+"</manufacturer><model>"+modell+"</model><release_version>"+androidversion+"</release_version><build_version>"+build+"</build_version><product>"+produkt+"</product><id>"+idd+"</id><device_HW>"+hardware+"</device_HW></device_type_info><app_version>"+appversion+"</app_version><login_info><u_id>"+username+"</u_id><pw>"+password+"</pw><d_id>"+deviceid_ucoded+"</d_id><d_type>"+htype+"</d_type></login_info></cmt>"
        debug("DATA: "+data)
        content=geturl(url,data=data,header=header)
        debug(content)
        token=""
        session=""
        if not "<code>err_13</code>" in content:
            token=re.compile('<one-time-token>(.+?)</one-time-token>', re.DOTALL).findall(content)[0]
            session=re.compile('<s_id>(.+?)</s_id>', re.DOTALL).findall(content)[0]
            with open(tokenfile, 'w') as fp:
                fp.write(token)       
        else:
            dialog = xbmcgui.Dialog()
            dialog.notification("Login Fehler", 'Login hat nicht geklappt', xbmcgui.NOTIFICATION_ERROR)
        return token,session

def login_with_token(token):
        debug("start login_with_token")
        url="https://srv01.kividoo.de/SRTL_ServiceInterface/v4/login.ashx?m_type=xml&lang=de&swipe_type=receiver"
        data="<cmt><device_type_info><manufacturer>"+name+"</manufacturer><model>"+modell+"</model><release_version>"+androidversion+"</release_version><build_version>"+build+"</build_version><product>"+produkt+"</product><id>"+idd+"</id><device_HW>"+hardware+"</device_HW></device_type_info><app_version>"+appversion+"</app_version><login_info><u_id>"+username+"</u_id><one-time-token>"+token+"</one-time-token><d_id>"+deviceid_ucoded+"</d_id><d_type>"+htype+"</d_type></login_info></cmt>"
        content=geturl(url,data=data,header=header)
        session=re.compile('<s_id>(.+?)</s_id>', re.DOTALL).findall(content)[0]
        return session

def getobject_scid(session,idd):
        debug("getobject_scid")
        #https://srv01.kividoo.de/SRTL_ServiceInterface/v3/getAssetsSC.ashx?s_id=c67e6f6c-fb43-4c38-a385-53f3edbf293f&sc_id=710&al_ver=0
        url="https://srv01.kividoo.de/SRTL_ServiceInterface/v3/getAssetsSC.ashx?s_id="+session+"&sc_id="+str(idd)+"&al_ver=0"
        content=geturl(url,header=header)
        return content

def getobject_serie(session,idd):
        debug("getobject_serie")
        url="https://srv01.kividoo.de/SRTL_ServiceInterface/v4/getAssetDetails.ashx?s_id="+session+"&p_vers=ditto_1&a_id="+str(idd)+"&lang=de"
        content=geturl(url,header=header)
        return(content)
def getepisode(session,idd):
  debug("getepisode")
  url="https://srv01.kividoo.de/SRTL_ServiceInterface/v4/getToken.ashx?s_id="+session+"&ass_id="+idd+"&time_shift=false&auto-preview=false&lang=de"
  content=geturl(url,header=header)
  return(content)
  
def getdesc(session,idd):
  debug("getdesc")
  url="https://srv01.kividoo.de/SRTL_ServiceInterface/v4/getAssetDetails.ashx?s_id="+session+"&p_vers=ditto_1&a_id="+str(idd)+"&lang=de"
  data="<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><cmt><ps><p>synopsis</p><p>g1</p><p>DL_info</p><p>prods</p><p>playlists</p></ps></cmt>"
  content=geturl(url,header=header,data=data)
  return(content)

# Parameter  

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))

def login():
    debug("Start login")
    if not os.path.isfile(tokenfile) :
            debug("FETCH NEW TOKEN")
            token,session=get_onetime()
    else:
            debug("TOKEN READ")
            with open(tokenfile, 'r') as fp:
                token=fp.read()
    try:
        debug("GEt SESSION WITH TOKEN")
        session=login_with_token(token)
        debug(session)
    except:
        debug("NEW SESSION")
        token,session=get_onetime()        
    debug("TOKEN  :"+token)
    debug("SESSION:"+session)
    return token,session

        

def liste():
  addDir("Serien","710","listserien","")
  addDir("Filme","110","listmovies","")
  addDir("Hoerspiele","10041","listhoerspiele","")
  addDir("Settings","","Settings","")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
        
def listserien(idd):
   debug("lsitserien start")
   token,session=login()
   content=getobject_scid(session,int(idd)).encode("utf-8")
   debug(content)
   root = ET.fromstring(content)
   debug(":::::::::")
   for element in root.findall('.//show_cl'):  
      debug("----")   
      idd=element.get('id')
      name=element.find("name").text.encode("utf-8")
      url=element.find(".//url").text
      debug("idd :"+idd)
      debug("name :"+name)
      debug("url :"+url)
      addDir(name,idd,"serie",url)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)      
   
def listmovies(idd):
   debug("lsitserien start")
   token,session=login()
   content=getobject_scid(session,int(idd)).encode("utf-8")
   debug(content)
   root = ET.fromstring(content)
   debug(":::::::::")
   for element in root.findall('.//vod_cl'):  
      debug("----")   
      idd=element.get('id')
      name=element.find("name").text.encode("utf-8")
      url=element.find(".//url").text
      debug("idd :"+idd)
      debug("name :"+name)
      debug("url :"+url)
      addLink(name,idd,"playvideo",url)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     

def listhoerspiele(idd):
   debug("lsitserien start")
   token,session=login()
   content=getobject_scid(session,int(idd)).encode("utf-8")
   debug(content)
   root = ET.fromstring(content)
   debug(":::::::::")
   for element in root.findall('.//audiobook_cl'):  
      debug("----")   
      idd=element.get('id')
      name=element.find("name").text.encode("utf-8")
      url=element.find(".//url").text
      debug("idd :"+idd)
      debug("name :"+name)
      debug("url :"+url)
      addLink(name,idd,"playvideo",url)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     
   
def serie(idd):
    debug("Serie start")
    token,session=login()
    content=getobject_serie(session,idd).encode("utf-8")
    debug(content)
    root = ET.fromstring(content)
    debug(":::::::::")
    for element in root.findall('.//season_item'):  
       idd=element.get('id')
       name=element.find("short-name").text.encode("utf-8")
       addLink(name,idd,"playvideo","")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)             

def staffel(idd):
    debug("Staffel start")
    token,session=login()
    content=getobject_serie(session,idd).encode("utf-8")
    debug(content)
    root = ET.fromstring(content)
    debug(":::::::::")
    for element in root.findall('.//episode_item'):  
        idd=element.get('id')
        episode_nr=element.find("episode_num").text.encode("utf-8")
        name=element.find("name").text.encode("utf-8")
        url=element.find(".//url").text        
        addLink(episode_nr +" "+name,idd,"playvideo",url)
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)                     
def playvideo(idd):
    token,session=login()
    content=getdesc(session,idd)
    dd=re.compile('inst id="([^"]+?)"', re.DOTALL).findall(content)[0]
    content=getepisode(session,dd)   
    dd=re.compile('<pval>(.+?)</pval>', re.DOTALL).findall(content)[0]    
    listitem = xbmcgui.ListItem(path=dd)   
    addon_handle = int(sys.argv[1])  
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)


    
    
if mode is '':
     liste()   
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'listserien':
          listserien(url)
  if mode == 'serie':
          serie(url)
  if mode == 'staffel':
          staffel(url)  
  if mode == 'playvideo':
          playvideo(url)   
  if mode == 'listmovies':
          listmovies(url)     
  if mode == 'listhoerspiele':
          listhoerspiele(url)                        