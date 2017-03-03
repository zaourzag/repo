#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
import os
import urllib
import urllib2
import httplib
import cookielib
import socket
import xbmcgui
import xbmcaddon
import xbmcplugin
import HTMLParser,json
from pyamf import remoting

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.dmax_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
xbox = xbmc.getCondVisibility("System.Platform.xbox")
translation = addon.getLocalizedString
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
defaultFanart = os.path.join(addonDir ,'fanart.png')
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
userDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
channelFavsFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".favorites")
maxBitRate = addon.getSetting("maxBitRate")
mobilestreams = addon.getSetting("mobilestreams")== "true"
qual = [512000, 1024000, 1536000, 2048000, 2560000, 3072000]
maxBitRate = qual[int(maxBitRate)]
baseUrl = "http://www.dmax.de"
opener = urllib2.build_opener()
userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
opener.addheaders = [('User-Agent', userAgent)]

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    

if not os.path.isdir(userDataFolder):
    os.mkdir(userDataFolder)


def index():
    addDir(translation(30002), "", 'listAZ', icon, '')
    addDir(translation(30010), "", 'listShowsFavs', icon, '')
    addDir(translation(30003), "NEU", 'listVideosLatest', icon, '')
    addDir(translation(30004), "BELIEBT", 'listVideosLatest', icon, '')
    addDir(translation(30007), "KURZE CLIPS", 'listVideosLatest', icon, '')
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideosMain(url, thumb):
    debug("listVideosMain :"+ url)
    content = opener.open(url).read()
    matchShowID = re.compile('id="dni_listing_post_id" value="(.+?)"', re.DOTALL).findall(content)  
    matchFE = re.compile('<h2>GANZE FOLGEN</h2>.+?id="dni-listing(.+?)"', re.DOTALL).findall(content)    
    matchMV = re.compile('<h2>MEIST GESEHEN</h2>.+?id="dni-listing(.+?)"', re.DOTALL).findall(content)    
    matchClips = re.compile('<h2>CLIPS</h2>.+?id="dni-listing(.+?)"', re.DOTALL).findall(content)    
    matchEpisodes = re.compile('title":"([^"]+)","url":"([^"]+)"', re.DOTALL).findall(content)
    debug("------#")
    debug(matchFE)
    showID="0"
    if matchShowID:
       showID = matchShowID[0]
    debug("match")
    if matchFE:
        for title,url in matchEpisodes:
                addDir(translation(30006), url, 'listSeasons', thumb, "")
        addDir(translation(30008), baseUrl+"/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_listing_items_filter&letter=&page=1&id="+matchFE[0]+"&post_id="+showID, 'listVideos', thumb, "")
    if matchMV:
        debug("matchMV")
        addDir(translation(30005), baseUrl+"/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_listing_items_filter&letter=&page=1&id="+matchMV[0]+"&post_id="+showID, 'listVideos', thumb, "")
    if matchClips:
        debug("matchClips")
        addDir(translation(30007), baseUrl+"/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_listing_items_filter&letter=&page=1&id="+matchClips[0]+"&post_id="+showID, 'listVideos', thumb, "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(urlMain):
    debug("listVideos :"+ urlMain)
    content = opener.open(urlMain).read()
    #content = content.replace("\\", "")
    spl = content.split('<a')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        if "(" in title:
            title = title[:title.rfind("(")].strip()
        if title.endswith("Teil 1"):
            title = title[:title.rfind("Teil 1")]
        if title.endswith(" 1") and not title.endswith("Episode 1"):
            title = title[:title.rfind(" 1")]
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = cleanTitle(match[0]).replace("_thumb", "")
        addDir(title, url, 'playVideo', thumb, title)
    try:
        matchCurrent = re.compile('"current_page":"(.+?)",', re.DOTALL).findall(content)
        matchTotal = re.compile('"total_pages":(.+?),', re.DOTALL).findall(content)
        currentPage = matchCurrent[0]
        nextPage = str(int(currentPage)+1)
        totalPages = matchTotal[0]
        if int(currentPage) < int(totalPages):
            addDir(translation(30001)+" ("+nextPage+")", urlMain.replace("page="+currentPage, "page="+nextPage), 'listVideos', icon, "")
    except:
        pass
    xbmcplugin.endOfDirectory(pluginhandle)

def cleanit(title):
    title = title.replace("Ã¼", "ü").replace("Ã¤","ä").replace("ÃŸ","ß").replace("Ã¶","ö")
    title = title.strip()    
    return title        

def listVideosLatest(type):
    content = opener.open(baseUrl+"/videos/").read()
    content = content[content.find('<div class="tab-module-header">'+type+'</div>'):]
    content = content[:content.find('</section>	</div>')]
    spl = content.split('<section class="pagetype-video" >')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        if "(" in title:
            title = title[:title.rfind("(")].strip()
        if title.endswith("Teil 1"):
            title = title[:title.rfind("Teil 1")]
        if title.endswith(" 1") and not title.endswith("Episode 1"):
            title = title[:title.rfind(" 1")]
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = cleanTitle(match[0]).replace("_thumb", "")
        title=cleanit(title)
        debug("- ::: :"+title)
        addLink(title, url, 'playVideo', thumb, title)
    xbmcplugin.endOfDirectory(pluginhandle)


def listAZ():
    letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
    for letter in letters:
        url = baseUrl+"/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_listing_items_filter&letter="+letter.upper()+"&page=1&id=bc4&post_id=2178"
        addDir(letter.upper(), url, 'listShows', icon, "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listShows(urlMain):
    debug("listshows URL:"+urlMain)
    content = opener.open(urlMain).read()
    content = content.replace("\/", "/")
    content = content.replace("\\\"", "\"")
    spl = content.split('<a')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        debug("ENTRY: "+entry)        
        match = re.compile('<h3>(.+?)</h3>', re.DOTALL).findall(entry)
        title = match[0]
        if " - VIDEOS" in title:
            title = title[:title.rfind(" - VIDEOS")].strip()
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = cleanTitle(match[0]).replace("_thumb", "")
        addShowDir(title, url, 'listSeasons', thumb, title)
    try:
        matchCurrent = re.compile('"current_page":"(.+?)",', re.DOTALL).findall(content)
        matchTotal = re.compile('"total_pages":(.+?),', re.DOTALL).findall(content)
        currentPage = matchCurrent[0]
        nextPage = str(int(currentPage)+1)
        totalPages = matchTotal[0]
        if int(currentPage) < int(totalPages):
            addDir(translation(30001)+" ("+nextPage+")", urlMain.replace("page="+currentPage, "page="+nextPage), 'listShows', icon, "")
    except:
        pass
    xbmcplugin.endOfDirectory(pluginhandle)



def listShowsFavs():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    if os.path.exists(channelFavsFile):
        fh = open(channelFavsFile, 'r')
        all_lines = fh.readlines()
        for line in all_lines:
            title = line[line.find("###TITLE###=")+12:]
            title = title[:title.find("#")]
            url = line[line.find("###URL###=")+10:]
            url = url[:url.find("#")]
            thumb = line[line.find("###THUMB###=")+12:]
            thumb = thumb[:thumb.find("#")]
            addShowRDir(title, urllib.unquote_plus(url), "listVideosMain", thumb, title)
        fh.close()
    xbmcplugin.endOfDirectory(pluginhandle)


def listSeasons(urlMain):
    debug("urlMain :"+urlMain)
    content = opener.open(urlMain).read()
    videos = content.split('\"cfct-module dni-listing\"')
    for i in range(1,len(videos),1):  
      try:
        name_reg = re.compile('<div class="tab-module-header">(.+?)</div>', re.DOTALL).findall(videos[i])
        name=name_reg[0]
        addDir(name, urlMain, 'listEpisodes',"","",text=name)
      except:
        pass
    videos = content.split('\"cfct-module dni-content-grid\"')
    for i in range(1,len(videos),1):   
      try:    
          name_reg = re.compile('<div class="tab-module-header">(.+?)</div>', re.DOTALL).findall(videos[i])
          name=name_reg[0]
          addDir(name, urlMain, 'listEpisodes',"","",text=name)            
      except:
          pass
    xbmcplugin.endOfDirectory(pluginhandle)


def listEpisodes(url, text):
        debug("URL listepisodes :" + url)
        debug("text listepisodes :" + text)
        content = opener.open(url).read()
        videos = content.split('\"cfct-module dni-listing\"')                      
        for i in range(1,len(videos),1):
           debug("####### "+ videos[i])
           name_reg = re.compile('<div class="tab-module-header">(.+?)</div>', re.DOTALL).findall(videos[i])
           namel=name_reg[0]
           if namel==text:
            json_reg = re.compile('dniListingData = {(.+?)};', re.DOTALL).findall(videos[i])        
            jsonstring="{"+json_reg[0]+"}"
            debug("----" + jsonstring)
            struktur = json.loads(jsonstring)
            for name in struktur["raw"]:  
                title=unicode(name["title"]).encode("utf-8")            
                addLink(title, name["url"], 'playVideo',name["image"], title)  
        videos = content.split('\"cfct-module dni-content-grid\"')                      
        for i in range(1,len(videos),1):
           debug("####### "+ videos[i])
           try:
            name_reg = re.compile('<div class="tab-module-header">(.+?)</div>', re.DOTALL).findall(videos[i])
            namel=name_reg[0]
           except: 
             pass
           if namel==text:
            names_reg = re.compile('<a href="(.+?)" target="" onClick=".+?">.+?<img class="" src="(.+?)" alt=".+?" ><h3>(.+?)</h3></div></a>', re.DOTALL).findall(videos[i])                                    
            for url,img,name in names_reg:            
               addLink(name, url, 'playVideo',img, name)                   
        xbmcplugin.endOfDirectory(pluginhandle)



def playVideo(url, title, thumb):
    debug("playVideo url : "+ url)
    content = opener.open(url).read()
    matchMulti = re.compile('<li data-number="(.+?)" data-guid="(.+?)"', re.DOTALL).findall(content)
    matchSingle = re.compile('name="@videoPlayer" value="(.+?)"', re.DOTALL).findall(content)
    if matchMulti:
        addDir(title+": Alle Teile", url, "playVideoAll", thumb, title)
        for part, videoID in matchMulti:
            addLink(title+": Teil "+part, videoID, "playBrightCoveStream", thumb, title, "no")
            debug("matchMulti : "+ videoID)
        xbmcplugin.endOfDirectory(pluginhandle)
    elif matchSingle:
        debug("matchSingle : "+ matchSingle[0])
        playBrightCoveStream(matchSingle[0],title,thumb,"yes")
                


def playVideoAll(url, title, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    content = opener.open(url).read()
    matchMulti = re.compile('<li data-number="(.+?)" data-guid="(.+?)"', re.DOTALL).findall(content)
    for part, videoID in matchMulti:
        listitem = xbmcgui.ListItem(title+": Teil "+part, thumbnailImage=thumb)
        if xbox:
            pluginUrl = "plugin://video/DMAX.de/?url="+videoID+"&mode=playBrightCoveStream&isSingle=no&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(thumb)
        else:
            pluginUrl = "plugin://plugin.video.dmax_de/?url="+videoID+"&mode=playBrightCoveStream&isSingle=no&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(thumb)
        playlist.add(pluginUrl, listitem)
    if playlist:
        xbmc.Player().play(playlist)


def playBrightCoveStream(bc_videoID, title, thumb, isSingle):
    bc_playerID = 586587148001
    bc_publisherID = 1659832546
    bc_const = "ef59d16acbb13614346264dfe58844284718fb7b"
    conn = httplib.HTTPConnection("c.brightcove.com")
    envelope = remoting.Envelope(amfVersion=3)
    envelope.bodies.append(("/1", remoting.Request(target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById", body=[bc_const, bc_playerID, bc_videoID, bc_publisherID], envelope=envelope)))
    conn.request("POST", "/services/messagebroker/amf?playerId=" + str(bc_playerID), str(remoting.encode(envelope).read()), {'content-type': 'application/x-amf'})
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body
    streamUrl = ""
    if mobilestreams :
        rubrik="IOSRenditions"
    else:
        rubrik="renditions"
    for item in sorted(response[rubrik], key=lambda item: item['encodingRate'], reverse=False):
        encRate = item['encodingRate']
        if encRate < maxBitRate:
            streamUrl = item['defaultURL']    
    if not streamUrl:
        streamUrl = response['FLVFullLengthURL']
    if streamUrl:
            listitem = xbmcgui.ListItem(title, path=streamUrl, thumbnailImage=thumb)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def favs(param):
    mode = param[param.find("###MODE###=")+11:]
    mode = mode[:mode.find("###")]
    channelEntry = param[param.find("###TITLE###="):]
    if mode == "ADD":
        if os.path.exists(channelFavsFile):
            fh = open(channelFavsFile, 'r')
            content = fh.read()
            fh.close()
            if content.find(channelEntry) == -1:
                fh = open(channelFavsFile, 'a')
                fh.write(channelEntry+"\n")
                fh.close()
        else:
            fh = open(channelFavsFile, 'a')
            fh.write(channelEntry+"\n")
            fh.close()
    elif mode == "REMOVE":
        refresh = param[param.find("###REFRESH###=")+14:]
        refresh = refresh[:refresh.find("#")]
        fh = open(channelFavsFile, 'r')
        content = fh.read()
        fh.close()
        entry = content[content.find(channelEntry):]
        fh = open(channelFavsFile, 'w')
        fh.write(content.replace(channelEntry+"\n", ""))
        fh.close()
        if refresh == "TRUE":
            xbmc.executebuiltin("Container.Refresh")




def cleanTitle(title):
    title = title.decode('unicode_escape').encode("utf-8")
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


def addLink(name, url, mode, iconimage, title, isSingle="no", desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&isSingle="+str(isSingle)+"&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    liz.setProperty('IsPlayable', 'true')
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultFanart)
    liz.addContextMenuItems([(translation(30009), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&title='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, title, desc="",text=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(iconimage)
    if text!="":
        u=u+"&text="+urllib.quote_plus(text)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultFanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDir(name, url, mode, iconimage, title, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultFanart)
    playListInfos = "###MODE###=ADD###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30011), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowRDir(name, url, mode, iconimage, title, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultFanart)
    playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30012), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
isSingle = urllib.unquote_plus(params.get('isSingle', 'yes'))
thumb = urllib.unquote_plus(params.get('thumb', ''))
title = urllib.unquote_plus(params.get('title', ''))
text = urllib.unquote_plus(params.get('text', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listVideosLatest':
    listVideosLatest(url)
elif mode == 'listVideosMain':
    listVideosMain(url, thumb)
elif mode == 'listAZ':
    listAZ()
elif mode == 'listShows':
    listShows(url)
elif mode == 'listSeasons':
    listSeasons(url)
elif mode == 'listEpisodes':
    listEpisodes(url,text)
elif mode == 'playVideo':
    playVideo(url, title, thumb)
elif mode == 'queueVideo':
    queueVideo(url, title, thumb)
elif mode == 'playVideoAll':
    playVideoAll(url, title, thumb)
elif mode == 'playBrightCoveStream':
    playBrightCoveStream(url, title, thumb, isSingle == "yes")
elif mode == 'listShowsFavs':
    listShowsFavs()
elif mode == 'favs':
    favs(url)
else:
    index()
