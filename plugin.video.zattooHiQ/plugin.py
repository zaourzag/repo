# coding=utf-8
#
#    copyright (C) 2017 Steffen Rolapp (github@rolapp.de)
#
#    based on ZattooBoxExtended by Daniel Griner (griner.ch@gmail.com) License under GPL
#    based on ZattooBox by Pascal Nançoz (nancpasc@gmail.com) Licence under BSD 2 clause
#
#    This file is part of zattooHiQ
#
#    zattooHiQ is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    zattooHiQ is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with zattooHiQ.  If not, see <http://www.gnu.org/licenses/>.
#


REMOTE_DBG = False
if REMOTE_DBG:
  try:
    import pysrc.pydevd as pydevd
    pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)
  except ImportError:
    sys.stderr.write("Error: You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
    sys.exit(1)


import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, urlparse,  os
import  time, datetime, threading

from resources.zattooDB import ZattooDB
from resources.library import library
from resources.guiactions import *

#import resources.MyFont as MyFont
#MyFont.addFont( "zattoo45" , "NotoSans-Bold.ttf" , "45", style="bold") # style and aspect are optional.


__addon__ = xbmcaddon.Addon()
__addonId__=__addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')

_timezone_ = int(__addon__.getSetting('time_offset'))*60*-60 #-time.altzone

if __addon__.getSetting('show_favourites')=='true':_listMode_ ='favourites'
else: _listMode_ ='all'

_channelList_=[]
_zattooDB_=ZattooDB()
_library_=library()

_umlaut_ = {ord(u'ä'): u'ae', ord(u'ö'): u'oe', ord(u'ü'): u'ue', ord(u'ß'): u'ss'}

localString = __addon__.getLocalizedString
local = xbmc.getLocalizedString

SWISS = __addon__.getSetting('swiss')
accountData=_zattooDB_.zapi.get_accountData()
premiumUser=accountData['account']['subscriptions']!=[]

DASH = __addon__.getSetting('dash')=='true'


if SWISS=="true": xbmc.executebuiltin( "Skin.SetBool(%s)" %'swiss')
else: xbmc.executebuiltin( "Skin.Reset(%s)" %'swiss')

if premiumUser: xbmc.executebuiltin( "Skin.SetBool(%s)" %'hiq')
else: xbmc.executebuiltin( "Skin.Reset(%s)" %'hiq')

from tzlocal import get_localzone
import pytz
try:
  tz = get_localzone()
  offset=tz.utcoffset(datetime.datetime.now()).total_seconds()
  _timezone_=int(offset)
except:
  _timezone_ = int(__addon__.getSetting('time_offset'))*60*-60 #-time.altzone


def build_directoryContent(content, addon_handle, cache=True, root=False, con='movies'):
  fanart=__addon__.getAddonInfo('path') + '/fanart.jpg'
  xbmcplugin.setContent(addon_handle, con)
  xbmcplugin.setPluginFanart(addon_handle, fanart)
  for record in content:
    record['thumbnail'] = record.get('thumbnail', fanart)
    record['image'] = record.get('image', "")

    li = xbmcgui.ListItem(record['title'], iconImage=record['image'])
    li.setInfo(type='Video', infoLabels = record)
    li.setArt({'icon': record['image'], 'thumb': record['image'], 'poster': record['thumbnail'], 'banner': record['thumbnail']})
    li.setProperty('Fanart_Image', record['thumbnail'])
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=record['url'], listitem=li, isFolder=record['isFolder'])

  xbmcplugin.endOfDirectory(addon_handle, True, root, cache)

  '''
    # set missing properties
    record['image'] = record.get('image', "")
    record['plot'] = record.get('plot', "")
    record['thumbnail'] = record.get('thumbnail', "")
    record['selected'] = record.get('selected', False)
    record['genre'] = record.get('genre', "")
    record['year'] = record.get('year', " ")
    record['country'] = record.get('country', "")
    record['category'] = record.get('category', "")

    li = xbmcgui.ListItem(record['title'], iconImage=record['image'])
    li.setInfo('video', {'plot':record['plot'] })

    li.setInfo('video', {'genre':record['genre'] })
    li.setInfo('video', {'year':record['year'] })
    li.setInfo('video', {'country':record['country']})
    li.setInfo('video', {'category':record['category']})
    li.setProperty('fanart_image', record['thumbnail'])
    li.select(record['selected'])

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=record['url'], listitem=li, isFolder=record['isFolder'])

  xbmcplugin.endOfDirectory(addon_handle, True, root, cache)
  '''
    
def build_root(addon_uri, addon_handle):
  import urllib

  # check if settings are set
  name = __addon__.getSetting('username')
  if name == '':
    # show home window, zattooHiQ settings and quit
    xbmc.executebuiltin('ActivateWindow(10000)')
    xbmcgui.Dialog().ok(__addonname__, localString(31902))
    __addon__.openSettings()
    sys.exit()

  #play channel on open addon
  if ((xbmcgui.Window(10000).getProperty('ZBEplayOnStart')!='false') and (not xbmc.Player().isPlaying()) and (__addon__.getSetting('start_liveTV')=='true')):
    channeltitle = __addon__.getSetting('start_channel')
    if channeltitle=="lastChannel": channelid=_zattooDB_.get_playing()['channel']
    else: channelid = _zattooDB_.get_channelid(channeltitle)
    resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/watch', {'cid': channelid, 'stream_type': 'hls', 'maxrate':__addon__.getSetting('max_bandwidth')})
    xbmc.Player().play(resultData['stream']['watch_urls'][0]['url'])
    streamsList = []
    for stream in resultData['stream']['watch_urls']: streamsList.append(stream['url'])
    streamsList = '|'.join(streamsList)
    _zattooDB_.set_playing(channelid, streamsList, 0)
    makeZattooGUI()
    xbmcgui.Window(10000).setProperty('ZBEplayOnStart', 'false')


  iconPath = __addon__.getAddonInfo('path') + '/icon.png'
  if _listMode_ == 'all': listTitle = localString(31100)
  else: listTitle = localString(31101)

  content = [
    #{'title': '[B][COLOR blue]' + listTitle + '[/COLOR][/B]', 'image': iconPath, 'isFolder': False, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'switchlist'})},
    {'title': '[COLOR ff00ff00]'+localString(31099)+'[/COLOR]', 'image': iconPath, 'isFolder': False, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'popular'})},
    {'title': localString(31103), 'image': iconPath, 'isFolder': False, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'preview'})},
    {'title': localString(31104), 'image': iconPath, 'isFolder': False, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'epg'})},
    {'title': localString(31102), 'image': iconPath, 'isFolder': True, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'channellist'})},
    {'title': localString(31105), 'image': iconPath, 'isFolder': True, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'search'})},
    {'title': localString(31106), 'image': iconPath, 'isFolder': True, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'recordings'})},
#    {'title': localString(31023), 'image': iconPath, 'isFolder': True, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'reloadDB'})},
    {'title': '[COLOR ff888888]' + localString(31107) + '[/COLOR]', 'image': iconPath, 'isFolder': False, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'show_settings'})},
    ]
  build_directoryContent(content, addon_handle, True, False, 'files')

  #update db
  _zattooDB_.updateChannels()
  _zattooDB_.updateProgram()


def build_channelsList(addon_uri, addon_handle):
  import urllib
  channels = _zattooDB_.getChannelList(_listMode_ == 'favourites')
  li = False
  if channels is not None:
    # get currently playing shows
    if __addon__.getSetting('dbonstart') == 'true': li = True
    program = _zattooDB_.getPrograms(channels, li)
    content = []
    # time of chanellist creation
    #content.append({'title': '[B][COLOR blue]' + time.strftime("%H:%M:%S") +'[/B][/COLOR]', 'isFolder': False, 'url':''})

    # get last watched channel
    playing = _zattooDB_.get_playing()

    nr=1
    for chan in channels['index']:
      #prog=program[chan]
      prog = {}
      for search in program:
        if search['channel'] == chan:
          prog = search
          break
      try:
        start = prog.get('start_date','').strftime('%H:%M')
        end = prog.get('end_date','').strftime('%H:%M')
        startend = '[COLOR yellow]'+start+"-"+end+'[/COLOR]'
      except AttributeError:
        startend = ''
      if len(str(nr)) == 1:
        chnr = '  '+str(nr)
      else: chnr = str(nr)
      yy = prog.get('year','')
      #if yy is None: yy=''
      content.append({
        'title': '[COLOR green]'+chnr+'[/COLOR]'+'  '+channels[chan]['title'] + ' - ' + prog.get('title', '')+ '  '+startend,
        'image': channels[chan]['logo'],
        'thumbnail': prog.get('image_small', ''),
        'genre': prog.get('genre',''),
        'plot':  prog.get('description_long', ''),
        #'plot': prog.get('genre','')+"  "+str(prog.get('year','')),
        'year': yy,
        'category': prog.get('category',''),
        'country': prog.get('country',''),
        'isFolder': False,
        'url': addon_uri + '?' + urllib.urlencode({'mode': 'watch_c', 'id': channels[chan]['id']}),
        'selected' : channels[chan]['id'] == playing['channel']
      })
      nr+=1

  build_directoryContent(content, addon_handle, False)



def build_recordingsList(addon_uri, addon_handle):
  import urllib
  
  resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/playlist', None)
  if resultData is None: return
  for record in resultData['recordings']:
    showInfo=_zattooDB_.getShowInfo(record['program_id'])
    #mark if show is future, running or finished
    start = int(time.mktime(time.strptime(record['start'], "%Y-%m-%dT%H:%M:%SZ"))) + _timezone_  # local timestamp
    end = int(time.mktime(time.strptime(record['end'], "%Y-%m-%dT%H:%M:%SZ"))) + _timezone_  # local timestamp
    position = int(time.mktime(time.strptime(record['position'], "%Y-%m-%dT%H:%M:%SZ"))) + _timezone_  # local timestamp
    now = time.time()
    color='red'
    if (now>start): color='orange'
    if (now>end): color='green'

    label=datetime.datetime.fromtimestamp(start).strftime('%d.%m.%Y. %H:%M')+' ' # NEW changed - by Samoth
    if record['episode_title']:
      label+='[COLOR '+color+']'+record['title']+'[/COLOR]: '+record['episode_title']
      meta = {'title':record['episode_title'], 'season':1, 'episode':1, 'tvshowtitle':record['title']}
    else:
      label+='[COLOR '+color+']'+record['title']+'[/COLOR]'
      meta = {'title':record['title']}
    if showInfo == "NONE": continue
    label+=' ('+showInfo['channel_name']+')'
    director=''
    cast=[]
    for person in showInfo['credits']:
      if person['role']=='director': director=person['person']
      else: cast.append(person['person'])

    meta.update({'title':label,'year':showInfo['year'], 'plot':showInfo['description'], 'country':showInfo['description'],'director':director, 'cast':cast, 'genre':', '.join(showInfo['genres'])  })

    li = xbmcgui.ListItem(label)
    li.setInfo('video',meta)
    li.setThumbnailImage(record['image_url'])
    li.setArt({'thumb':record['image_url'], 'fanart':record['image_url'], 'landscape':record['image_url']})
    #li.setProperty('IsPlayable', 'true') #is played by myPlayer
    try:
      series=record['tv_series_id']
    except:
      series = 'None'
    contextMenuItems = []
    if series != 'None':
      contextMenuItems.append((localString(31925),'RunPlugin("plugin://'+__addonId__+'/?mode=remove_series&recording_id='+str(record['id'])+'&series='+str(series)+'")',))
    contextMenuItems.append((localString(31921), 'RunPlugin("plugin://'+__addonId__+'/?mode=remove_recording&recording_id='+str(record['id'])+'")'))
    li.addContextMenuItems(contextMenuItems, replaceItems=True)

    xbmcplugin.addDirectoryItem(
      handle=addon_handle,
      url=addon_uri + '?' + urllib.urlencode({'mode': 'watch_r', 'id': record['id'], 'starttime':start, 'position':position}),
      listitem=li,
      isFolder=False
    )
  xbmcplugin.endOfDirectory(addon_handle)
  xbmcplugin.setContent(addon_handle, 'movies')
  xbmcplugin.addSortMethod(addon_handle, 2)
  xbmcplugin.addSortMethod(addon_handle, 9)

def watch_recording(addon_uri, addon_handle, recording_id, startTime, position):
  #if xbmc.Player().isPlaying(): return
  startTime=int(startTime)
  position=int(position)
  max_bandwidth = __addon__.getSetting('max_bandwidth')
  if DASH: stream_type='dash'
  else: stream_type='hls'
  params = {'recording_id': recording_id, 'stream_type': stream_type, 'maxrate':max_bandwidth}
  resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/watch', params)
  if resultData is not None:
    streams = resultData['stream']['watch_urls']

    if len(streams)==0:
      xbmcgui.Dialog().notification("ERROR", "NO STREAM FOUND, CHECK SETTINGS!", channelInfo['logo'], 5000, False)
      return
    elif len(streams) > 1 and  __addon__.getSetting('audio_stream') == 'B' and streams[1]['audio_channel'] == 'B': streamNr = 1
    else: streamNr = 0
    
    li = xbmcgui.ListItem()
    if DASH:
        li.setProperty('inputstreamaddon', 'inputstream.adaptive')
        li.setProperty('inputstream.adaptive.manifest_type', 'mpd')

    #xbmcplugin.setResolvedUrl(addon_handle, True, li)
    prePadding=resultData['stream']['padding']['pre']
    positionSkip=0
    if (startTime!=position):
        pos=str(datetime.timedelta(seconds=(position-startTime)))
        ret = xbmcgui.Dialog().yesno('Zattoo Position', __addon__.getLocalizedString(31306)+'\n'+pos,'' , __addon__.getLocalizedString(31307))
        if ret:positionSkip= position-startTime

    player= myPlayer(prePadding+positionSkip)
    player.play(streams[streamNr]['url'], li)
    while (player.playing):
        try: pos=player.getTime()
        except: pass
        xbmc.sleep(100) 

    #send watched position to zattoo
    zStoptime=datetime.datetime.fromtimestamp(startTime+round(pos)-prePadding - _timezone_ ).strftime("%Y-%m-%dT%H:%M:%SZ")
    resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/playlist/recording', {'recording_id': recording_id, 'position': zStoptime})
  

def setup_recording(program_id):
  #print('RECORDING: '+program_id)
  params = {'program_id': program_id}
  resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/playlist/program', params)
  xbmcgui.Dialog().ok(__addonname__, __addon__.getLocalizedString(31903))
  _library_.make_library()  # NEW added - by Samoth


def delete_recording(recording_id):
  params = {'recording_id': recording_id}
  folder=__addon__.getSetting('library_dir') # NEW added - by Samoth
  if folder: # NEW added - by Samoth
    _library_.delete_entry_from_library(str(recording_id)) # NEW added - by Samoth
  resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/playlist/remove', params)
  xbmc.executebuiltin('Container.Refresh')
# times in local timestamps

def delete_series(recording_id, series):
  params = {'recording_id': recording_id, 'tv_series_id':series, 'remove_recording':'true'}
  folder=__addon__.getSetting('library_dir') # NEW added - by Samoth
  if folder: # NEW added - by Samoth
    _library_.delete_entry_from_library(str(recording_id)) # NEW added - by Samoth
  resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/series_recording/remove', params)
  xbmc.executebuiltin('Container.Refresh')

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import re, unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = unicode(re.sub('[-\s]+', '-', value))
    return value


def watch_channel(channel_id, start, end, showID="", restart=False, showOSD=False):
  #print('WATCH: '+channel_id+' st:'+str(start)+' en:'+str(end))
  #new ZattooDB instance because this is called from thread-timer on channel-nr input (sql connection doesn't work)
  _zattooDB_=ZattooDB()
  
  #selected currently playing live TV
  playing=_zattooDB_.get_playing()
  if (xbmc.Player().isPlaying() and channel_id == playing['channel'] and start=='0'):
    xbmc.executebuiltin("Action(FullScreen)")
    makeZattooGUI()
    return

  # (64 150 300) 600 900 1500 3000 5000
  max_bandwidth = __addon__.getSetting('max_bandwidth')

  if DASH: stream_type='dash'
  else:  stream_type='hls'

  if restart: params = {'stream_type': stream_type}
  elif start == '0': params = {'cid': channel_id, 'stream_type': stream_type, 'maxrate':max_bandwidth}
  else:
    zStart = datetime.datetime.fromtimestamp(int(start) - _timezone_ ).strftime("%Y-%m-%dT%H:%M:%SZ")  #5min zattoo skips back
    zEnd = datetime.datetime.fromtimestamp(int(end) - _timezone_ ).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {'cid': channel_id, 'stream_type': stream_type, 'start':zStart, 'end':zEnd, 'maxrate':max_bandwidth }

  channelInfo = _zattooDB_.get_channelInfo(channel_id)

  if restart: resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/watch/selective_recall/'+channel_id+'/'+showID, params)
  else: resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/watch',params)
  print 'ResultData ' +str(params)
  if resultData is None:
    xbmcgui.Dialog().notification("ERROR", "NO ZAPI RESULT", channelInfo['logo'], 5000, False)
    return

  streams = resultData['stream']['watch_urls']
  if len(streams)==0:
    xbmcgui.Dialog().notification("ERROR", "NO STREAM FOUND, CHECK SETTINGS!", channelInfo['logo'], 5000, False)
    return
  # change stream if settings are set
  streamNr = 0
  if len(streams) > 1 and  __addon__.getSetting('audio_stream') == 'B' and streams[1]['audio_channel'] == 'B': streamNr = 1
  xbmcgui.Window(10000).setProperty('playstream', streams[streamNr]['url'])

  # save currently playing
  streamsList = []
  for stream in resultData['stream']['watch_urls']: streamsList.append(stream['url'])
  streamsList = '|'.join(streamsList)
  _zattooDB_.set_playing(channel_id, streamsList, streamNr)

  #xbmc.Player().play(streams[streamNr]['url'], xbmcgui.ListItem(channel_id))
  #return


  #play liveTV: info is created in OSD
  if (start=='0'):
    listitem = xbmcgui.ListItem(channel_id)
    if DASH:
      listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
      listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    xbmc.Player().play(streams[streamNr]['url'], listitem)
    makeZattooGUI(showOSD)
    return

  #12005:fullscreenvideo
  #if (xbmcgui.getCurrentWindowId()!=12005):xbmc.executebuiltin("Action(FullScreen)")

  #make Info
  startTime = datetime.datetime.fromtimestamp(int(start))
  endTime = datetime.datetime.fromtimestamp(int(end))
  program = _zattooDB_.getPrograms({'index':[channel_id]}, True, startTime, endTime)

  listitem = xbmcgui.ListItem(channel_id)
  if program:
    program = program[0]
    heading = ('[B]' + channelInfo['title'] + '[/B] ').translate(_umlaut_) + '  ' + program['start_date'].strftime('%H:%M') + '-' + program['end_date'].strftime('%H:%M')
    xbmcgui.Dialog().notification(heading, program['title'].translate(_umlaut_), channelInfo['logo'], 5000, False)

    #set info for recall
    listitem.setThumbnailImage(program['image_small'])
    meta = {'title': program['title'], 'season' : 'S', 'episode': streamNr, 'tvshowtitle': channelInfo['title']+ ', ' + program['start_date'].strftime('%A %H:%M') + '-' + program['end_date'].strftime('%H:%M'), 'premiered' :'premiered', 'duration' : '20', 'rating': 'rating', 'director': 'director', 'writer': 'writer', 'plot': program['description_long']}
    listitem.setInfo(type="Video", infoLabels = meta)
    listitem.setArt({ 'poster': program['image_small'], 'logo' : channelInfo['logo'] })

  if DASH:
    listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')

  player= myPlayer(290)
  player.startTime=startTime
  player.play(streams[streamNr]['url'], listitem)
  while (player.playing):xbmc.sleep(100)
      
def skip_channel(skipDir):
  #new ZattooDB instance because this is called from thread-timer on channel-nr input (sql connection doesn't work)
  _zattooDB_=ZattooDB()

  channelList = _zattooDB_.getChannelList(_listMode_ == 'favourites')
  currentChannel = _zattooDB_.get_playing()['channel']
  nr=channelList[currentChannel]['nr']
  nr += skipDir

  if nr<len(channelList) and nr>-1:
    watch_channel(channelList['index'][nr], '0', '0')
    return nr
  else:
    xbmc.executebuiltin('XBMC.Action(FullScreen)')
    return channelList[currentChannel]['nr']

def  toggle_channel():
  _zattooDB_=ZattooDB()
  toggleChannel=xbmcgui.Window(10000).getProperty('toggleChannel')
  playing=_zattooDB_.get_playing()
  xbmcgui.Window(10000).setProperty('toggleChannel', playing['channel'])
      
  if toggleChannel=="": xbmc.executebuiltin("Action(Back)") #go back to channel selector
  else:
    watch_channel(toggleChannel, '0', '0')
    channelList = _zattooDB_.getChannelList(_listMode_ == 'favourites')
    nr=channelList[toggleChannel]['nr']
    return nr


def change_stream(dir):
  playing = _zattooDB_.get_playing()
  streams = playing['streams'].split('|')
  streamNr = (playing['current_stream'] + dir) % len(streams)

  _zattooDB_.set_currentStream(streamNr)

  channelInfo = _zattooDB_.get_channelInfo(playing['channel'])
  channel_id=_zattooDB_.get_playing()['channel']
  program = _zattooDB_.getPrograms({'index':[channel_id]}, True)[0]

  title = channelInfo['title'] + " (stream" + str(streamNr) + ")"
  listitem = xbmcgui.ListItem(channelInfo['title'], thumbnailImage=channelInfo['logo'])
  listitem.setInfo('video', {'Title': title, 'plot':program['description_long']})

  xbmc.Player().play(streams[streamNr], listitem)
  xbmcgui.Dialog().notification(title.translate(_umlaut_), program['title'].translate(_umlaut_), channelInfo['logo'], 5000, False)

def search_show(addon_uri, addon_handle):
  import urllib
  input = xbmcgui.Dialog().input(__addon__.getLocalizedString(31200), type=xbmcgui.INPUT_ALPHANUM)
  if input == '': return
  resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/program/search?query=' + input, None)

  if resultData is None:
    build_directoryContent([{'title': __addon__.getLocalizedString(31203), 'isFolder': False, 'url':''}], addon_handle)
    return

  programs = sorted(resultData['programs'], key=lambda prog: (prog['cid'], prog['start']))

  channels = _zattooDB_.getChannelList(False)
  '''
  chanDict = {}
  for chan in channels: chanDict[chan['id']] = chan
  channels = chanDict
  '''

  recall_shows = []
  record_shows = []
  now = time.time()  # datetime.datetime.now()
  for program in programs:
    start = int(time.mktime(time.strptime(program['start'], "%Y-%m-%dT%H:%M:%SZ"))) + _timezone_  # local timestamp
    startLocal = time.localtime(start)  # local timetuple
    end = int(time.mktime(time.strptime(program['end'], "%Y-%m-%dT%H:%M:%SZ"))) + _timezone_  # local timestamp

    if program.get('episode_title', '') is not None:episode_title=program.get('episode_title', '')
    else:episode_title=''

    item = {
        'title': time.strftime("%d.%m. %H:%M ", startLocal) + program.get('cid', '') + ': ' + program.get('title', '') + ' - ' + episode_title,
        'image': channels[program['cid']]['logo'],
         'thumbnail': program.get('image_url', ''),
        'plot':  program.get('episode_title', ''),
        'isFolder': False
      }

    startLocal = time.mktime(startLocal)  # local timestamp
    if startLocal < now:
      item['url'] = addon_uri + '?' + urllib.urlencode({'mode': 'watch_c', 'id': program['cid'], 'start':str(start + 10), 'end':str(end)})
      recall_shows.append(item)
    else:
      item['url'] = addon_uri + '?' + urllib.urlencode({'mode': 'record_p', 'program_id': program['id']})
      record_shows.append(item)

  content = []
  content.append({'title': '[B][COLOR blue]' + __addon__.getLocalizedString(31201) + '[/B][/COLOR]', 'isFolder': False, 'url':''})
  for item in recall_shows: content.append(item)
  content.append({'title': '[B][COLOR blue]' + __addon__.getLocalizedString(31202) + '[/B][/COLOR]', 'isFolder': False, 'url':''})
  for item in record_shows: content.append(item)
  build_directoryContent(content, addon_handle)


def showPreview(popularList=''):
  from resources.channelspreview import ChannelsPreview
  preview = ChannelsPreview()
  if popularList=='popular': preview.createPreview('popular')
  else: preview.createPreview(_listMode_ == 'favourites')
  preview.show() #doModal()
  while xbmcgui.Window(10000).getProperty('zattoo_runningView')=="preview": xbmc.sleep(10)
  del preview

def showEpg():
  from resources.epg.epg import EPG
  currentChannel = _zattooDB_.get_playing()['channel']
  channelList = _zattooDB_.getChannelList(_listMode_ == 'favourites')
  currentNr=channelList[currentChannel]['nr']
  accountData=_zattooDB_.zapi.get_accountData()
  premiumUser=accountData['account']['subscriptions']!=[]
  epg = EPG(currentNr, premiumUser)
  epg.loadChannels(_listMode_ == 'favourites')
  epg.show() #doModal()
  while xbmcgui.Window(10000).getProperty('zattoo_runningView')=="epg": xbmc.sleep(10)
  del epg

def selectStartChannel():
  channels = _zattooDB_.getChannelList(_listMode_ == 'favourites')
  chanList = [localString(310095)]
  for chan in channels['index']: chanList.append(channels[chan]['title'])
  dialog=xbmcgui.Dialog()
  ret = dialog.select(localString(31009), chanList)
  if ret==-1: return
  __addon__.setSetting('start_liveTV', 'true')
  if ret==0: __addon__.setSetting('start_channel', 'lastChannel')
  else: __addon__.setSetting('start_channel', chanList[ret])
 

def editKeyMap():
    cmds=['OSD', 'prevChan', 'nextChan', 'toggleChan', 'audio', 'pause', 'stop', 'record', 'Teletext', 'Preview', 'List', 'EPG']
    cmdsText=[]
    nr=0
    for cmd in cmds:
        cmdsText.append(localString(32010+int(nr)))
        nr+=1
    dialog=xbmcgui.Dialog()
    cmd = dialog.select(localString(32000), cmdsText)
    if cmd==-1:return

    newkey = KeyListener.record_key()
    __addon__.setSetting('key_'+cmds[cmd], newkey)


def makeZattooGUI(showOSD=False):
  if (xbmcgui.Window(10000).getProperty('zattooGUI')!="True"):
    gui = zattooGUI("zattooGUI.xml", __addon__.getAddonInfo('path'))
    if showOSD: gui.act_showOSD()
    gui.doModal()
    del gui

def makeOsdInfo():
  channel_id=_zattooDB_.get_playing()['channel']
  channelInfo = _zattooDB_.get_channelInfo(channel_id)
  program = _zattooDB_.getPrograms({'index':[channel_id]}, True, datetime.datetime.now(), datetime.datetime.now())
  try: program=program[0]
  except: xbmcgui.Dialog().ok('Error',' ','No Info')

  description = program['description']
  if description is None: description = ''
  else: description = '  -  ' + description
  win=xbmcgui.Window(10000)
  win.setProperty('title', program['title'] + description)
  win.setProperty('channelInfo', channelInfo['title'] + ', ' + program['start_date'].strftime('%A %H:%M') + '-' + program['end_date'].strftime('%H:%M'))
  win.setProperty('showThumb', program['image_small'])
  win.setProperty('channelLogo', channelInfo['logo'])
  win.setProperty('plot', program['description_long'])
  win.setProperty('genre', '[COLOR blue]'+ local(135) + ':  ' + '[/COLOR]'+ str(program['genre']))
  win.setProperty('year', '[COLOR blue]' + local(345) + ':  ' + '[/COLOR]' + str(program['year']) + '   ' + '[COLOR blue]' + local(21866) + ':  ' + '[/COLOR]' + str(program['category']))
  win.setProperty('country', '[COLOR blue]' + local(574) + ':  ' + '[/COLOR]' + str(program['country']))
  
  played = datetime.datetime.now()-program['start_date']
  total = program['end_date'] - program['start_date']
  win.setProperty('progress', str((100/total.total_seconds())*played.total_seconds()))
  
  win.setProperty('favourite', str(channelInfo['favourite']))
  if channelInfo['favourite']==1: xbmc.executebuiltin( "Skin.SetBool(%s)" %'favourite')
  else: xbmc.executebuiltin( "Skin.Reset(%s)" %'favourite')
#  win.setProberty('category', '[COLOR blue]' + local(21866) + ':  ' + '[/COLOR]' + program['category'])

class myPlayer(xbmc.Player):
    def __init__(self, skip=0):
      self.skip=skip
      self.startTime=0
      self.playing=True
    def onPlayBackStarted(self):
      if (self.skip>0):
        self.seekTime(self.skip)
        self.startTime=self.startTime-datetime.timedelta(seconds=self.skip)
    def onPlayBackSeek(self, time, seekOffset):
      if self.startTime+datetime.timedelta(milliseconds=time) > datetime.datetime.now():
        channel=_zattooDB_.get_playing()['channel']
        _zattooDB_.set_playing() #clear setplaying to start channel in watch_channel
        xbmc.executebuiltin('RunPlugin("plugin://'+__addonId__+'/?mode=watch_c&id='+channel+'&showOSD=1")')
        self.playing=False
    def onPlayBackStopped(self):
        self.playing=False;
    def onPlayBackEnded(self):        
        self.playing=False;


class zattooGUI(xbmcgui.WindowXMLDialog):
  def __init__(self, xmlFile, scriptPath):
    xbmcgui.Window(10000).setProperty('zattooGUI', 'True')
    self.playing= _zattooDB_.get_playing()
    self.channelID = self.playing['channel']
    channels = _zattooDB_.getChannelList(_listMode_ == 'favourites')
    self.showChannelNr(channels[self.channelID]['nr']+1)

    self.toggleImgBG =xbmcgui.ControlImage(1280, 574, 260, 148, __addon__.getAddonInfo('path') + '/resources/teletextBG.png', aspectRatio=1)
    self.addControl(self.toggleImgBG)
    self.toggleImg =xbmcgui.ControlImage(1280, 576, 256, 144, '', aspectRatio=1)
    self.addControl(self.toggleImg)
    
    self.toggleChannelID=xbmcgui.Window(10000).getProperty('toggleChannel')
    if self.toggleChannelID!="": self.showToggleImg()

  def showToggleImg(self):
    self.toggleImgBG.setPosition(1022, 574)
    self.toggleImg.setPosition(1024, 576)
    self.refreshToggleImg()

  def hideToggleImg(self):
    if self.toggleChannelID!="":  
      self.toggleChannelID=""
      xbmcgui.Window(10000).setProperty('toggleChannel','')  
      self.toggleImgBG.setPosition(1280, 574)
      self.toggleImg.setPosition(1280, 576)
      if hasattr(self, 'refreshToggleImgTimer'): self.refreshToggleImgTimer.cancel()
      xbmcgui.Dialog().notification('Toggle', 'toggle end', __addon__.getAddonInfo('path') + '/icon.png', 5000, False)


  def refreshToggleImg(self):
    self.toggleImg.setImage('http://thumb.zattic.com/'+self.toggleChannelID+'/256x144.jpg?r='+str(int(time.time())), False)
    if hasattr(self, 'refreshToggleImgTimer'): self.refreshToggleImgTimer.cancel()
    self.refreshToggleImgTimer=  threading.Timer(16, self.refreshToggleImg)
    self.refreshToggleImgTimer.start()
  

  def onAction(self, action):
    key=str(action.getButtonCode())
    action = action.getId()

    #ignore mousemove
    if action==107: return

    #_zattooDB_=ZattooDB()
    #channel=_zattooDB_.get_playing()['channel']
    #channeltitle=_zattooDB_.get_channeltitle(channel)

    #print('ZATTOOGUI BUTTON'+str(action.getButtonCode()))
    #print('ZATTOOGUI ACTIONID'+str(action.getId()))
    #self.channelInputCtrl.setVisible(False)

    #user defined keys
    if key==__addon__.getSetting('key_OSD'): self.act_showOSD()
    elif key==__addon__.getSetting('key_Preview'): self.act_showPreview()
    elif key==__addon__.getSetting('key_EPG'): self.act_showEPG()
    elif key==__addon__.getSetting('key_List'): self.act_showList()
    elif key==__addon__.getSetting('key_Teletext'): self.act_teletext()
    elif key==__addon__.getSetting('key_nextChan'): self.act_nextChan()
    elif key==__addon__.getSetting('key_prevChan'): self.act_prevChan()
    elif key==__addon__.getSetting('key_toggleChan'): self.act_toggleChan()
    elif key==__addon__.getSetting('key_audio'):  self.act_changeStream()
    elif key==__addon__.getSetting('key_pause'): xbmc.Player().pause()
    elif key==__addon__.getSetting('key_stop'): self.close()
    elif key==__addon__.getSetting('key_record'): self.act_record()

    #default actions/keys
    elif action in [ACTION_PARENT_DIR, KEY_NAV_BACK, ACTION_PREVIOUS_MENU, ACTION_OSD]:
      self.close()
      xbmc.executebuiltin("Action(Back)")
    elif action  == ACTION_STOP:
      self.close()
      xbmc.Player().stop()  
    elif action in [ACTION_SELECT_ITEM, ACTION_MOUSE_LEFT_CLICK]: self.act_showOSD()
    elif action == ACTION_MOVE_DOWN: self.act_showEPG()
    elif action == ACTION_MOVE_UP: self.act_showList()
    elif action == ACTION_MOVE_LEFT: self.act_toggleChan()
    elif action == ACTION_MOVE_RIGHT: self.act_changeStream()
    elif action in [ACTION_CHANNEL_UP, ACTION_PAGE_UP, ACTION_SKIPNEXT]: self.act_prevChan()
    elif action in [ACTION_CHANNEL_DOWN, ACTION_PAGE_DOWN, ACTION_SKIPPREW]: self.act_nextChan()
    elif action == ACTION_RECORD: self.act_record()
    elif (action>57 and action<68):self.act_numbers(action)
    elif action == ACTION_BUILT_IN_FUNCTION:self.close() #keymap functions
    
  def act_showOSD(self):
    self.hideToggleImg()
      
    if(self.channelInput):
      self.channelInputTimer.cancel()
      self.channelInputTimeout()
    else:
      makeOsdInfo()
      gui = zattooOSD("zattooOSD.xml",__addon__.getAddonInfo('path'))
      gui.doModal()

  def act_showPreview(self):    
    xbmc.executebuiltin('RunPlugin("plugin://'+__addonId__+'/?mode=previewOSD")')  
    xbmc.executebuiltin("Action(OSD)") #close hidden gui
    
  def act_showEPG(self):    
    xbmc.executebuiltin("Action(OSD)") #close hidden gui
    xbmc.executebuiltin('RunPlugin("plugin://'+__addonId__+'/?mode=epgOSD")')
    
  def act_showList(self):
    xbmc.executebuiltin("Action(OSD)") #close hidden gui
    xbmc.executebuiltin('ActivateWindow(10025,"plugin://'+__addonId__+'/?mode=channellist")')
      
  def act_teletext(self):    
    from resources.teletext import Teletext
    tele = Teletext()
    tele.doModal()
    del tele     
            
  def act_toggleChan(self):
      self.hideChannelNr()
      self.showChannelNr(toggle_channel()+1)
      self.toggleChannelID=xbmcgui.Window(10000).getProperty('toggleChannel')
      self.showToggleImg()
            
  def act_changeStream(self): 
      if not DASH: change_stream(1)
      else:
          streams=xbmc.Player().getAvailableAudioStreams()
          dialog=xbmcgui.Dialog()
          ret = dialog.select('audio streams', streams)
          if ret==-1: return
          xbmc.Player().setAudioStream(ret)
          
  def act_prevChan(self):
      self.hideChannelNr()
      nr=skip_channel(-1)
      self.showChannelNr(nr+1)
      
  def act_nextChan(self):
      self.hideChannelNr()
      nr=skip_channel(+1)
      self.showChannelNr(nr+1)
      
  def act_record(self):
      program = _zattooDB_.getPrograms({'index':[channel]}, True, datetime.datetime.now(), datetime.datetime.now())
      program=program[0]
      setup_recording(program['showID'])
       
  def act_numbers(self,action):
      #print('channel ipnut'+str(action))
      if hasattr(self, 'channelInputTimer'): self.channelInputTimer.cancel()
      self.channelInput+=str(action-58)
      self.channelInputCtrl.setLabel(self.channelInput)
      self.channelInputCtrl.setVisible(True)
      if len(self.channelInput)>2: self.channelInputTimeout()
      else:
         self.channelInputTimer = threading.Timer(1.5, self.channelInputTimeout)
         self.channelInputTimer.start()


  def showChannelNr(self, channelNr):
    if not hasattr(self, 'channelInputCtrl'):
      self.channelInputCtrl = xbmcgui.ControlLabel(1000, 0, 270, 75,'', font='zattoo45', alignment=1)
      self.addControl(self.channelInputCtrl)
    self.channelNr=channelNr
    self.channelInput=''
    self.channelInputCtrl.setLabel(str(channelNr))
    self.channelInputCtrl.setVisible(True)
    if hasattr(self, 'hideNrTimer'): self.hideNrTimer.cancel()
    self.hideNrTimer=threading.Timer(5, self.hideChannelNr)
    self.hideNrTimer.start()

  def hideChannelNr(self):
    self.channelInputCtrl.setLabel(' ')
    self.channelInputCtrl.setVisible(False)

  def channelInputTimeout(self):
    skip=int(self.channelInput)-self.channelNr
    self.showChannelNr(int(self.channelInput))
    skip_channel(skip)

  def close(self):
    if hasattr(self, 'hideNrTimer'): self.hideNrTimer.cancel()
    xbmcgui.Window(10000).setProperty('zattooGUI', 'False')
    super(zattooGUI, self).close()
        

class zattooOSD(xbmcgui.WindowXMLDialog):
  def onInit(self):
    self.getControl(350).setPercent(float(xbmcgui.Window(10000).getProperty('progress')))    

  def onAction(self, action):
    #print('ZATTOOOSD BUTTON'+str(action.getButtonCode()))
    #print('ZATTOOOSD ACTIONID'+str(action.getId()))
    action = action.getId()
    #self.close()
    if action in [ACTION_PARENT_DIR, KEY_NAV_BACK, ACTION_PREVIOUS_MENU]:
      if hasattr(self, 'hideNrTimer'): self.hideNrTimer.cancel()
      self.close()
    elif action in [ACTION_STOP, ACTION_BUILT_IN_FUNCTION]:
      if hasattr(self, 'hideNrTimer'): self.hideNrTimer.cancel()
      self.close()
      print 'Action Stop'
      xbmc.sleep(1000)
      xbmc.executebuiltin('Action(OSD)') #close hidden gui
      #xbmc.executebuiltin("Action(Back)")
    elif action == ACTION_SKIPPREW:
      xbmc.executebuiltin("Action(Left)")
    elif action == ACTION_SKIPNEXT:
      xbmc.executebuiltin("Action(Right)")

  def onClick(self, controlID):
    channel=_zattooDB_.get_playing()['channel']
    channeltitle=_zattooDB_.get_channeltitle(channel)
    program = _zattooDB_.getPrograms({'index':[channel]}, True, datetime.datetime.now(), datetime.datetime.now())
    program=program[0]
    self.close() #close OSD

    if controlID==209: #recall
      xbmc.executebuiltin("Action(OSD)") #close hidden gui
      start = int(time.mktime(program['start_date'].timetuple()))
      end = int(time.mktime(program['end_date'].timetuple()))
      showID = program['showID']
      if SWISS == 'true': watch_channel(channel,start,end)
      else: watch_channel(channel, start, end, showID, True)
    elif controlID==210: #record program
      setup_recording(program['showID'])
    elif controlID==211: #teletext
      from resources.teletext import Teletext
      tele = Teletext()
      tele.doModal()
      del tele
    elif controlID==201: #Back
      self.close()
    elif controlID==202: #Channel Up
      nr=skip_channel(-1)
    elif controlID==203: #Channel Down
      nr=skip_channel(+1)
    elif controlID==205: #stop
      #xbmc.executebuiltin("Action(OSD)")
      xbmc.executebuiltin("Action(Stop)")
      
    #elif controlID==208: #start channel
    #  if xbmcgui.Dialog().yesno(channeltitle, __addon__.getLocalizedString(31907)):
    #     __addon__.setSetting(id="start_channel", value=channeltitle)
     
    elif controlID==208: #favourite
      isFavourite=xbmcgui.Window(10000).getProperty('favourite')
      channelList=_zattooDB_.getChannelList()['index']
      update=False
                                 
      if isFavourite=="0":
          if xbmcgui.Dialog().yesno(channeltitle, __addon__.getLocalizedString(31908)): 
            channelList.append(channel)
            update=True
      elif xbmcgui.Dialog().yesno(channeltitle, __addon__.getLocalizedString(31909)):
          channelList.remove(channel)
          update=True

      if update:
        channelList=",".join(channelList)
        result=_zattooDB_.zapi.exec_zapiCall('/zapi/channels/favorites/update', {'cids': channelList, 'ctype': 'tv'})
        _zattooDB_.updateChannels(True)
        _zattooDB_.updateProgram()
         
    elif controlID>300:
      xbmcgui.Window(10000).setProperty('zattoo_runningView',"")
      xbmcgui.Window(10000).setProperty('zattooGUI', 'False')
      xbmc.executebuiltin("Dialog.Close(all,true)") #close hidden GUI
      #xbmc.executebuiltin("Action(OSD)") #close hidden gui
      
      if controlID==303: xbmc.executebuiltin('ActivateWindow(10025,"plugin://'+__addonId__+'/?mode=channellist")')
      elif controlID==302: xbmc.executebuiltin('RunPlugin("plugin://'+__addonId__+'/?mode=previewOSD")')
      elif controlID==301: xbmc.executebuiltin('RunPlugin("plugin://'+__addonId__+'/?mode=epgOSD")')
      
  def onFocus(self, controlID):
    i=10



class KeyListener(xbmcgui.WindowXMLDialog):
    TIMEOUT = 3

    def __new__(cls):
        gui_api = tuple(map(int, xbmcaddon.Addon('xbmc.gui').getAddonInfo('version').split('.')))
        file_name = "DialogNotification.xml" if gui_api >= (5, 11, 0) else "DialogKaiToast.xml"
        return super(KeyListener, cls).__new__(cls, file_name, "")

    def __init__(self):
        self.key = None

    def onInit(self):
        try:
            self.getControl(401).addLabel(localString(32001)+' in 3sec')
            #self.getControl(402).addLabel(localString(32002))
        except AttributeError:
            self.getControl(401).setLabel(localString(32001)+' in 3sec')
            #self.getControl(402).setLabel(localString(32002))

    def onAction(self, action):
        code = action.getButtonCode()
        self.key = None if code == 0 else str(code)
        self.close()

    @staticmethod
    def record_key():
        dialog = KeyListener()
        timeout = threading.Timer(KeyListener.TIMEOUT, dialog.close)
        timeout.start()
        dialog.doModal()
        timeout.cancel()
        key = dialog.key
        del dialog
        return key











def main():

  global _listMode_
  if _listMode_ == None: _listMode_='all'
  print 'LISTMODE  ' + str(_listMode_)
  addon_uri = sys.argv[0]
  addon_handle = int(sys.argv[1])
  args = urlparse.parse_qs(sys.argv[2][1:])
  action=args.get('mode', ['root'])[0]

  #xbmcgui.Dialog().notification("HANDLE", str(action)+' '+str(addon_handle), '', 1000, False)

  #hack for repeat actions from keyMap
  #if ((action=='preview' or action=='epg' )and action==xbmcgui.Window(10000).getProperty('ZBElastAction')):
    #xbmcgui.Window(10000).setProperty('ZBElastAction', '')
    #xbmc.executebuiltin("Action(FullScreen)")
    #if(str(_zattooDB_.get_playing()['start'])=='1970-01-01 01:00:00'):makeZattooGUI()
    #return
  xbmcgui.Window(10000).setProperty('ZBElastAction', action)


  if action is 'root': build_root(addon_uri, addon_handle)
  elif action == 'channellist': build_channelsList(addon_uri, addon_handle)
  elif action == 'preview': showPreview()
  elif action == 'previewOSD': showPreview()
  elif action == 'epg': showEpg()
  elif action == 'epgOSD': showEpg()
  elif action == 'recordings': build_recordingsList(addon_uri, addon_handle)
  elif action == 'search': search_show(addon_uri, addon_handle)
  elif action == 'selectStartChannel': selectStartChannel()
  elif action == 'editKeyMap': editKeyMap()
  elif action == 'show_settings':
    __addon__.openSettings()
    _zattooDB_.zapi.renew_session()
  elif action == 'watch_c':
    cid = args.get('id','ard')[0]
    start = args.get('start', '0')[0]
    end = args.get('end', '0')[0]
    showID = args.get('showID', '1')[0]
    restart = args.get('restart', 'false')[0]
    showOSD = args.get('showOSD', '0')[0]
    watch_channel(cid, start, end, showID, restart=='true', showOSD=='1')
  elif action == 'skip_channel':
    skipDir = args.get('skipDir')[0]
    skip_channel(int(skipDir))
  elif action == 'toggle_channel': toggle_channel()
  elif action == 'switchlist':
    if _listMode_ == 'all': _listMode_ = 'favourites'
    else: _listMode_ = 'all'
    __addon__.setSetting('channellist', _listMode_)
    xbmc.executebuiltin('Container.Refresh')
  elif action == 'watch_r':
    recording_id = args.get('id')[0]
    startTime = args.get('starttime')[0]
    position =  args.get('position')[0]
    watch_recording(addon_uri, addon_handle, recording_id, startTime, position)
  elif action == 'record_p':
    program_id = args.get('program_id')[0]
    setup_recording(program_id)
  elif action == 'remove_recording':
    recording_id = args.get('recording_id')[0]
    delete_recording(recording_id)
  elif action == 'remove_series':
    recording_id = args.get('recording_id')[0]
    series = args.get('series')[0]
    delete_series(recording_id, series)
  elif action == 'reloadDB':
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    _zattooDB_.reloadDB()
    xbmcgui.Dialog().notification(localString(31916), localString(30110),  __addon__.getAddonInfo('path') + '/icon.png', 3000, False)
    _zattooDB_.getProgInfo(True)
    xbmcgui.Dialog().notification(localString(31106), localString(31915),  __addon__.getAddonInfo('path') + '/icon.png', 3000, False)
    _library_.make_library()
    xbmc.executebuiltin("Dialog.Close(busydialog)")
  elif action == 'changeStream':
    dir = int(args.get('dir')[0])
    change_stream(dir)
  elif action == 'teletext':
    from resources.teletext import Teletext
    tele = Teletext()
    tele.doModal()
    del tele
  elif action == 'makelibrary':
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    _library_.delete_library()
    _library_.make_library()
    xbmc.executebuiltin("Dialog.Close(busydialog)")
  elif action == 'resetdir':
    delete = xbmcgui.Dialog().yesno(__addonname__, __addon__.getLocalizedString(31911))
    if delete:
      _library_.delete_library()
      __addon__.setSetting(id="library_dir", value="")
      xbmc.executebuiltin('Container.Refresh')
  elif action == 'cleanProg':
    _zattooDB_.cleanProg()
  elif action == 'popular': showPreview('popular')



  '''
  elif action == 'showInfo':
    #xbmc.executebuiltin('ActivateWindow(12003)')
    info = osdInfo()
    info.doModal()
    del info
  '''


main()







