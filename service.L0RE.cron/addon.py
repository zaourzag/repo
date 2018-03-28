#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os
import xbmc,xbmcaddon,xbmcgui,xbmcvfs,xbmcplugin
from datetime import datetime
import urlparse,urllib
import sqlite3,traceback

global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
translation = addon.getLocalizedString
addon = xbmcaddon.Addon()

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')

thread="https://www.kodinerds.net/index.php/Thread/11148-Was-ist-eure-Lieblingsserie-Serientalk-Empfehlungen/"
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

def adddata():
    reg,msg=post.postdb()
    if reg=="1":
       dialog = xbmcgui.Dialog()
       nr=dialog.ok("Fehler", msg)
    else:
       dialog = xbmcgui.Dialog()
       nr=dialog.ok("OK", msg)
       
def addDir(name, url, mode, thump, desc="",seite=1,anz=0,serienname=0,stattfolgen=0,play=0):   
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&seite="+str(seite)+"&anz="+str(anz)+"&serienname="+str(serienname)+"&stattfolgen="+str(stattfolgen)
  ok = True
  liz = xbmcgui.ListItem(name)  
  liz.setArt({ 'fanart' : thump })
  liz.setArt({ 'thumb' : thump })
  liz.setArt({ 'banner' : icon })
  liz.setArt({ 'fanart' : icon })
  if play==1: 
    liz.setProperty('IsPlayable', 'true')
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
params = parameters_string_to_dict(sys.argv[2])
debug("--->")
debug(params)
debug(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name= urllib.unquote_plus(params.get('name', ''))
stunden= urllib.unquote_plus(params.get('stunden', ''))

def createtable():
    conn = sqlite3.connect(temp+'/cron.db')
    c = conn.cursor()
    try:
            c.execute('CREATE TABLE cron (stunden INTEGER ,url text PRIMARY KEY,name text,last datetime)')
    except :
              var = traceback.format_exc()
              debug(var)
    conn.commit()
    c.close()
def insert(name,url,stunden,last):
    conn = sqlite3.connect(temp+'/cron.db')
    c = conn.cursor()    
    try:
        c.execute('insert into cron (name,url,stunden,last) values ("%s","%s",%d,%s)'%(name,url,stunden,last))
    except:
        var = traceback.format_exc()
        debug(var)
    conn.commit()
    c.close()
def delete(url):
    conn = sqlite3.connect(temp+'/cron.db')
    c = conn.cursor()    
    try:
        c.execute('delete from cron where url="%s"'%(url))
    except:
        var = traceback.format_exc()
        debug(var)
    conn.commit()
def liste(surl):
    namelist=[]
    urllist=[]
    conn = sqlite3.connect(temp+'/cron.db')
    c = conn.cursor()    
    try:
        if url=="":
            search='select name,url from cron where url like "%"'
        else:
            search='select name,url from cron where url like "%'+surl+'%"'
        
        debug(search)
        debug("#+#+#+#+")
        c.execute(search)        
        r = list(c)
        for member in r:
           addDir("Loesche: "+member[0],member[1],"delete","")
    except:
        var = traceback.format_exc()
        debug(var)
    conn.commit()
    c.close()  
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

if mode == '':
   liste("")
if mode == 'delete':
   delete(url)
if mode == 'liste':
   liste(url)
if mode == 'adddata':
      debug("URL :"+url)
      createtable()
      debug("instert")
      insert(name,url,int(stunden),"datetime()")
      debug("AFTER INSTERT")
      debug(url)
      xbmc.executebuiltin('XBMC.RunPlugin('+url+')')
