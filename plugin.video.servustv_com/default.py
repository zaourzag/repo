#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import httplib
import socket
import sys
import re
import os
import random
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import subprocess

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.servustv_com'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceView") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
defaultFanart = os.path.join(addonDir ,'fanart.png')
siteVersion = addon.getSetting("siteVersion")
siteVersion = ["de", "at"][int(siteVersion)]
quality = addon.getSetting("quality")
quality = [240, 480, 720][int(quality)]
qualityLive = addon.getSetting("qualityLive")
viewMode = str(addon.getSetting("viewID"))
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')]
urlMain = "http://www.servustv.com"
def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def index():
    addDir(translation(30001), urlMain+"/"+siteVersion, 'liste', defaultFanart)
    addDir(translation(30002), urlMain+"/"+siteVersion+"/Videos", 'listGenres', defaultFanart)
    addDir(translation(30008), urlMain+"/"+siteVersion+"/Themen", 'liste', defaultFanart)
    addDir(translation(30010), "", 'search', defaultFanart)
    addLink(translation(30011), "", 'playLiveStream', defaultFanart)
    addDir(translation(30107), translation(30107), 'Settings', "")     
    xbmcplugin.endOfDirectory(pluginhandle)
def liste(url):
    debug("listGenres url "+url)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(url).read()
    spl = content.split('<div class="mol teaser columns large-3 ">')
    for i in range(1, len(spl), 1):
      entry = spl[i]              
      #debug("---------")
      #debug(entry)
      #debug("---------")
      match = re.compile('<a href="(.+?)" >', re.DOTALL).findall(entry)
      url=match[0]
      match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
      img=match[0]
      match = re.compile('teaser-s">([^<]+)<', re.DOTALL).findall(entry)      
      title=match[0]
      debug("title : "+title)
      debug("url : "+url)
      debug("img : "+urlMain+img)
      addDir(cleanTitle(title), urlMain+url, 'listGenres', urlMain+img)
    
    xbmcplugin.endOfDirectory(pluginhandle)

def listGenres(url):
    debug("listGenres url "+url)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(url).read()
    debug("------------------")
    debug(content)
    titleall=[]
    match = re.compile('h1 class="ato headline[^<]+<a href="(.+?)" >([^<]+?)<', re.DOTALL).findall(content)
    found=0    
    for url2, title in match:        
        debug("URL : "+url)
        title = cleanTitle(title)
        if not title in titleall:
          titleall.append(title)
          if title:
            found=1
            addDir(cleanTitle(title), urlMain+url2, 'listGenres', defaultFanart)    
         
    match = re.compile('<div class="teaser-thema short">[^<]+<a href="(.+?)" >([^<]+?)<', re.DOTALL).findall(content)    
    for url3, title in match:        
        debug("THEMEN URL : "+url3)
        debug("THEMEN Thema : "+title)
        title = cleanTitle(title)
        if not title in titleall:
          titleall.append(title)
          if title:
            found=1
            addDir(cleanTitle(title), urlMain+url3, 'listGenres', defaultFanart)    
            
    match = re.compile('h2 class="ato headline[^<]+<a href="(.+?)" >([^<]+?)<', re.DOTALL).findall(content)         
    for url4, title in match:        
        debug("URL : "+url)
        title = cleanTitle(title)
        if not title in titleall:
          titleall.append(title)
          if title:
            found=1
            addDir(cleanTitle(title), urlMain+url4, 'listGenres', defaultFanart)            

    if found==0:
      listVideos(url)
    else:
      xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    xbmc.log("XXX listVideos url :"+ url)
    debug("listVideos url : "+url)
    content = opener.open(url).read()    
    content = content[content.find('<div class="Flow-block">'):]
    spl = content.split('<div class="mol teaser')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if 'class="ato btn playbutton"' in entry:
            match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
            url = urlMain+match[0]
            match = re.compile('class="ato headline.*?">(.+?)<', re.DOTALL).findall(entry)
            if match:
                title = match[0].strip()
                match = re.compile('class="ato text  teaser-sendungsdetail-subtitel">(.+?)<', re.DOTALL).findall(entry)
                if match:
                    title = title+" - "+match[0].strip()
                title = cleanTitle(title)
                match = re.compile('class="ato videoleange">(.+?)<', re.DOTALL).findall(entry)
                duration = ""
                if match:
                    duration = match[0]
                match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
                thumb = urlMain+match[0].replace("_stvd_teaser_small.jpg",".jpg").replace("_stvd_teaser_large.jpg",".jpg")
                debug("listVideos title : "+title)
                addLink(title, url, 'playVideo', thumb, "", duration)
    match = re.compile('class="next-site">.+?href="(.+?)"', re.DOTALL).findall(content)
    if match:        
        addDir(translation(30003), urlMain+cleanTitle(match[0]), 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url,name):
    content = opener.open(url).read()
    match = re.compile('data-videoid="(.+?)"', re.DOTALL).findall(content)
    content = opener.open("http://c.brightcove.com/services/mobile/streaming/index/master.m3u8?videoId="+match[0]).read()
    match = re.compile('RESOLUTION=(.+?)x(.+?)\n(.+?)\n', re.DOTALL).findall(content)
    for resX, resY, url in match:
        if int(resY)<=quality:
            finalURL=url
    
    listitem = xbmcgui.ListItem(path=finalURL)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def download (url,name):    
    xbmc.log("star download url"+ url)
    probe_args = [ffmpg, "-i", url, folder+name+".mp4" ]
    proc = runCommand(probe_args)
    temp_output = proc.communicate()[0]

def runCommand(args):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            proc = subprocess.Popen(args,startupinfo=startupinfo)
        except:
            xbmc.log("Couldn't run command")
            return False
        else:
            xbmc.log("Returning process", 5)
            return proc
    
def playLiveStream():
    if siteVersion=="de":    
                streamUrl=" http://hdiosstv-f.akamaihd.net/i/servustvhdde_1@75540/master.m3u8?b=0-1500"    
    else: 
                streamUrl="http://hdiosstv-f.akamaihd.net/i/servustvhd_1@51229/master.m3u8"
    content = opener.open(streamUrl).read()
    match = re.compile('RESOLUTION=(.+?)x([0-9]+?).+?\n(.+?)\n', re.DOTALL).findall(content)
    for resX, resY, url in match:
        debug("resX"+resX)
        if int(resY)<=quality:
            finalURL=url      
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def search():
    keyboard = xbmc.Keyboard('', translation(30002))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        listVideos(urlMain+"/"+siteVersion+"/search?stvd_form_search[name]="+search_string)


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
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+str(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    liz.setProperty('IsPlayable', 'true')
    if useThumbAsFanart and iconimage!=icon:
        liz.setProperty("fanart_image", iconimage)
    liz.addContextMenuItems([(translation(30007), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart and iconimage!=icon:
        liz.setProperty("fanart_image", defaultFanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listGenres':
    listGenres(url)
elif mode == 'Sendungen':
    Sendungen(url)
elif mode == 'playVideo':
    playVideo(url,name)
elif mode == 'playLiveStream':
    playLiveStream()
elif mode == 'queueVideo':    
    queueVideo(url, name, thumb)
elif mode == 'search':
    search()
elif mode == 'liste':
    liste(url)       
elif mode == 'Settings':
          addon.openSettings()
else:
    index()
