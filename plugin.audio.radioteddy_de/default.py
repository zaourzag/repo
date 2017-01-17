#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmcaddon,base64

pluginhandle = int(sys.argv[1])
settings = xbmcaddon.Addon(id='plugin.audio.radioteddy_de')

forceViewMode=settings.getSetting("forceViewMode")
if forceViewMode=="true":
  forceViewMode=True
else:
  forceViewMode=False
viewMode=str(settings.getSetting("viewMode"))

def index():
        addLink("RadioTeddy - Livestream","http://streams.ir-media-tec.com/radioteddy.mp3",'playAudio',"http://webplayer.radioteddy.de/img/_channels/_header/live.png")
        addLink("Made in Germany","http://streams.ir-media-tec.com/radioteddy-ch05.mp3",'playAudio',"http://webplayer.radioteddy.de/img/_channels/_header/ch05.png")
        addLink("Kinder Disco","http://streams.ir-media-tec.com/radioteddy-ch02.mp3",'playAudio',"http://webplayer.radioteddy.de/img/_channels/_header/ch02.png")
        addLink("Soft Mix","http://streams.ir-media-tec.com/radioteddy-ch06.mp3",'playAudio',"http://webplayer.radioteddy.de/img/_channels/_header/ch06.png")
        addLink("Gute Nacht Musik","http://streams.ir-media-tec.com/radioteddy-ch03.mp3",'playAudio',"http://webplayer.radioteddy.de/img/_channels/_header/ch03.png")
        addLink("Weihnachtslieder","http://streams.ir-media-tec.com/radioteddy-ch07.mp3",'playAudio',"http://webplayer.radioteddy.de/img/_channels/_header/ch07.png")
        addLink("Kinderlieder","http://streams.ir-media-tec.com/radioteddy-ch04.mp3",'playAudio',"http://webplayer.radioteddy.de/img/_channels/_header/ch04.png")
        addLink("TEDDY Cool","http://streams.ir-media-tec.com/radioteddy-ch01.mp3",'playAudio',"http://webplayer.radioteddy.de/img/_channels/_header/ch01.png")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode==True:
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playAudio(url):
        if url.find(".m3u")>=0:
          url=getUrl(url)
        listitem = xbmcgui.ListItem(path=url)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def cleanTitle(title):
        title=title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#039;","\\").replace("&quot;","\"").replace("&szlig;","ß").replace("&ndash;","-")
        title=title.replace("&Auml;","Ä").replace("&Uuml;","Ü").replace("&Ouml;","Ö").replace("&auml;","ä").replace("&uuml;","ü").replace("&ouml;","ö")
        title=title.strip()
        return title

def getUrl(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0')
        response = urllib2.urlopen(req,timeout=60)
        link=response.read()
        response.close()
        return link

def parameters_string_to_dict(parameters):
        ''' Convert parameters encoded in a URL to a dict. '''
        paramDict = {}
        if parameters:
            paramPairs = parameters[1:].split("&")
            for paramsPair in paramPairs:
                paramSplits = paramsPair.split('=')
                if (len(paramSplits)) == 2:
                    paramDict[paramSplits[0]] = paramSplits[1]
        return paramDict

def addLink(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
         
params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)

if mode == 'playAudio':
    playAudio(url)
else:
    index()
