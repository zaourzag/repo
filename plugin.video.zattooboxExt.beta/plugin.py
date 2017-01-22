# coding=utf-8
#
#    ZattooBox Extended
#
#  Copyright (C) 2015 Daniel Griner (griner.ch@gmail.com)
#  based on ZattooBox by Pascal Nançoz (nancpasc@gmail.com)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#



REMOTE_DBG = False

# append pydev remote debugger
if REMOTE_DBG:
  # Make pydev debugger works for auto reload.
  # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
  try:
    import pysrc.pydevd as pydevd  # with the addon script.module.pydevd, only use `import pydevd`
  # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
    #pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True, suspend=False)
    pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)
  except ImportError:
    sys.stderr.write("Error: You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
    sys.exit(1)


import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, urlparse
import  time, datetime, threading
from resources.library import library
from resources.zattooDB import ZattooDB

__addon__ = xbmcaddon.Addon()
__addonId__=__addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')

#_timezone_ = int(__addon__.getSetting('time_offset'))*60*-60 #-time.altzone
_listMode_ = __addon__.getSetting('channellist')
_channelList_=[]
_zattooDB_=ZattooDB()
_library_=library()

_umlaut_ = {ord(u'ä'): u'ae', ord(u'ö'): u'oe', ord(u'ü'): u'ue', ord(u'ß'): u'ss'}

localString = __addon__.getLocalizedString
local = xbmc.getLocalizedString

ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_SELECT_ITEM = 7
ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_STOP = 13

ACTION_OSD=24

KEY_NAV_BACK = 92
KEY_HOME = 159

ACTION_MOUSE_DOUBLE_CLICK = 103
ACTION_MOUSE_DRAG = 106
ACTION_MOUSE_END = 109
ACTION_MOUSE_LEFT_CLICK = 100
ACTION_MOUSE_LONG_CLICK = 108
ACTION_MOUSE_MIDDLE_CLICK = 102
ACTION_MOUSE_MOVE = 107
ACTION_MOUSE_RIGHT_CLICK = 101
ACTION_MOUSE_START = 100
ACTION_MOUSE_WHEEL_DOWN = 105
ACTION_MOUSE_WHEEL_UP = 104
ACTION_BUILT_IN_FUNCTION = 122

ACTION_CHANNEL_UP = 184
ACTION_CHANNEL_DOWN = 185
ACTION_PAGE_UP = 5
ACTION_PAGE_DOWN = 6

SWISS = xbmcaddon.Addon('plugin.video.zattooboxExt.beta').getSetting('swiss')
HIQ = xbmcaddon.Addon('plugin.video.zattooboxExt.beta').getSetting('hiq')



if SWISS=="true":
    xbmc.executebuiltin( "Skin.SetBool(%s)" %'swiss')
else:
    xbmc.executebuiltin( "Skin.Reset(%s)" %'swiss')
if HIQ=='true':
    xbmc.executebuiltin( "Skin.SetBool(%s)" %'hiq')
else:
    xbmc.executebuiltin( "Skin.Reset(%s)" %'hiq')
    
from tzlocal import get_localzone
import pytz
try:
  tz = get_localzone()
  offset=tz.utcoffset(datetime.datetime.now()).total_seconds()
  _timezone_=int(offset)
except:
  _timezone_ = int(__addon__.getSetting('time_offset'))*60*-60 #-time.altzone


def build_directoryContent(content, addon_handle, cache=True, root=False):
  xbmcplugin.setContent(addon_handle, 'movies')
  xbmcplugin.setPluginFanart(addon_handle, __addon__.getAddonInfo('path') + '/fanart.jpg')
  for record in content:
    # set missing properties
    record['image'] = record.get('image', "")
    record['plot'] = record.get('plot', "")
    record['thumbnail'] = record.get('thumbnail', "")
    record['selected'] = record.get('selected', False)
    record['genre'] = record.get('genre', "")
    record['year'] = record.get('year', "")
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
 
def build_root(addon_uri, addon_handle):
  import urllib

  # check if settings are set
  name = __addon__.getSetting('username')
  if name == '':
    # show home window, zattoobox settings and quit
    xbmc.executebuiltin('ActivateWindow(10000)')
    xbmcgui.Dialog().ok(__addonname__, localString(31902))
    __addon__.openSettings()
    sys.exit()
  
  #play channel on open addon
  if ((not xbmc.Player().isPlaying()) and (__addon__.getSetting('start_liveTV')=='true')):
    channeltitle = __addon__.getSetting('start_channel')
    channelid = _zattooDB_.get_channelid(channeltitle)
    resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/watch', {'cid': channelid, 'stream_type': 'hls', 'maxrate':__addon__.getSetting('max_bandwidth')})
    xbmc.Player().play(resultData['stream']['watch_urls'][0]['url'])
    streamsList = []
    for stream in resultData['stream']['watch_urls']: streamsList.append(stream['url'])
    streamsList = '|'.join(streamsList)
    _zattooDB_.set_playing(channelid, '0', streamsList, 0)
    makeZattooGUI()

  
  iconPath = __addon__.getAddonInfo('path') + '/icon.png'
  if _listMode_ == 'all': listTitle = localString(31100)
  else: listTitle = localString(31101)

  content = [
    {'title': '[B][COLOR blue]' + listTitle + '[/COLOR][/B]', 'image': iconPath, 'isFolder': False, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'switchlist'})},
    {'title': localString(31102), 'image': iconPath, 'isFolder': True, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'channellist'})},
    {'title': localString(31103), 'image': iconPath, 'isFolder': False, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'preview'})},
    {'title': localString(31104), 'image': iconPath, 'isFolder': False, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'epg'})},
    {'title': localString(31105), 'image': iconPath, 'isFolder': True, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'search'})},
    {'title': localString(31106), 'image': iconPath, 'isFolder': True, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'recordings'})},
    {'title': localString(31006), 'image': iconPath, 'isFolder': True, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'reloadDB'})},
    {'title': '[COLOR ff333333]' + localString(31107) + '[/COLOR]', 'image': iconPath, 'isFolder': False, 'url': addon_uri + '?' + urllib.urlencode({'mode': 'show_settings'})},
    ]
  build_directoryContent(content, addon_handle, True, False)

  #update db
  _zattooDB_.updateChannels()
  _zattooDB_.updateProgram()

  
def build_channelsList(addon_uri, addon_handle):
  import urllib
  channels = _zattooDB_.getChannelList(_listMode_ == 'favourites')
  if channels is not None:
    # get currently playing shows
    program = _zattooDB_.getPrograms(channels, True)
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
      
      content.append({
        'title': '[COLOR green]'+chnr+'[/COLOR]'+'  '+channels[chan]['title'] + ' - ' + prog.get('title', '')+ '  '+startend,
        'image': channels[chan]['logo'],
        'thumbnail': prog.get('image_small', ''),
        'genre': prog.get('genre',''),
        'plot':  prog.get('description_long', ''),
        #'plot': prog.get('genre','')+"  "+str(prog.get('year','')),
        'year': prog.get('year',''),
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
    now = time.time()    
    color='red'
    if (now>start): color='orange'
    if (now>end): color='green'
    
    start=datetime.datetime.fromtimestamp(start).strftime('%d.%m.%Y. %H:%M') # NEW changed - by Samoth
    label=start+' '
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
    li.setProperty('IsPlayable', 'true')

    contextMenuItems = []
    contextMenuItems.append(('delete recording', 'RunPlugin("plugin://'+__addonId__+'/?mode=remove_recording&recording_id='+str(record['id'])+'")'))
    li.addContextMenuItems(contextMenuItems, replaceItems=True)
    
    xbmcplugin.addDirectoryItem(
      handle=addon_handle,
      url=addon_uri + '?' + urllib.urlencode({'mode': 'watch_r', 'id': record['id']}),
      listitem=li,
      isFolder=False
    )
  xbmcplugin.endOfDirectory(addon_handle)
  xbmcplugin.setContent(addon_handle, 'movies')
  xbmcplugin.addSortMethod(addon_handle, 2)
  xbmcplugin.addSortMethod(addon_handle, 9)
  
def watch_recording(addon_uri, addon_handle, recording_id):
  #if xbmc.Player().isPlaying(): return
  max_bandwidth = __addon__.getSetting('max_bandwidth')
  params = {'recording_id': recording_id, 'stream_type': 'hls', 'maxrate':max_bandwidth}
  resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/watch', params)
  if resultData is not None:
    streams = resultData['stream']['watch_urls']

    if len(streams)==0:
      xbmcgui.Dialog().notification("ERROR", "NO STREAM FOUND, CHECK SETTINGS!", channelInfo['logo'], 5000, False)
      return
    elif len(streams) > 1 and  __addon__.getSetting('audio_stream') == 'B' and streams[1]['audio_channel'] == 'B': streamNr = 1
    else: streamNr = 0
    #image=xbmc.getInfoLabel('infolabel')
    
    li = xbmcgui.ListItem()
    #li.setInfo(type="Video", infoLabels={})
    li.setPath(streams[streamNr]['url'])

    player= myPlayer(True)
    xbmcplugin.setResolvedUrl(addon_handle, True, li)
    #wait for 5min skip
    while (player.starting):xbmc.sleep(100)

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


def watch_channel(channel_id, start, end):
  #print('WATCH: '+channel_id+' st:'+str(start)+' en:'+str(end))
  
  #new ZattooDB instance because this is called from thread-timer on channel-nr input (sql connection doesn't work)
  _zattooDB_=ZattooDB()
  #selected currently playing live TV
  playing=_zattooDB_.get_playing()
  if (xbmc.Player().isPlaying() and channel_id == playing['channel'] and start=='0' and str(playing['start'])=='1970-01-01 01:00:00'):
    xbmc.executebuiltin("Action(FullScreen)")
    makeZattooGUI()
    return

  #save current channel for toggle
  xbmcgui.Window(10000).setProperty('ZBElastChannel', playing['channel'])
  
  # (64 150 300) 600 900 1500 3000 5000
  max_bandwidth = __addon__.getSetting('max_bandwidth')
  if start == '0': params = {'cid': channel_id, 'stream_type': 'hls', 'maxrate':max_bandwidth}
  else:
    zStart = datetime.datetime.fromtimestamp(int(start) - _timezone_ ).strftime("%Y-%m-%dT%H:%M:%SZ")  #5min zattoo skips back
    zEnd = datetime.datetime.fromtimestamp(int(end) - _timezone_ ).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {'cid': channel_id, 'stream_type': 'hls', 'start':zStart, 'end':zEnd, 'maxrate':max_bandwidth }
    
  channelInfo = _zattooDB_.get_channelInfo(channel_id)  
  resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/watch',params)
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
  
  #play liveTV: info is created in OSD
  if (start=='0'):
    xbmc.Player().play(streams[streamNr]['url'], xbmcgui.ListItem(channel_id))
    xbmcgui.Window(10000).setProperty('playstream', streams[streamNr]['url'])
  
  #12005:fullscreenvideo
  #if (xbmcgui.getCurrentWindowId()!=12005):xbmc.executebuiltin("Action(FullScreen)")
   
  # save currently playing
  streamsList = []
  for stream in resultData['stream']['watch_urls']: streamsList.append(stream['url'])
  streamsList = '|'.join(streamsList)
  _zattooDB_.set_playing(channel_id, start, streamsList, streamNr)

  #make Info
  if start == '0':startTime = datetime.datetime.now()
  else: startTime = datetime.datetime.fromtimestamp(int(start))
  if end == '0': endTime = datetime.datetime.now() 
  else: endTime = datetime.datetime.fromtimestamp(int(end))
  program = _zattooDB_.getPrograms({channel_id:''}, True, startTime, endTime)

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

  #play recall
  if (start!='0'):
    player= myPlayer(True)
    player.play(streams[streamNr]['url'], listitem)
    while (player.starting):xbmc.sleep(10) #wait for player to skip 5min on recall
  else: makeZattooGUI() #liveTV: intercept keys and show OSD

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
  lastChannel=xbmcgui.Window(10000).getProperty('ZBElastChannel')
  watch_channel(lastChannel, '0', '0')
  
  _zattooDB_=ZattooDB()
  channelList = _zattooDB_.getChannelList(_listMode_ == 'favourites')
  nr=channelList[lastChannel]['nr']
  return nr


def change_stream(dir):
  playing = _zattooDB_.get_playing()
  streams = playing['streams'].split('|')
  streamNr = (playing['current_stream'] + dir) % len(streams)

  _zattooDB_.set_currentStream(streamNr)

  channelInfo = _zattooDB_.get_channelInfo(playing['channel'])
  program = _zattooDB_.getPrograms({playing['channel']:''}, True)[0]

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


def showPreview(OSD):
  from resources.channelspreview import ChannelsPreview
  preview = ChannelsPreview()
  preview.createPreview(_listMode_ == 'favourites')
  preview.doModal()
  del preview

  if (OSD): makeZattooGUI()
  
def showEpg(OSD):
  from resources.epg.epg import EPG

  currentChannel = _zattooDB_.get_playing()['channel']
  channelList = _zattooDB_.getChannelList(_listMode_ == 'favourites')
  currentNr=channelList[currentChannel]['nr']  

  accountData=_zattooDB_.zapi.get_accountData()
  premiumUser=accountData['account']['subscriptions']!=[]
  
  epg = EPG(currentNr, premiumUser)
  epg.loadChannels(_listMode_ == 'favourites')
  epg.doModal()
  del epg
  
  if (OSD): makeZattooGUI()


def makeZattooGUI():
  open=xbmcgui.Window(10000).getProperty('zattooGUI')
  if (open!='True'):
    xbmcgui.Window(10000).setProperty('zattooGUI', 'True')
    gui = zattooGUI("zattooGUI.xml", __addon__.getAddonInfo('path'))
    gui.doModal()
    del gui
    xbmcgui.Window(10000).setProperty('zattooGUI', 'False')

def makeOsdInfo():
  channel_id=_zattooDB_.get_playing()['channel']
  channelInfo = _zattooDB_.get_channelInfo(channel_id)
  program = _zattooDB_.getPrograms({channel_id:''}, True, datetime.datetime.now(), datetime.datetime.now())
  program=program[0]
  
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
#  win.setProberty('category', '[COLOR blue]' + local(21866) + ':  ' + '[/COLOR]' + program['category'])

class myPlayer( xbmc.Player ):
  def __init__(self, skip=False):
    self.skip=skip
    self.starting=True
  def onPlayBackStarted(self):
    self.starting=False
    if (self.skip): self.seekTime(300)

class zattooGUI(xbmcgui.WindowXMLDialog):
  def __init__(self, xmlFile, scriptPath):
    #super(zattooGUI, self).__init__()
    #print('ZATTOOGUI')
    self.channelID = _zattooDB_.get_playing()['channel']
    channels = _zattooDB_.getChannelList(_listMode_ == 'favourites')
    self.showChannelNr(channels[self.channelID]['nr']+1)
    
    self.prevImageBG =xbmcgui.ControlImage(1280, 574, 260, 148, __addon__.getAddonInfo('path') + '/resources/teletextBG.png', aspectRatio=1)
    self.addControl(self.prevImageBG)
    
    self.prevImage =xbmcgui.ControlImage(1280, 576, 256, 144, '', aspectRatio=1)
    self.addControl(self.prevImage)
    
    
    
  def setPrevImg(self):
    self.channelID = _zattooDB_.get_playing()['channel']
    self.prevImageBG.setPosition(1022, 574)
    self.prevImage.setPosition(1024, 576)
    self.refreshPrevImg()

  def hidePrevImg(self):
    if self.prevImage.getX()==1024:
      self.prevImageBG.setPosition(1280, 574)
      self.prevImage.setPosition(1280, 576)
      if hasattr(self, 'refreshPrevImageTimer'): self.refreshPrevImageTimer.cancel()
      return True
    else: return False
      
    
  def refreshPrevImg(self):
    self.prevImage.setImage('http://thumb.zattic.com/'+self.channelID+'/256x144.jpg?r='+str(int(time.time())), False)
    
    if hasattr(self, 'refreshPrevImageTimer'): self.refreshPrevImageTimer.cancel()
    self.refreshPrevImageTimer=  threading.Timer(16, self.refreshPrevImg)
    self.refreshPrevImageTimer.start()
    
  def onAction(self, action):
    #print('ZATTOOGUI BUTTON'+str(action.getButtonCode()))
    #print('ZATTOOGUI ACTIONID'+str(action.getId()))
    self.channelInputCtrl.setVisible(False)
    action = action.getId()
    
    if action in [ACTION_PARENT_DIR, KEY_NAV_BACK, ACTION_PREVIOUS_MENU]:
      if hasattr(self, 'hideNrTimer'): self.hideNrTimer.cancel()
      self.close()
      xbmc.executebuiltin("Action(Back)")
    elif action==ACTION_STOP:
      if hasattr(self, 'hideNrTimer'): self.hideNrTimer.cancel()
      self.close()
    elif action==ACTION_OSD:
      if hasattr(self, 'hideNrTimer'): self.hideNrTimer.cancel()
      self.close()
    if action in [ACTION_SELECT_ITEM, ACTION_MOUSE_LEFT_CLICK]:
      self.hidePrevImg()
      if(self.channelInput):
        self.channelInputTimer.cancel()
        self.channelInputTimeout()
      else:
        makeOsdInfo()
        gui = zattooOSD("zattooOSD.xml",__addon__.getAddonInfo('path'))
        gui.doModal()

    elif action == ACTION_MOVE_LEFT:
      self.setPrevImg()
      self.showChannelNr(toggle_channel()+1)
    elif action == ACTION_MOVE_RIGHT:
      change_stream(1)
    elif action in [ACTION_MOVE_UP, ACTION_CHANNEL_UP, ACTION_PAGE_UP]:
      if self.hidePrevImg():return
      nr=skip_channel(+1)
      self.showChannelNr(nr+1)
    elif action in [ACTION_MOVE_DOWN, ACTION_CHANNEL_DOWN, ACTION_PAGE_DOWN]:
      if self.hidePrevImg():return
      nr=skip_channel(-1)
      self.showChannelNr(nr+1)
    
    elif (action>57 and action<68): #numbers 0-9
      self.hidePrevImg()
      #print('channel ipnut'+str(action))
      if hasattr(self, 'channelInputTimer'): self.channelInputTimer.cancel()
      self.channelInput+=str(action-58)
      self.channelInputCtrl.setLabel(self.channelInput)
      self.channelInputCtrl.setVisible(True)
      if len(self.channelInput)>2: self.channelInputTimeout()
      else:
         self.channelInputTimer = threading.Timer(1.5, self.channelInputTimeout)
         self.channelInputTimer.start()
    elif action == ACTION_BUILT_IN_FUNCTION:self.close() #keymap functions

  def showChannelNr(self, channelNr):
    if not hasattr(self, 'channelInputCtrl'): 
      self.channelInputCtrl = xbmcgui.ControlLabel(1000, 0, 270, 75,'', font='font35_title', alignment=1)
      self.addControl(self.channelInputCtrl)
    self.channelNr=channelNr
    self.channelInput=''
    self.channelInputCtrl.setLabel(str(self.channelNr))
    self.channelInputCtrl.setVisible(True)
    if hasattr(self, 'hideNrTimer'): self.hideNrTimer.cancel()
    self.hideNrTimer=threading.Timer(5, self.hideChannelNr)
    self.hideNrTimer.start()

  def hideChannelNr(self):
    self.channelInputCtrl.setVisible(False)
    self.channelInputCtrl.setLabel('')

  def channelInputTimeout(self):
    skip=int(self.channelInput)-self.channelNr
    self.showChannelNr(int(self.channelInput))
    skip_channel(skip)
    
class zattooOSD(xbmcgui.WindowXMLDialog):
  
  def onAction(self, action):
    #print('ZATTOOOSD BUTTON'+str(action.getButtonCode()))
    #print('ZATTOOOSD ACTIONID'+str(action.getId()))
    action = action.getId()  
    if action in [ACTION_PARENT_DIR, KEY_NAV_BACK, ACTION_PREVIOUS_MENU]:
      self.close()
    if action in [ACTION_STOP, ACTION_BUILT_IN_FUNCTION]:
      self.close()
      xbmc.executebuiltin("Action(OSD)") #close hidden gui
   
      
  def onClick(self, controlID):
    channel=_zattooDB_.get_playing()['channel']
    channeltitle=_zattooDB_.get_channeltitle(channel)
    program = _zattooDB_.getPrograms({channel:''}, True, datetime.datetime.now(), datetime.datetime.now())
    program=program[0]
    self.close() #close OSD

    if controlID==209: #recall
      xbmc.executebuiltin("Action(OSD)") #close hidden gui
      start = int(time.mktime(program['start_date'].timetuple()))
      end = int(time.mktime(program['end_date'].timetuple()))
      watch_channel(channel,start,end)
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
      self.showChannelNr(nr+1)
    elif controlID==203: #Channel Down
      nr=skip_channel(+1)
      self.showChannelNr(nr+1)
    elif controlID==205:
      xbmc.executebuiltin("Action(Stop)")
      xbmc.executebuiltin("Action(OSD)")
      if hasattr(self, 'hideNrTimer'): self.hideNrTimer.cancel()
      self.close()
    elif controlID==208:
      if xbmcgui.Dialog().yesno(channeltitle, __addon__.getLocalizedString(31907)):
         __addon__.setSetting(id="start_channel", value=channeltitle)
    elif controlID>300:
      xbmc.executebuiltin("Action(OSD)") #close hidden gui
      if controlID==303: xbmc.executebuiltin('ActivateWindow(10025,"plugin://'+__addonId__+'/?mode=channellist")')
      #if controlID==301: xbmc.executebuiltin('RunPlugin("plugin://'+__addonId__+'/?mode=channellist")')
      elif controlID==302: xbmc.executebuiltin('RunPlugin("plugin://'+__addonId__+'/?mode=previewOSD")')
      elif controlID==301: xbmc.executebuiltin('RunPlugin("plugin://'+__addonId__+'/?mode=epgOSD")')


   
        
  def onFocus(self, controlID):
    i=10


def main():
  global _listMode_
  addon_uri = sys.argv[0]
  addon_handle = int(sys.argv[1])
  args = urlparse.parse_qs(sys.argv[2][1:])
  action=args.get('mode', ['root'])[0]
  
  #xbmcgui.Dialog().notification("HANDLE", str(action)+' '+str(addon_handle), '', 1000, False)
  
  #hack for repeat actions from keyMap 
  if ((action=='preview' or action=='epg' or action=='channellist')and action==xbmcgui.Window(10000).getProperty('ZBElastAction')):
    xbmcgui.Window(10000).setProperty('ZBElastAction', '')
    xbmc.executebuiltin("Action(FullScreen)")
    if(str(_zattooDB_.get_playing()['start'])=='1970-01-01 01:00:00'):makeZattooGUI()
    return
  xbmcgui.Window(10000).setProperty('ZBElastAction', action)
  
  
  if action is 'root': build_root(addon_uri, addon_handle)
  elif action == 'channellist': build_channelsList(addon_uri, addon_handle)
  elif action == 'preview': showPreview(False)
  elif action == 'previewOSD': showPreview(True)
  elif action == 'epg': showEpg(False)
  elif action == 'epgOSD': showEpg(True)
  elif action == 'recordings': build_recordingsList(addon_uri, addon_handle)
  elif action == 'search': search_show(addon_uri, addon_handle)
  elif action == 'show_settings':
    __addon__.openSettings()
    _zattooDB_.zapi.renew_session()    
  elif action == 'watch_c':
    cid = args.get('id','sf-1')[0]
    start = args.get('start', '0')[0]
    end = args.get('end', '0')[0]
    watch_channel(cid, start, end)
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
    watch_recording(addon_uri, addon_handle, recording_id)
  elif action == 'record_p':
    program_id = args.get('program_id')[0]
    setup_recording(program_id)
  elif action == 'remove_recording':
    recording_id = args.get('recording_id')[0]
    delete_recording(recording_id)
  elif action == 'reloadDB':
    _zattooDB_.reloadDB()
    xbmcgui.Dialog().notification(__addonname__, __addon__.getLocalizedString(31250),  __addon__.getAddonInfo('path') + '/icon.png', 000, False)    
    _library_.delete_library() # New added - by Samoth    
    _library_.make_library
  elif action == 'changeStream':
    dir = int(args.get('dir')[0])
    change_stream(dir)
  elif action == 'teletext':
    from resources.teletext import Teletext
    tele = Teletext()
    tele.doModal()
    del tele
  elif action == 'makelibrary':
    delete_library()
    _library_.make_library()
  elif action == 'resetdir':
    delete = xbmcgui.Dialog().yesno(__addonname__, __addon__.getLocalizedString(31911))
    if delete:
      _library_.delete_library()
      __addon__.setSetting(id="library_dir", value="")
      xbmc.executebuiltin('Container.Refresh')
  '''
  elif action == 'showInfo':
    #xbmc.executebuiltin('ActivateWindow(12003)')
    info = osdInfo()
    info.doModal()
    del info
  '''
  
  
  
main()







