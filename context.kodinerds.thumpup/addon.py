#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon
import xbmcgui,xbmcvfs
import json,urllib2,re,urlparse,os
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from datetime import datetime    
import urllib
import requests,cookielib
from cookielib import LWPCookieJar
cj = cookielib.CookieJar()
addon = xbmcaddon.Addon()

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
session = requests.session()

if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       

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
  
  
def geturl(url,data="x",header=[]):
   global cj
   content=""
   debug("URL :::::: "+url)
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   userAgent = "Coralie/1.7.2-2016081207(SM-G900F; Android; 6.0.1"
   header.append(('User-Agent', userAgent))
   header.append(('Accept', "*/*"))
   header.append(('Content-Type', "application/json;charset=UTF-8"))
   header.append(('Accept-Encoding', "plain"))   
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



def gettitle()  :
  title=""
  title=xbmc.getInfoLabel('ListItem.TVShowTitle')
  try:    
    info = sys.listitem.getVideoInfoTag() 
    title=info.getTVShowTitle()
  except:
    pass
  try:
      title=xbmc.getInfoLabel('ListItem.TVShowTitle')
  except:
       pass
  if title=="":
     title = xbmc.getInfoLabel("ListItem.Title").decode('UTF-8')      
  if title=="":
     title=sys.listitem.getLabel()
  debug("TITLE :::: "+title)     
  return title



addon = xbmcaddon.Addon()    
debug("Hole Parameter")
debug("Argv")
debug(sys.argv)
debug("----")
try:
      params = parameters_string_to_dict(sys.argv[2])
      debug("Parameter Holen geklappt")
except:
      debug("Parameter Holen nicht geklappt")
      mode="" 
debug("Mode ist : "+mode)
if mode=="":  
    username=addon.getSetting("username")
    password=addon.getSetting("password")
    title=gettitle()
    content=geturl("https://www.kodinerds.net/")
    newurl=re.compile('method="post" action="(.+?)"', re.DOTALL).findall(content)[0]
    sec_token=re.compile("SECURITY_TOKEN = '(.+?)'", re.DOTALL).findall(content)[0]
    content=geturl("https://www.kodinerds.net/index.php/Login/",data="username="+username+"&action=login&password="+password+"&useCookies=1&submitButton=Anmelden&url="+newurl+"&t="+sec_token)
    content=geturl("https://www.kodinerds.net/index.php/Thread/58034-L0RE-s-Test-thread/")
    debug(content)
    debug("---")
    sec_token=re.compile("SECURITY_TOKEN = '(.+?)'", re.DOTALL).findall(content)[0]
    hash=re.compile('name="tmpHash" value="(.+?)"', re.DOTALL).findall(content)[0]
    timestamp=re.compile('data-timestamp="(.+?)"', re.DOTALL).findall(content)[0]   
    values = {
      'actionName' : 'quickReply',
      'className' : 'wbb\data\post\PostAction',
      'interfaceName': 'wcf\data\IMessageQuickReplyAction',
      'parameters[objectID]': '58034',
      'parameters[data][message]' : "Aus Kodi Empfolen :"+ title,
      'parameters[data][tmpHash]' : hash,
      'parameters[lastPostTime]':timestamp,
      'parameters[pageNo]':'1'
    }
    data = urllib.urlencode(values)
    content=geturl("https://www.kodinerds.net/index.php/AJAXProxy/?t="+sec_token,data=data)
    debug(content)
    
    

    
