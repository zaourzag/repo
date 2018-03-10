#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil,json
import time
import base64
import requests
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser
import datetime

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
country=addon.getSetting("sprache")
prefQuality=int(addon.getSetting("quality"))
xbmcplugin.setContent(addon_handle, 'movies')
baseURL = "https://www.arte.tv/"
ARTE_apiURL = "https://www.arte.tv/guide/api/api"


xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)


icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')


profile    = xbmc.translatePath(addon.getAddonInfo('profile')).decode("utf-8")
temp       = xbmc.translatePath(os.path.join( profile, 'temp', '')).decode("utf-8")

try:
    if xbmcvfs.exists(temp):
        shutil.rmtree(temp)
except: pass
xbmcvfs.mkdirs(temp)
cookie=os.path.join( temp, 'cookie.jar')
cj = cookielib.LWPCookieJar();

if xbmcvfs.exists(cookie):
    cj.load(cookie,ignore_discard=True, ignore_expires=True)                  

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def addDir(name, url, mode, thump, desc="", page=1, nosub=0):   
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&nosub="+str(nosub)
    ok = True
    liz = xbmcgui.ListItem(name)  
    liz.setArt({'fanart': thump})
    liz.setArt({'thumb': thump})
    liz.setArt({'banner': icon})
    liz.setArt({'fanart': icon})
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addLink(name, url, mode, thump, duration="", desc="", genre='', director="", bewertung=""):
    debug("URL ADDLINK :"+url)
    debug(icon)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name,thumbnailImage=thump)
    liz.setArt({ 'fanart' : icon })
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre, "Director": director, "Rating": bewertung})
    liz.setProperty('IsPlayable', 'true')
    liz.addStreamInfo('video', { 'duration' : duration })
    #xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok
  
def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

def geturl(url,data="x",header="",referer=""):
    global cj
    debug("Get Url: " +url)
    for cook in cj:
        debug(" Cookie :"+ str(cook))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    if header=="":
        opener.addheaders = [('User-Agent', userAgent)]
    else:
        opener.addheaders = header
    if not referer=="":
        opener.addheaders = [('Referer', referer)]
    try:
        if data!="x" :
            content=opener.open(url,data=data).read()
        else:
            content=opener.open(url).read()
    except urllib2.HTTPError as e:
        #debug( e.code )  
        cc=e.read()  
        debug("Error : " +cc)
        content=""
    opener.close()
    cj.save(cookie,ignore_discard=True, ignore_expires=True)
    return content

def liste():
    UN_Supported = ['360', 'Accue', 'Direct', 'Digitale', 'Edition', 'Guide', 'Home', 'Live', 'Magazin', 'productions', 'Programm', 'VOD/DVD']
    content=geturl(baseURL+country+"/")
    htmlPage = BeautifulSoup(content, 'html.parser')
    elemente = htmlPage.find_all("li",attrs={"class":"next-menu-nav__item"})
    for element in elemente:
        link=element.find("a")
        name=link.text.strip()
        url=link["href"]
        if not any(x in name for x in UN_Supported):
            addDir(name,url,"subrubrik",icon)
    xbmcplugin.endOfDirectory(addon_handle)

def subrubrik(surl):
    content=geturl(surl)
    htmlPage = BeautifulSoup(content, 'html.parser')
    elemente = htmlPage.find_all("li",attrs={"class":"next-menu-nav__item"})
    anz=0
    for element in elemente :
        if '"'+surl+'"' in str(element):
            debug(element)
            debug("------")
            try:
                elemente2=element.find_all("li",attrs={"class":"next-menu-nav__item"})
                debug("++++++++++++")
                debug(elemente2)
                for element in elemente2:
                    debug(element)
                    debug("+++++++")
                    link=element.find("a")
                    url=link["href"]
                    name=link.text.strip()
                    if not "arte info" in name.lower():
                        addDir(name,url,"videoliste",icon)
                        anz=1
            except: pass
    if anz==0:
         videoliste(surl)
    xbmcplugin.endOfDirectory(addon_handle) 

def playvideo(url):
    # Übergabe des Abspiellinks von anderem Video-ADDON: plugin://plugin.video.L0RE.arte/?mode=playvideo&url=048256-000-A oder: plugin://plugin.video.L0RE.arte/?mode=playvideo&url=https://www.arte.tv/de/videos/048256-000-A/wir-waren-koenige/
    try:
        if url.startswith('http'):
            idd = re.compile('/videos/(.+?)/', re.DOTALL).findall(url)[0]
        else:
            idd = url
        if country=="de":
            standards1="OV" # Stumm oder Originalversion
            standards2="OmU" # Original mit deutschen Untertiteln
            standards3="DE" # Original deutsch
        elif country=="fr":
            standards1="VOSTF" # Stumm oder Original mit französischen Untertiteln
            standards2="VF" # französisch vertont
            standards3="VOF" # Original französisch
        #elif country=="pl":
            #sub="DE-POL"
        #elif country=="es":
            #sub="DE-ESP"
        try: 
            content = geturl("https://api.arte.tv/api/player/v1/config/"+country+"/"+idd+"?autostart=0&lifeCycle=1")
        except: return -1 # no network
        finalURL = False
        stream = json.loads(content)['videoJsonPlayer']
        stream_offer = stream['VSR']
        debug("----->")
        for element in stream_offer:
            debug(stream['VSR'][element])
            if int(stream['VSR'][element]["versionProg"]) == 1 and stream['VSR'][element]["mediaType"].lower() == "mp4":
                if stream['VSR'][element]["versionShortLibelle"]==standards3 and stream['VSR'][element]["height"]==prefQuality:
                    finalURL = stream['VSR'][element]["url"]
                if not finalURL and stream['VSR'][element]["versionShortLibelle"]==standards2 and stream['VSR'][element]["height"]==prefQuality:
                    finalURL = stream['VSR'][element]["url"]
                if not finalURL and stream['VSR'][element]["versionShortLibelle"]==standards1 and stream['VSR'][element]["height"]==prefQuality:
                    finalURL = stream['VSR'][element]["url"]
                if not finalURL and "VO" in stream['VSR'][element]["versionCode"] and stream['VSR'][element]["height"]==prefQuality:
                    finalURL = stream['VSR'][element]["url"]
        debug(prefQuality)
        debug("playvideo - finalUrl: "+finalURL)
        debug("<-----")
        if finalURL:
            listitem = xbmcgui.ListItem(path=finalURL)
            listitem.setProperty('IsPlayable', 'true')
            xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
        else:
            xbmcgui.Dialog().notification(addon.getAddonInfo('id')+" : [COLOR red]!!! STREAM - URL - ERROR !!![/COLOR]", "ERROR = [COLOR red]KEINE passende *Stream-Url* auf ARTE gefunden ![/COLOR]", xbmcgui.NOTIFICATION_ERROR, time=6000)
    except:
        xbmcgui.Dialog().notification(addon.getAddonInfo('id')+" : [COLOR red]!!! VIDEO - URL - ERROR !!![/COLOR]", "ERROR = [COLOR red]Der übertragene *Video-Abspiel-Link* ist FEHLERHAFT ![/COLOR]", xbmcgui.NOTIFICATION_ERROR, time=6000)

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
referer = urllib.unquote_plus(params.get('referer', ''))
page = urllib.unquote_plus(params.get('page', ''))
nosub= urllib.unquote_plus(params.get('nosub', ''))
query = urllib.unquote_plus(params.get('query', ''))

def videoliste(url,page="1"):  
    debug("Start Videoliste")
    debug(url)
    SUPPORTED = ['Bonus', 'Programm', 'Programme']
    #https://www.arte.tv/guide/api/api/zones/de/web/videos_subcategory_OPE?page=2&limit=10
    #https://www.arte.tv/sites/de/webproductions/api/?lang=de&paged=3  
    if int(page)==1:
        content=geturl(url)
        #"nextPage":"https:\u002F\u002Fapi-cdn.arte.tv\u002Fapi\u002Femac\u002Fv2\u002Fde\u002Fweb\u002Fzones\u002Fvideos_subcategory_OPE?page=2&limit=10"
        content=re.compile(' window.__INITIAL_STATE__ = ({.+})', re.DOTALL).findall(content)[0]
        struktur1 = json.loads(content)
        debug("###")
        debug(struktur1)
        sub1=struktur1["pages"]["list"]
        key=sub1.keys()[0]
        sub2=sub1[key]["zones"]
        debug(sub2)
        for zone in sub2:
            debug("++++")
            debug(zone)
            try:
                debug(zone["data"][0]["kind"]["label"])
                if any(x in zone["data"][0]["kind"]["label"] for x in SUPPORTED):
                    code=zone["code"]
                    break
            except: pass
        url=ARTE_apiURL+"/zones/"+country+"/web/"+str(code)
    jsonurl=url+"?page="+page+"&limit=50"
    debug(jsonurl)
    content=geturl(jsonurl)
    struktur2 = json.loads(content)
    for element in struktur2["data"]:
        videourl=element["url"].encode("utf-8")
        title=element["title"].encode("utf-8")
        try:
            subtitle=element["subtitle"].encode("utf-8")
            title=title+ " - "+subtitle
        except: pass
        try: desc=element["description"].encode("utf-8")
        except: desc=""
        bild=element["images"]["landscape"]["resolutions"][-1]["url"].encode("utf-8")
        duration=element["duration"]
        if duration and duration != "" and duration != "0":
            addLink(title,videourl,"playvideo",bild,duration=duration,desc=desc)
    try:
        debug("NextPage try:")
        nextpage=struktur2["nextPage"]
        debug(nextpage)
        debug("Endnext")
        if nextpage.startswith("http"):
            addDir("Next Page >>>",url,"videoliste",icon,page=int(page)+1)
    except: pass
    xbmcplugin.endOfDirectory(addon_handle)
# Haupt Menu Anzeigen     
def menu():
    if country=="de":
        addDir("Themen", "", "liste",icon)
        addDir("Programm", "", "datummenu",icon)
        addDir("Sendungen A-Z",baseURL+country+"/videos/sendungen/","abiszetc",icon)
        addDir("Meistgesehen",baseURL+country+"/videos/meistgesehen/","abiszetc",icon)
        addDir("Neueste Videos",baseURL+country+"/videos/neueste-videos/","abiszetc",icon)
        addDir("Letzte Chance",baseURL+country+"/videos/letzte-chance/","abiszetc",icon)
        addDir("Videos sortiert nach Laufzeit","","listVideos_Time",icon)
        addDir("Live TV", "", "live",icon)
        addDir("Suche ...", "", "SearchArte",icon)
        addDir("Einstellungen", "", "Settings",icon)
    elif country=="fr":
        addDir("Sujets", "", "liste",icon)
        addDir("Guide +7", "", "datummenu",icon)
        addDir("Émissions A-Z",baseURL+country+"/videos/emissions/","abiszetc",icon)
        addDir("Les plus vues",baseURL+country+"/videos/plus-vues/","abiszetc",icon)
        addDir("Les plus récentes",baseURL+country+"/videos/plus-recentes/","abiszetc",icon)
        addDir("Dernière chance",baseURL+country+"/videos/derniere-chance/","abiszetc",icon)
        addDir("Vidéos triées par durée","","listVideos_Time",icon)
        addDir("Recherche ...", "", "SearchArte",icon)
        addDir("Paramètres", "", "Settings",icon)
    xbmcplugin.endOfDirectory(addon_handle)

def abiszetc(url,page="1",query=False):
    xbmcplugin.setContent(addon_handle, 'tvshows')
    newUrl = url
    if int(page)==1:
        content=geturl(url)
        content=re.compile(' window.__INITIAL_STATE__ = ({.+})', re.DOTALL).findall(content)[0]
        struktur1 = json.loads(content)
        debug("###")
        debug(struktur1)
        sub1=struktur1["pages"]["list"]
        key=sub1.keys()[0]
        sub2=sub1[key]["zones"]    
        code=sub2[0]["code"]
        debug("CODE : "+code)
        url=ARTE_apiURL+"/zones/"+country+"/web/"+str(code)
    if '###' in url:
        nextQuery=url.split('###')[1].replace('###', '')
        jsonurl=url.split('###')[0]+"?page="+page+"&limit=50&query="+nextQuery
    elif not '###' in url and query != "":
        jsonurl=url+"?page="+page+"&limit=50&query="+query
    else:
        jsonurl=url+"?page="+page+"&limit=50"
    content=geturl(jsonurl)
    struktur2 = json.loads(content)
    for element in struktur2["data"]:
        videourl=element["url"].encode("utf-8")
        title=element["title"].encode("utf-8")
        try:
            subtitle=element["subtitle"].encode("utf-8")
            title=title+ " - "+subtitle
        except: pass
        try: desc=element["description"].encode("utf-8")
        except: desc=""
        bild=element["images"]["landscape"]["resolutions"][-1]["url"].encode("utf-8")
        duration=element["duration"]
        if "/sendungen/" in newUrl.lower() or "/emissions/" in newUrl.lower():
            addDir(title,videourl,"videoliste",bild,desc=desc)
        else:
            if duration and duration != "" and duration != "0":
                addLink(title,videourl,"playvideo",bild,duration=duration,desc=desc)
    try:
        debug("NextPage try:")
        nextpage=struktur2["nextPage"]
        debug(nextpage)
        debug("Endnext")
        if nextpage.startswith("http"):
            if "search" in nextpage.lower():
                addDir("Next Page >>>",url+'###'+query,"abiszetc",icon,page=int(page)+1)
            else:
                addDir("Next Page >>>",url,"abiszetc",icon,page=int(page)+1)
    except: pass
    xbmcplugin.endOfDirectory(addon_handle)

def live():
    addLink("Arte HD","https://artelive-lh.akamaihd.net/i/artelive_de@393591/index_1_av-p.m3u8","playlive",icon)
    addLink("ARTE Event 1","https://arteevent01-lh.akamaihd.net/i/arte_event01@395110/index_1_av-p.m3u8","playlive",icon)
    addLink("ARTE Event 2","https://arteevent02-lh.akamaihd.net/i/arte_event02@308866/index_1_av-p.m3u8","playlive",icon)
    addLink("ARTE Event 3","https://arteevent03-lh.akamaihd.net/i/arte_event03@305298/index_1_av-p.m3u8","playlive",icon)
    addLink("ARTE Event 4","https://arteevent04-lh.akamaihd.net/i/arte_event04@308879/index_1_av-p.m3u8","playlive",icon)
    xbmcplugin.endOfDirectory(addon_handle)

def playlive(url):
    listitem = xbmcgui.ListItem(path=url)  
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)

def datummenu():
    if country=="de":
        addDir("Zukunft","-30","datumselect",icon)
        addDir("Vergangenheit","30","datumselect",icon)
    elif country=="fr":
        addDir("Avenir","-30","datumselect",icon)
        addDir("Passé","30","datumselect",icon)
    xbmcplugin.endOfDirectory(addon_handle)
    
def datumselect(wert):
    if int(wert)<0:
        start=0
        end=int(wert)
        sprung=-1
    elif int(wert)>0:
        start=0
        end=int(wert)
        sprung=1
    for i in range(start,end,sprung):
        title=(datetime.date.today()-datetime.timedelta(days=i)).strftime("%d/%m/%Y")
        suche=(datetime.date.today()-datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        addDir(title,suche,"showday",icon)
    xbmcplugin.endOfDirectory(addon_handle)

def showday(tag):
    url=ARTE_apiURL+"/pages/"+country+"/web/TV_GUIDE/?day="+tag
    content=geturl(url)
    struktur = json.loads(content)
    for element in struktur["zones"][-1]["data"]:
        videourl=element["url"].encode("utf-8")
        title=element["title"].encode("utf-8")
        try:
            subtitle=element["subtitle"].encode("utf-8")
            title=title+ " - "+subtitle
        except: pass
        try: desc=element["fullDescription"].encode("utf-8")
        except: desc=""
        bild=element["images"]["landscape"]["resolutions"][-1]["url"].encode("utf-8")
        duration=element["duration"]
        broadcastDates=element["broadcastDates"][0]
        #"2018-02-28T04:00:00Z"
        datetime_object = datetime.datetime.strptime(broadcastDates, '%Y-%m-%dT%H:%M:%SZ')
        wann="[COLOR orangered]"+datetime_object.strftime("%H:%M")+"[/COLOR]"
        debug("-----------------------")
        debug(wann)
        stickers=str(element["stickers"])
        if "PLAYABLE" in stickers:
            addLink(wann+"  "+title,videourl,"playvideo",bild,duration=duration,desc=desc)
    xbmcplugin.endOfDirectory(addon_handle)

def listVideos_Time():
    if country=="de":
        addDir("Videos 0 bis 5 Min.",baseURL+country+"/videos/5-min/","abiszetc",icon)
        addDir("Videos 5 bis 15 Min.",baseURL+country+"/videos/15-min/","abiszetc",icon)
        addDir("Videos 15 bis 60 Min.",baseURL+country+"/videos/1-stunde/","abiszetc",icon)
        addDir("Videos > 60 Min.",baseURL+country+"/videos/viel-zeit/","abiszetc",icon)
    elif country=="fr":
        addDir("Vidéos 0 à 5 min.",baseURL+country+"/videos/5-min/","abiszetc",icon)
        addDir("Vidéos 5 à 15 min.",baseURL+country+"/videos/15-min/","abiszetc",icon)
        addDir("Vidéos 15 à 60 min.",baseURL+country+"/videos/1-heure/","abiszetc",icon)
        addDir("Vidéos > 60 min.",baseURL+country+"/videos/beaucoup/","abiszetc",icon)
    xbmcplugin.endOfDirectory(addon_handle)

def SearchArte():
    #https://www.arte.tv/guide/api/api/zones/de/web/listing_SEARCH?page=1&limit=20&query=filme
    someReceived = False
    word = xbmcgui.Dialog().input("Search ARTE ...", type=xbmcgui.INPUT_ALPHANUM)
    word = urllib.quote(word, safe='')
    if word == "": return
    title_SEARCH = baseURL+country+"/search/?q="+word
    debug("SearchArte - Url: "+title_SEARCH)
    try:
        result = geturl(title_SEARCH)
        content = re.findall('<span class="font-size-l">(.*?)</span>',result,re.S)[0]
    except: content = "OKAY"
    debug("SearchArte - Result: "+content)
    if content == "OKAY":
        abiszetc(title_SEARCH,query=word)
        someReceived = True
    elif ("keine daten verfügbar" in content.lower() or "aucun résultat" in content.lower() or not someReceived):
        if country=="de":
            addDir("[B][COLOR FFFF456E]!!! Zu dem gesuchten Begriff wurden KEINE Ergebnisse gefunden !!![/COLOR][/B]", word, "",icon)
        elif country=="fr":
            addDir("[B][COLOR FFFF456E]!!! Aucun résultat n'a été trouvé pour le terme recherché !!![/COLOR][/B]", word, "",icon)
    else: pass
    xbmcplugin.endOfDirectory(addon_handle)

if mode is '':
    menu()
else:
    if mode == 'liste':
        liste()
    # Wenn Settings ausgewählt wurde
    if mode == 'Settings':
        addon.openSettings()
    # Wenn Kategory ausgewählt wurde
    if mode == 'playvideo':
        playvideo(url)
    if mode == 'subrubrik':
        subrubrik(url)
    if mode == 'videoliste':
        videoliste(url,page)
    if mode == 'menu':
        menu()  
    if mode == 'live':
        live()
    if mode == 'playlive':
        playlive(url)
    if mode == 'datumselect':
        datumselect(url)
    if mode == 'showday':
        showday(url)
    if mode == 'datummenu':
        datummenu()
    if mode == 'abiszetc':
        abiszetc(url,page,query)
    if mode == 'listVideos_Time':
        listVideos_Time()
    if mode == 'SearchArte':
        SearchArte()