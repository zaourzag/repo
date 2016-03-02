#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, os, urlparse
import xbmc ,xbmcgui, xbmcaddon,xbmcvfs
import urllib2,urllib, zlib,json
import re
import math
import socket, cookielib

addon = xbmcaddon.Addon()
__addonname__ = addon.getAddonInfo('name')
__addondir__    = xbmc.translatePath( addon.getAddonInfo('path') )
background = os.path.join(__addondir__,"bg.png")

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
  
# Einlesen von Parametern, Notwendig für Reset der Twitter API
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

# Soll Twitter Api Resetter Werden

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
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
      print("User :"+ user)
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
  
def download(id,token):  
  print("Start Download")
  download_dir=addon.getSetting("downloaddir")    
  if download_dir=="": 
       return 0
  quaname=[]
  qalfile=[]
  qname=[]
  bitrate=addon.getSetting("bitrate")
  print("ID :::"+ id)
  token=login()
  content=getUrl("https://www.youtv.de/api/v2/broadcast_files/"+ str(id) +".json?platform=ios",token=token)
  print("+X+ :"+ content)
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
     
  file_name = file.split('/')[-1]        
  urllib.urlretrieve (file, downloaddir + file_name)
  
if __name__ == '__main__':
   # Starte Service
   monitor = xbmc.Monitor()        
   # Solange der Service läuft
   while not monitor.abortRequested():                     
      downloaddir=addon.getSetting("downloaddir") 
      bitrate=addon.getSetting("bitrate")  
      delete=addon.getSetting("delete") 
      url="https://www.youtv.de/api/v2/archived_broadcasts.json?platform=ios"
      downloaddir=addon.getSetting("downloaddir") 
      if downloaddir!="":
         print("Main Download dir: "+ downloaddir)
         token=login()
         print("token: "+token)
         content=getUrl(url,token=token)
         print("XX :"+content)
         struktur = json.loads(content)   
         themen=struktur["archived_broadcasts"]   
         for name in themen:              
             title=unicode(name["title"]).encode("utf-8")
             print("File : "+ title)
             id=str(name["id"])     
             download(id,token)
             delit(id)
      if monitor.waitForAbort(86400):
         break      
