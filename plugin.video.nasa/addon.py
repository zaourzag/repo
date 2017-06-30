#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2012 Tristan Fischer (sphere@dersphere.de)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from xbmcswift2 import Plugin
import urllib,urllib2,re,xbmcgui,xbmcplugin
from bs4 import BeautifulSoup

pluginhandle = int(sys.argv[1])

def parameters_string_to_dict(parameters):
  paramDict = {}
  if parameters:
    paramPairs = parameters[1:].split("&")
    for paramsPair in paramPairs:
      paramSplits = paramsPair.split('=')
      if (len(paramSplits)) == 2:
        paramDict[paramSplits[0]] = paramSplits[1]
  return paramDict
   
  
def addDir(name, url, mode, iconimage, desc=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  if useThumbAsFanart:
    if not iconimage or iconimage==icon:
      iconimage = defaultBackground    
    liz.setArt({ 'fanart': iconimage })
  else:
    liz.setArt({ 'fanart': defaultBackground })    
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="",artist_id="",genre="",shortname="",production_year=0,zeit=0,liedid=0):    
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage="", thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre,"Sorttitle":shortname,"Dateadded":zeit,"year":production_year })
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setArt({ 'fanart': iconimage })   
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok
  
STRINGS = {
    'page': 30001,
    'streams': 30100,
    'videos': 30101,
    'vodcasts': 30103,
    'search': 30200,
    'title': 30201
}


YOUTUBE_CHANNELS = (
    {
        'name': 'NASA Main',
        'logo': 'nasa.jpg',
        'channel_id': 'UCLA_DiR1FfKNvjuUpBHmylQ',
        'user': 'NASAtelevision',
    }, {
        'name': 'NASA Goddard',
        'logo': 'goddard.jpg',
        'channel_id': 'UCAY-SMFNfynqz1bdoaV8BeQ',
        'user': 'NASAexplorer',
    }, {
        'name': 'NASA Jet Propulsion Laboratory',
        'logo': 'jpl.jpg',
        'channel_id': 'UCryGec9PdUCLjpJW2mgCuLw',
        'user': 'JPLnews',
    }, {
        'name': 'NASA Kennedy Space Center',
        'logo': 'nasa.jpg',
        'channel_id': 'UCjJtr2fFcUp6yljzJOzpHUg',
        'user': 'NASAKennedy',
    }, {
        'name': 'Hubble Space Telescope',
        'logo': 'hubble.jpg',
        'channel_id': 'UCqvjEkH_41m4DYaoNQwk4Bw',
        'user': 'HubbleSiteChannel',
    },
)

YOUTUBE_URL ='plugin://plugin.video.youtube/channel/%s/?page=1'

plugin = Plugin()


@plugin.route('/')
def show_root_menu():
    items = [
        {'label': _('streams'),
         'path': "plugin://plugin.video.nasa?mode=mainmenu"},
        {'label': _('videos'),
         'path': plugin.url_for('show_channels')},
    ]
    return plugin.finish(items)

    

@plugin.route('/streams/')
def show_streams():
    items = [{
        'label': stream['title'],
        'thumbnail': get_logo(stream['logo']),
        'path': "plugin://plugin.video.nasa?mode=play&url="+urllib.quote_plus(stream['stream_url']),
        'is_playable': True,
    } for stream in STATIC_STREAMS]
    return plugin.finish(items)


@plugin.route('/channels/')
def show_channels():
    items = [{
        'label': channel['name'],
        'thumbnail': get_logo(channel['logo']),
        'path': YOUTUBE_URL % channel['channel_id'],
    } for channel in YOUTUBE_CHANNELS]
    return plugin.finish(items)

def get_logo(logo):
    addon_id = plugin._addon.getAddonInfo('id')
    return 'special://home/addons/%s/resources/media/%s' % (addon_id, logo)


def _(string_id):
    if string_id in STRINGS:
        return plugin.get_string(STRINGS[string_id])
    else:
        plugin.log.warning('String is missing: %s' % string_id)
        return string_id


def getUrl(url,data="x"):    
        print("#"+url+"#")            
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        userAgent = "Dalvik/2.1.0 (Linux; U; Android 5.0;)"
        opener.addheaders = [('User-Agent', userAgent)]
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #print e.code   
             cc=e.read()  
             struktur = json.loads(cc)  
             error=struktur["errors"][0] 
             error=unicode(error).encode("utf-8")             
             dialog = xbmcgui.Dialog()
             nr=dialog.ok("Error", error)
             return ""
             
        opener.close()
        return content


def log(text):
    plugin.log.info(text)
def mainmenu():
    url="http://www.ustream.tv/nasahdtv"
    content=getUrl(url)
    htmlPage = BeautifulSoup(content, 'html.parser')        
    elemente=htmlPage.findAll("a",{"class" :"channel"})
    for element in elemente: 
      print("+++++"+element.span.text)    
      if not "OFF AIR" in element.span.text:
          img=element.find("img")["src"]
          link=element["href"]
          if not "http" in link:
            link="http://www.ustream.tv/"+link
          title=element.h3.string
          if not "LSP -" in title:            
            addLink(title, link, 'play', img)    
    xbmcplugin.endOfDirectory(pluginhandle)          
    
def play(url):
  print("PLAY :"+url)
  content=getUrl(url)
  urlv=re.compile('"hls":"(.+?)"', re.DOTALL).findall(content)[0]
  urlv=urlv.replace("\/","/")
  content=getUrl(urlv)
  urlv=re.compile('(http[^\n]+)', re.DOTALL).findall(content)[0]
  listitem = xbmcgui.ListItem(path=urlv)   
  addon_handle = int(sys.argv[1])  
  xbmcplugin.setResolvedUrl(addon_handle, True, listitem)

if __name__ == '__main__':
  params = parameters_string_to_dict(sys.argv[2])
  mode = urllib.unquote_plus(params.get('mode', ''))
  url = urllib.unquote_plus(params.get('url', ''))
  if mode=="play":
     play(url)
  elif mode=="mainmenu":
      mainmenu() 
  else:
    plugin.run()
