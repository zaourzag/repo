#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import random
import xbmcplugin
import xbmcgui
import xbmcaddon
import json

addonID = 'plugin.video.fernsehkritik_tv'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceViewMode") == "true"
view_mode_id=int('503')
xbmcplugin.setContent(pluginhandle, 'Episodes')
translation = addon.getLocalizedString
urlMain = "http://fernsehkritik.tv"
downloadpath=addon.getSetting('download_path')
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
fanart=xbmc.translatePath('special://home/addons/'+addonID+'/fanart.jpg')
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')]


def main():
	addDir('Magazin','http://fernsehkritik.tv/tv-magazin/?p=1',"index",icon)
	if downloadpath is '':
		pass
	else:
		addDir('meine Downloads','','listing',icon)
	xbmcplugin.endOfDirectory(pluginhandle)
def folge(url,page="1"):    
    anzahl=100
    content = opener.open(url).read()
    PID = re.compile('MAG_PID = ([0-9]+?);', re.DOTALL).findall(content)[0]
    SID = re.compile('MAG_SPID = ([0-9]+?);', re.DOTALL).findall(content)[0]   
    print ("### "+url)
    print ("PID "+PID)
    print ("SID "+SID)
    nu="https://massengeschmack.tv/api/api_p.php?action=getFeed&from=["+str(PID)+"]&access_type=0&limit="+str(anzahl)+"&contentType=["+str(SID)+"]&page="+str(page)
    print("NU :"+nu)
    content = opener.open(nu).read()
    struktur = json.loads(str(content))
    x=1
    for element in struktur["eps"]:
      x=x+1
      uurl="https://massengeschmack.tv/play/"+element["identifier"]
      title=element["title"]
      icon=element["img"]
      print("###----")
      print(element["subscribed"])
      if element["subscribed"]==True:
        addLink(title,uurl,'playVideo',icon,'','')
    if x>=anzahl:
       addDir("Next",url,"folge","",page=int(page)+1)
    xbmcplugin.endOfDirectory(pluginhandle)
    
def index(url):
    content = opener.open(url).read()
    pag = re.compile('<li><a href="(.+?)">(.+?)</a></li>', re.DOTALL).findall(content)
    for url,name in pag:
       url="https://massengeschmack.tv"+url          
       addDir(name,url,"folge","",page=1)		
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)
	
def getVideourl(url):    
	content = opener.open(url).read()		
	if re.findall('<h4>Clip nicht kostenlos verfügbar.</h4>',content,re.S):
		print 'video nicht verfügbar'
		xbmc.executebuiltin('XBMC.Notification(Info:,Folge ist noch nicht verfügbar!,5000,'+icon+')')
	else:
		print 'weiter'
		match=re.findall('type: "video/mp4",.+?src: "([^"]+)"',content,re.S)
		if match:
			video_url=match[0]
			return video_url
			
 
def playVideo(url):
  print ("#########"+url)
  video_url=getVideourl(url)
  print ("###########"+video_url)
  listitem=xbmcgui.ListItem(path=video_url)
  xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	
def download(url):
	if downloadpath is '':
		d=xbmcgui.Dialog()
		d.ok('Download Error','Du hast keinen Download Folder gesetzt','','')
		addon.openSettings(sys.argv[ 0 ])
		return
	url=url+'play/'
	video_url=getVideourl(url)
	xbmc.executebuiltin('XBMC.Notification(Fernsehkritik,Starte Download)')
	urllib.urlretrieve(video_url, downloadpath+name+'.mp4')
	xbmc.executebuiltin("XBMC.Notification(Download beendet!,2000)")
	
def listing():
	dirs=os.listdir(downloadpath)
	for url in dirs:
		url=downloadpath+url
		name=(url).replace(downloadpath,'').replace('.mp4','')
		addLink(name,url,'play1',icon,'','')
	xbmcplugin.endOfDirectory(pluginhandle)
	
def play1(url):
	videolink=str(url)
	listitem=xbmcgui.ListItem(path=videolink)
	xbmcplugin.setResolvedUrl(pluginhandle, succeeded=True, listitem=listitem)
	


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    liz.setProperty('fanart_image', fanart)
    liz.setProperty('IsPlayable', 'true')
    menu = []
    menu.append(('Download Video', 'XBMC.RunPlugin(%s?mode=59&name=%s&url=%s)' % (sys.argv[0], name, url)))
    liz.addContextMenuItems(items=menu, replaceItems=False)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def addDir(name,url,mode,iconimage,page=1):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&page="+str(page)
    ok=True
    item=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    item.setInfo( type="Video", infoLabels={ "Title": name } )
    item.setProperty('fanart_image', fanart)
    xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=True)

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
page = urllib.unquote_plus(params.get('page', ''))

if mode == 'index':
	index(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
elif mode =='listing':
	listing()
elif mode =='play1':
	play1(url)
elif mode =='folge':
	folge(url,page)  
elif mode =='59':
    download(url)
else:
    main()


