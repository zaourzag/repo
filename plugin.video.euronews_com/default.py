#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import os
import re
import xbmcplugin
import xbmcaddon
import xbmcgui,json
from HTMLParser import HTMLParser


addon = xbmcaddon.Addon()
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
translation = addon.getLocalizedString
xbox = xbmc.getCondVisibility("System.Platform.xbox")

while (not os.path.exists(xbmc.translatePath("special://profile/addon_data/"+addonID+"/settings.xml"))):
    addon.openSettings()

forceViewMode = addon.getSetting("forceViewMode") == "true"
viewMode = str(addon.getSetting("viewMode"))
language = addon.getSetting("language")
languages = ["en", "gr", "fr", "de", "it", "es", "pt", "pl", "ru", "ua", "tr", "ar", "pe"]
language = languages[int(language)]
language2 = language.replace("en", "www").replace("pe", "persian").replace("ar", "arabic")

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    

def index():
    if language!="pl":
        addLink(translation(30001), "", 'playLive', "")
    addDir(translation(30002), "", 'newsMain', "")
    content = getUrl("http://"+language2+".euronews.com")
    match = re.compile('<li class="menu-element-programs"><a title="(.+?)" href="(.+?)">', re.DOTALL).findall(content)
    if match:
        addDir(match[0][0], "http://"+language2+".euronews.com"+match[0][1], 'listShows', "")
    content = content[content.find('<ol id="categoryNav">'):]
    content = content[:content.find('</ol>')]
    spl = content.split('<a')
    for i in range(2, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = "http://"+language2+".euronews.com"+match[0]
        match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        if "/nocomment/" in url:
            addDir(title, url, 'listNoComment', "")
        elif "/travel/" not in url and "/in-vogue/" not in url:
            addDir(title, url, 'listVideos', "")
    addDir(translation(30004), "", 'search', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def newsMain():
    addDir(translation(30003), "http://"+language2+".euronews.com/news/", 'listVideos', "")
    content = getUrl("http://"+language2+".euronews.com")
    content = content[content.find('<ol class="lhsMenu">'):]
    content = content[:content.find('</ol>')]
    spl = content.split('<a')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = "http://"+language2+".euronews.com"+match[0]
        match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        addDir(title, url, 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideos(url):
    content = getUrl(url)
    contenttop = content[content.find('<div class="topStoryWrapper clear">'):]
    contenttop = contenttop[:contenttop.find('<div class="subcategoryList clear">')]
    titletop = contenttop[contenttop.find('<h2 class="topStoryTitle">'):]
    match = re.compile('<a href="(.+?)" title="(.+?)"', re.DOTALL).findall(titletop)
    url="http://"+language2+".euronews.com"+match[0][0]
    title=match[0][1]
    title=HTMLParser().unescape(title.decode('utf-8'))
    title=title.encode('utf-8')
    match = re.compile('src="(.+?)"', re.DOTALL).findall(titletop)
    thumb =  match[0]
    match = re.compile('<p>(.+?)</p>', re.DOTALL).findall(titletop)
    desc=match[0]
    addLink(title, url, 'playVideo', thumb, desc)
    spl = content.split('<span class="artDate">')
    for i in range(1, len(spl), 1):      
        element=spl[i]
        sp2 = element.split('<a title="INSIDERS"')
        for i2 in range(0, len(sp2), 1):
            element=sp2[i2]
            debug("---------")
            debug(element)
            debug("---------")
            match = re.compile('href="([^"]+?)"[ ]+title="([^"]+?)"', re.DOTALL).findall(element)
            if not match:
               debug("Keine Url")
               continue
            url="http://"+language2+".euronews.com"+match[0][0]
            title=match[0][1]
            match = re.compile('src="(.+?)"', re.DOTALL).findall(element)
            if match:
              thumb =  match[0]            
            else:
               thump=""
            match = re.compile('<p>(.+?)</p>', re.DOTALL).findall(element)
            if match:
                desc=match[0]
            else :
                 desc=""
            debug("URL :" + url)
            title=HTMLParser().unescape(title.decode('utf-8'))
            title=title.encode('utf-8')
            addLink( title, url, 'playVideo', thumb, desc)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode == "true":
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listNoComment(url):
    content = getUrl(url)
    match = re.compile('<p id="topStoryImg"><a href="(.+?)" title="(.+?)"><img src="(.+?)"', re.DOTALL).findall(content)
    match2 = re.compile('<span class="cet">(.+?) (.+?)</span>', re.DOTALL).findall(content)
    addLink(match2[0][0]+" - "+match[0][1], "http://"+language2 + ".euronews.com"+match[0][0], 'playVideo', match[0][2], "")
    spl = content.split('<div class="column span-8')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<em>nocomment \\| (.+?) (.+?)</em>', re.DOTALL).findall(entry)
        date = match[0][0]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = "http://"+language2+".euronews.com"+match[0]
        match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        title = date+" - "+cleanTitle(title)
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        addLink(title, url, 'playVideo', thumb, "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode == "true":
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShows(url):
    content = getUrl(url)
    spl = content.split('<a class="imgWrap"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = "http://"+language2+".euronews.com"+match[0]
        match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        match = re.compile('class="artTitle">(.+?)</p>', re.DOTALL).findall(entry)
        desc = ""
        if len(match) > 0:
            desc = match[0]
            desc = cleanTitle(desc)
        if "/nocomment/" in url:
            addDir(title, url, 'listNoComment', thumb, desc)
        elif "/travel/" not in url and "/in-vogue/" not in url:
            addDir(title, url, 'listVideos', thumb, desc)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode == "true":
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def search():
    keyboard = xbmc.Keyboard('', translation(30004))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        content = getUrl("http://"+language2+".euronews.com/search/", data="q="+search_string)
        content = content[content.find('<h1>Such-Resultate</h1>'):]
        content = content[:content.find('<script type="text/javascript">')]
        spl = content.split('<li')
        for i in range(1, len(spl), 1):
            entry = spl[i]
            debug("entry :"+entry)
            match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
            url = "http://"+language2+".euronews.com"+match[0]
            match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            title = match[0].replace("<strong>", "").replace("</strong>", "").replace("<br />", "")
            title = cleanTitle(title)
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb = match[0]
            addLink(title, url, 'playVideo', thumb, "")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode == "true":
            xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    content = getUrl(url)
    match = re.compile('file: "(.+?)"', re.DOTALL).findall(content)
    matchYT = re.compile('youtube.com/embed/(.+?)"', re.DOTALL).findall(content)
    if match:
        fullUrl = match[0]
    elif matchYT:
        if xbox:
            fullUrl = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + matchYT[0]
        else:
            fullUrl = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + matchYT[0] 
    listitem = xbmcgui.ListItem(path=fullUrl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name)
    playlist.add(url, listitem)


def playLive():
    #content = getUrl("http://euronews.hexaglobe.com/json/")
    #struktur = json.loads(content)        
    url="http://fr-par-iphone-1.cdn.hexaglobe.net/streaming/euronews_ewns/iphone_"+language+".m3u8"
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def cleanTitle(title):
    return title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#038;", "&").replace("&#39;", "'").replace("&#039;", "'").replace("&#8211;", "-").replace("&#8220;", "-").replace("&#8221;", "-").replace("&#8217;", "'").replace("&#8230;", "…").replace("&quot;", "\"").strip()


def getUrl(url, data=None, cookie=None):
    debug("URL :" + url)
    if data != None:
        req = urllib2.Request(url, data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    else:
        req = urllib2.Request(url)
    req.add_header(
        'User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    if cookie != None:
        req.add_header('Cookie', cookie)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    liz.setProperty('IsPlayable', 'true')
    if mode=="playVideo":
        liz.addContextMenuItems([(translation(30006), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listNoComment':
    listNoComment(url)
elif mode == 'listShows':
    listShows(url)
elif mode == 'newsMain':
    newsMain()
elif mode == 'playLive':
    playLive()
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name)
elif mode == 'search':
    search()
else:
    index()
