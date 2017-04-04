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
import time
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
        playVideoAll(url,title,thumb)
        #xbmcplugin.endOfDirectory(pluginhandle)
    elif matchSingle:
        debug("matchSingle : "+ matchSingle[0])        
        streamUrl=getStream(bc_videoID)        
        listitem = xbmcgui.ListItem(title, path=streamUrl, thumbnailImage=thumb)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
                


def playVideoAll(url, title, thumb):
    debug("playVideoAll url"+url)
    pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    pl.clear()
    content = opener.open(url).read()
    matchMulti = re.compile('<li data-number="([^"]+?)" data-guid="([^"]+?)"', re.DOTALL).findall(content)
    for part, videoID in matchMulti:         
        listitem = xbmcgui.ListItem(title+": Teil "+part, thumbnailImage=thumb)        
        pluginUrl=getStream(videoID)
        pl.add(pluginUrl, listitem)        
    if pl:
        xbmc.Player().play(pl)   
        time.sleep(10000)


def  getStream(bc_videoID):
    debug("getStream bc_videoID :"+str(bc_videoID))
    bc_playerID = 586587148001
    bc_publisherID = 1659832546
    bc_const = "ef59d16acbb13614346264dfe58844284718fb7b"
        
    conn = httplib.HTTPConnection("c.brightcove.com")
    envelope = remoting.Envelope(amfVersion=3)
    envelope.bodies.append(("/1", remoting.Request(target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById", body=[bc_const, bc_playerID, bc_videoID, bc_publisherID], envelope=envelope)))
        
    conn.request("POST", "/services/messagebroker/amf?playerId=" + str(bc_playerID), str(remoting.encode(envelope).read()), {'content-type': 'application/x-amf'})    
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body    
    # Response ist:
    #{'startDate': None, 'adCategories': None, 'endDate': None, 'drmMetadataURL': None, 'color': None, 'FLVFullSize': 272122334.0, 'FLVFullLengthURL': u'http://discintlhdflash-f.akamaihd.net/byocdn/media/1659832546/201412/953/1659832546_3921288417001_mp4-DCB355460006000-106.mp4', 'SWFVerificationRequired': False, 'FLVFullCodec': 3, 'hdsManifestUrl': None, 'thumbnailURL': u'http://discoveryint1.edgeboss.net/byocdn/img/1659832546/201412/481/1659832546_3921221378001_thumb-discovery-DCB355460006000-106.jpg?pubId=1659832546', 'FLVPreviewSize': 0.0, 'FLVPreviewStreamed': False, 'rentalAmount': None, 'geoRestricted': True, 'filterEndDate': None, 'customFields': None, 'FLVPreBumperControllerType': 0, 'rentalPeriod': None, 'yearProduced': None, 'IOSRenditions': [{'videoCodec': u'H264', 'defaultURL': u'http://c.brightcove.com/services/mobile/streaming/index/rendition.m3u8?assetId=3922596652001', 'encodingRate': 1240000, 'audioOnly': False, 'videoContainer': 2, 'mediaDeliveryType': 2, 'frameWidth': 640, 'frameHeight': 360, 'size': 418914295.0}, {'videoCodec': u'H264', 'defaultURL': u'http://c.brightcove.com/services/mobile/streaming/index/rendition.m3u8?assetId=3922569188001', 'encodingRate': 640000, 'audioOnly': False, 'videoContainer': 2, 'mediaDeliveryType': 2, 'frameWidth': 400, 'frameHeight': 224, 'size': 216883038.0}, {'videoCodec': u'H264', 'defaultURL': u'http://c.brightcove.com/services/mobile/streaming/index/rendition.m3u8?assetId=3922575873001', 'encodingRate': 240000, 'audioOnly': False, 'videoContainer': 2, 'mediaDeliveryType': 2, 'frameWidth': 320, 'frameHeight': 180, 'size': 81365538.0}], 'publishedDate': datetime.datetime(2014, 12, 8, 17, 3, 14, 355000), 'FLVPreBumperURL': None, 'purchaseAmount': None, 'sharedToExternalAcct': False, 'longDescription': u'Lotto King Karl in einer 35 Tonnen schweren Baumaschine gegen ein dreist\xf6ckiges Geb\xe4ude: In dieser Folge rei\xdft der S\xe4nger, Moderator und Stadionsprecher mit Schere und Mei\xdfel ein Haus ein. Da kommt Freude auf! Au\xdferdem besucht Lotto Michael Manousakis von den "Steel Buddies" und testet dessen "Hammerteile". Sabine Schmitz feiert ein Wiedersehen mit ihrem ersten Auto, einem VW Polo. Und beim "Auto-Quartett" trumpfen der Ferrari 458 und der McLaren MP4-12C ganz gro\xdf auf.', 'referenceId': u'DCB355460006000_106', 'creationDate': datetime.datetime(2014, 12, 3, 13, 55, 4, 394000), 'sharedByExternalAcct': False, 'categories': [], 'renditions': [{'videoCodec': u'H264', 'defaultURL': u'http://discintlhdflash-f.akamaihd.net/byocdn/media/1659832546/201412/208/1659832546_3922585920001_mp4-DCB355460006000-106.mp4', 'encodingRate': 542409, 'audioOnly': False, 'videoContainer': 1, 'mediaDeliveryType': 0, 'frameWidth': 480, 'frameHeight': 268, 'size': 182233038.0}, {'videoCodec': u'H264', 'defaultURL': u'http://discintlhdflash-f.akamaihd.net/byocdn/media/1659832546/201412/1720/1659832546_3922667311001_mp4-DCB355460006000-106.mp4', 'encodingRate': 1778409, 'audioOnly': False, 'videoContainer': 1, 'mediaDeliveryType': 0, 'frameWidth': 1280, 'frameHeight': 720, 'size': 593914274.0}, {'videoCodec': u'H264', 'defaultURL': u'http://discintlhdflash-f.akamaihd.net/byocdn/media/1659832546/201412/3088/1659832546_3922591176001_mp4-DCB355460006000-106.mp4', 'encodingRate': 1178409, 'audioOnly': False, 'videoContainer': 1, 'mediaDeliveryType': 0, 'frameWidth': 720, 'frameHeight': 404, 'size': 394800905.0}, {'videoCodec': u'H264', 'defaultURL': u'http://discintlhdflash-f.akamaihd.net/byocdn/media/1659832546/201412/953/1659832546_3921288417001_mp4-DCB355460006000-106.mp4', 'encodingRate': 810409, 'audioOnly': False, 'videoContainer': 1, 'mediaDeliveryType': 0, 'frameWidth': 640, 'frameHeight': 360, 'size': 272122334.0}], 'ratingEnum': None, 'submitted': False, 'excludeListedCountries': False, 'logoOverlay': {'burnIn': False, 'assetURL': u'http://discoveryint1.edgeboss.net/byocdn/img/1659832546/201401/155/1659832546_3122320618001_DMAX-bug.png?pubId=1659832546', 'clickThru': None, 'version': 0, 'tooltip': None, 'id': 3925518439001.0, 'alignment': u'top left', 'assetDTO': {'progressiveDownload': True, 'referenceId': None, 'encodingRate': None, 'audioOnly': False, 'videoContainer': -1, 'frameWidth': None, 'assetTypeEnum': 17, 'id': 3122320618001.0, 'size': 4986.0, 'absoluteURL': None, 'uploadTypeEnum': 50, 'dualDeliveryHttpURL': u'http://discoveryint1.edgeboss.net/byocdn/img/1659832546/201401/155/1659832546_3122320618001_DMAX-bug.png', 'hashCode': u'MD5:bc235ef1ed1765f44d4e6f4b1a804d36', 'defaultURL': u'http://discoveryint1.edgeboss.net/byocdn/img/1659832546/201401/155/1659832546_3122320618001_DMAX-bug.png?pubId=1659832546', 'version': 6, 'frameHeight': None, 'videoCodecEnum': 0, 'uploadTimestampMillis': 1391010523773.0, 'mimeTypeEnum': 6, 'originalFilename': u'DMAX_bug.png', 'complete': True, 'assetControllerTypeEnum': 0, 'controllerType': 0, 'absoluteStreamName': None, 'previewThumbnailURL': None, 'currentFilename': u'1659832546_3122320618001_DMAX-bug.png', 'videoDuration': 0.0, 'displayName': u'DMAX_bug.png', 'DRMEncoded': False, 'campaignPolicyId': None, 'previewThumbnailAssetId': None, 'CDNStored': True, 'fingerprinted': False, 'publisherId': 1659832546.0}}, 'publisherId': 1659832546.0, 'publisherName': u'Discovery Networks - Germany', 'videoStillURL': u'http://discoveryint1.edgeboss.net/byocdn/img/1659832546/201412/3481/1659832546_3921221377001_still-discovery-DCB355460006000-106.jpg?pubId=1659832546', 'encodingRate': 810409, 'sharedBy': None, 'allowViralSyndication': True, 'isSubmitted': False, 'lineupId': None, 'captions': None, 'shortDescription': u'Lotto King Karl in einer 35 Tonnen schweren Baumaschine gegen ein dreist\xf6ckiges Geb\xe4ude: In dieser Folge rei\xdft der S\xe4nger, Moderator und Stadionsprecher mit Schere und Mei\xdfel ein Haus ein.', 'id': 3921212119001.0, 'previewLength': 0.0, 'customFieldValues': None, 'allowedCountries': [u'li', u'de', u'at', u'lu', u'ch'], 'FLVPreBumperStreamed': False, 'version': None, 'HDSRenditions': None, 'dateFiltered': False, 'FLVFullLengthStreamed': True, 'monthlyAmount': None, 'tags': [{'image': None, 'name': u'topic:entertainment'}, {'image': None, 'name': u'series:01'}, {'image': None, 'name': u'site:DMAX Germany'}, {'image': None, 'name': u'Herbert Feuerstein'}, {'image': None, 'name': u'motorrad'}, {'image': None, 'name': u'auto'}, {'image': None, 'name': u'powerboot'}, {'image': None, 'name': u'Lotto King Karl'}, {'image': None, 'name': u'autos'}, {'image': None, 'name': u'episode:06'}, {'image': None, 'name': u'show:hammerteile'}, {'image': None, 'name': u'form:long'}], 'controllerType': 5, 'sharedSourceId': None, 'awards': None, 'linkText': None, 'FLVPreviewURL': None, 'forceAds': False, 'WMVFullAssetId': None, 'numberOfPlays': 0.0, 'cuePoints': None, 'displayName': u'Hammerteile: Einst\xfcrzende Altbauten', 'filterStartDate': None, 'language': None, 'FLVPreviewCodec': 0, 'economics': 1, 'length': 2649328.0, 'WMVFullLengthURL': None, 'adKeys': None, 'linkURL': None}
    debug("############+#")
    debug(response)   
    debug("############+#")
    debug(response['IOSRenditions'])    
    maxbit=0
    # Mobile Streams sind in IOSRenditions Gespeichert, Webstreams in renditions
    # Mobile Streams < 720 , Web gibt es in 720,aber spoolen geht nicht
    if mobilestreams:
       type="IOSRenditions"
       type2="renditions"
    else:
       type="renditions"
       type2="IOSRenditions"
    # Sollte kein Stream im Ausgewählten Type geben (Mobile/Nicht Mobile) nutze den anderen
    if len(response[type])<1:
        type=type2
    
    # Streams durchgehen, und den mit der Höchsten Bitrarate raussuchen    
    for element in response[type]:             
        if element["encodingRate"] <= maxBitRate and maxbit < element["encodingRate"]:
            streamUrl = element['defaultURL']
            maxbit =  element["encodingRate"]          
    # Wenn keinen Stream gibt nimm den Fallback
    if not streamUrl:
        streamUrl = response['FLVFullLengthURL']
    return(streamUrl)
    
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
elif mode == 'listShowsFavs':
    listShowsFavs()
elif mode == 'favs':
    favs(url)
else:
    index()
