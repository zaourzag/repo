# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,sys,urllib,urllib2,re,socket
import os
import xml.dom.minidom
import random

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.video.cinetrailer.tv')

home = addon.getAddonInfo('path').decode('utf-8')
imageDir = os.path.join(home, 'thumbnails') + '/'
fanart=imageDir+"fanart1.jpg"
translation = addon.getLocalizedString
language=xbmc.getInfoLabel('System.Language')
xbox=xbmc.getCondVisibility("System.Platform.xbox")

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
def CATEGORIES():
        if language=='Italian':
          addDir(translation(30005),'0',"Parse",'')
        addDir(translation(30001),'1',"Parse",'')
        addDir(translation(30002),'2',"Parse",'')
        addDir(translation(30003),'3',"Parse",'')
        addDir(translation(30004),'4',"Parse",'')

def Parse(url):
	if language=='German':
	  region='de'
        elif language=='English':
          region='uk'
        elif language=='Italian':
          region='it'
        elif language=='French':
          region='fr'
        elif language=='Spanish':
          region='es'
        id=url
        id=int(id)
        intid = 100 + id 
        strid = str(intid)
        if region =='it':
          url="http://cinetrailer.it/getblob.aspx?path=nettv.cinetrailer/xml&container=webservices-xml&filename=movie_"+ str(id) + ".xml"
        else:
          url="http://cinetrailer.it/getblob.aspx?path=nettv.cinetrailer/xml&container=webservices-xml&filename=movie_"+ region + "_" + str(id) + ".xml"
        print 'ffffffffffffffffffffffffffffffffffffffff'+url
        dom = xml.dom.minidom.parse(urllib.urlopen(url))
        movies = dom.getElementsByTagName("movie")
        for movie in movies:
			title_id= str(movie.getElementsByTagName("id_movie")[0].firstChild.toxml("utf-8"))
			title = str(movie.getElementsByTagName("titolo")[0].firstChild.toxml("utf-8"))
			title = title[9:len(title)-3]
			url='http://player.cinetrailer.tv/%s/new/%s' % (region,title_id)
			try:
				thumb = str(movie.getElementsByTagName("poster")[0].firstChild.nodeValue)
			except:
				thumb=''
			premiere = str(movie.getElementsByTagName("premiere_date")[0].firstChild.nodeValue)
			premiere =re.search('(.*?)T.*?',premiere)
			premiere =premiere.group(1)
			fanart = str(movie.getElementsByTagName("screenshot")[0].firstChild.nodeValue)
			title = premiere+'     '+title
			addLink(title,fanart,url,"Videolink",thumb, '')

def Videolink(url):
       debug("Videolink URL"+ url)
       data=urllib2.urlopen(url).read()
       debug("DATA :")
       debug (data)
       if xbox:
		   video_url=re.findall("var clipUrlLQ = '(.*?)'",data,re.S)[0]
       else:
		   video_url=re.findall("var clipUrlHQ = '(.*?)'",data,re.S)[0]
       if "youtube" in video_url:
          id=video_url.replace("https://www.youtube.com/watch?v=","")
          debug(" ID ::::::"+id)
          video_url='plugin://plugin.video.youtube/?action=play_video&videoid='+ id           
       listitem = xbmcgui.ListItem(path=video_url)
       return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        #liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addLink(name,fanart,url,mode,iconimage,desc):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&fanart="+urllib.quote_plus(fanart)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name , "Plot": desc } )
        #liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

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

params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
fanart=params.get('fanart')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)
if mode == 'Parse':
    Parse(url)

elif mode == 'Videolink':
    Videolink(url)
else:
    CATEGORIES()
xbmcplugin.endOfDirectory(pluginhandle)
