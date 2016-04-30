# -*- coding: utf-8 -*-
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import os.path
import urllib, urllib2, cookielib
import re,time, string

try:
	import json
except:
	import simplejson as json


addon = xbmcaddon.Addon(id='plugin.video.putpat')

# Constants
MODE_ROOT = 0
MODE_PLAY = 1
MODE_VEEQUALIZER = 2
MODE_VEEQUALIZER_PLAY = 3

ADDONUSERDATAPATH = xbmc.translatePath(addon.getAddonInfo('profile'))
COOKIEFILE = os.path.join(ADDONUSERDATAPATH, 'cookies.lwp')

if not os.path.exists(ADDONUSERDATAPATH):
	os.makedirs(ADDONUSERDATAPATH)



pluginhandle = int(sys.argv[1])

qualitySetting = xbmcplugin.getSetting(pluginhandle, 'quality')

baseurl = 'http://www.putpat.tv'
streamingMethod = 'rtmp'
authenticityToken = ''

# This is done for cookie handling
cookieJar = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
urllib2.install_opener(opener)

if os.path.isfile(COOKIEFILE):
	cookieJar.load(COOKIEFILE, ignore_discard = True)



def showRootMenu():
	
	# Log in
	mail = xbmcplugin.getSetting(pluginhandle, 'mail')
	password = xbmcplugin.getSetting(pluginhandle, 'password')
	
	session = {}
	postObject = {}
	postObject['session'] = session
	
	if (mail is not None) and (len(mail) > 0) and (password is not None) and (len(password) > 0):
		session['email'] = mail
		session['password'] = password
	else:
		cookieJar.clear()
	
	jsonObject = getJsonObject(baseurl + '/api/session.json', postObject)
	
	receivedSession = jsonObject['session']
	authenticityToken = receivedSession['csrf_token']
	userId = receivedSession['user_id']
	
	# Veequalizer
	if userId is not None:
		addDir('Veequalizer', '', MODE_VEEQUALIZER, getThumbUrl(0), authenticityToken)
	
	# Get standard channels
	jsonObject = getJsonObject(baseurl + '/ws.json?method=Channel.allWithClips&streaming_method=' + streamingMethod)
	
	for object in jsonObject:
		channel = object['channel']
		
		title = channel['title']
		identifier = channel['id']
		thumb = getThumbUrl(identifier)
		url = baseurl + '/ws.json?method=Channel.clips&channelId=' + str(identifier) + '&streaming_method=' + streamingMethod
		
		description = channel['channel_info']
		shortDescription = channel['channel_message']
		additionalInfos = {}
		additionalInfos['plot'] = description
		additionalInfos['plotoutline'] = shortDescription
		
		liz = addLink(title, url, MODE_PLAY, thumb, authenticityToken, additionalInfos = additionalInfos)
		
	xbmcplugin.endOfDirectory(int(sys.argv[1]))



def showVeequalizerPresets():
	
	jsonObject = getJsonObject(baseurl + '/ws.json?method=User.veequalizerPresets')
	jsonObject.remove(jsonObject[0])
	
	for object in jsonObject:
		veequalizerPreset = object['veequalizer_preset']
		
		title = veequalizerPreset['name']
		
		if title is None:
			title = 'Custom'
		
		slidersString = json.dumps(veequalizerPreset['entries'])
		
		addLink(title.encode("utf-8"), slidersString.encode("utf-8"), MODE_VEEQUALIZER_PLAY, '', authenticityToken)
		
	xbmcplugin.endOfDirectory(int(sys.argv[1]))



def getThumbUrl(identifier):
	
	return 'http://files.putpat.tv/artwork/channelgraphics/' + str(identifier) + '/channellogo_invert_500.png'



def search():

	query = keyboard('Titel')
	
	if query:
		url = plugin.url_for('search_result', search_string=search_string)
		plugin.redirect(url)



def getJsonObject(url, postJson = None):
	
	postData = None
	
	if postJson != None:
		postData = json.dumps(postJson, separators=(',',':'))
	
	request = urllib2.Request(url, postData, {'Content-Type': 'application/json'})
	response = urllib2.urlopen(request)
	response = opener.open(url, postData)
	data = response.read()
	response.close()
	
	cookieJar.save(COOKIEFILE, ignore_discard = True)
	
	result = None
	
	try:
		result = json.loads(data)
	except: pass
	
	return result



def search(query):
	
	searchResult = getJsonObject(baseurl + '/ws.json?method=Veequalizer.completer&searchterm=' + urllib.urlencode(query))
	
	for artist in searchResult['artists']:
		print ""
	
	for tag in searchResult['tags']:
		print ""
	
	for mood in searchResult['moods']:
		print ""
	
	for dynamicTag in searchResult['dynamic_tags']:
		print ""



def addClipsToPlaylist(clips, playlist):
	
	for object in clips:
		clip = object['clip']
		asset = clip['asset']
		tokens = clip['tokens']
		
		title = asset['title']
		artist = asset['display_artist_title']
		
		try:
			album = asset['album']
			albumId = album['id']
		except:
			albumId = None
		
		if qualitySetting == '1':
			videoUrl = tokens['low']
				
		elif qualitySetting == '0':
			videoUrl = tokens['preview']
			
		else:
			videoUrl = tokens['medium']
			
		
		# Create a playable url out of the videoUrl
		match_token = re.compile('token=(.+?)=').findall(videoUrl)
		token = '?token=' + match_token[0] + '='
		
		match_mp4 = re.compile('mp4(.+?)mp4').findall(videoUrl)
		mp4 = 'mp4' + match_mp4[0] + 'mp4'

		url = 'rtmp://tvrlfs.fplive.net/tvrl/ playpath=' + mp4 + token + ' swfurl=http://files.putpat.tv/putpat_player/231/PutpatPlayer.swf swfvfy=true pageUrl=http://www.putpat.tv/'
		
		# Create the cover url
		coverUrl = ''
		
		if albumId is not None:
			albumId = string.zfill(albumId, 7)
			albumIdFolder = albumId[0:5]
			coverUrl = 'http://files.putpat.tv/artwork/album_covers/' + albumIdFolder + '/' + albumId + '/' + albumId + '_front.jpg'
		
		
		if artist is None:
			artist = ''
		
		if title is None:
			title = ''
		
		listItem = xbmcgui.ListItem(artist + ' - ' + title, thumbnailImage = coverUrl)
		playlist.add(url, listItem)



def createPlaylist(clips):
	
	playlist = xbmc.PlayList(1)
	playlist.clear()
	
	addClipsToPlaylist(clips, playlist)
	
	return playlist



def getClips(url):
	
	return getJsonObject(url)



def getVeequalizerClips(sliders, history = None):
	
	url = baseurl + '/ws.json?method=Veequalizer.clips&requester=fetchClips'
	
	if history is None:
		history = []
	
	params = {}
	params['sliders'] = sliders
	params['maxClips'] = 5
	params['history'] = history
	params['streaming_method'] = streamingMethod
	# Milliseconds from 01.01.1970 / 40
	milliseconds = int(round(time.time() * 1000))
	params['start_time'] = milliseconds / 40
	
	postObject = {}
	postObject['params'] = params
	postObject['authenticity_token'] = authenticityToken
	
	return getJsonObject(url, postObject)



def clearPlaylistAndStart(clips):
	
	playlist = createPlaylist(clips)
	#xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, playlist[0])
	listItem = xbmcgui.ListItem('', thumbnailImage = '')
	xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=False, listitem=listItem)
	xbmc.Player().play(playlist)
	
	return playlist



def play(url):
	
	parameter = getParams(url)
	channelId = int(parameter['channelId'])
	
	clips = getClips(url)
	playlist = clearPlaylistAndStart(clips)
	monitorPlayback(playlist, clips = clips, url = url, channelId = channelId)



def veequalizerPlay(slidersString):
	
	sliders = json.loads(slidersString)
	clips = getVeequalizerClips(sliders)
	playlist = clearPlaylistAndStart(clips)
	monitorPlayback(playlist, clips = clips, sliders = sliders)



def monitorPlayback(playlist, clips = None, url = None, sliders = None, channelId = 0):
	
	# Set a loop to wait for positive confirmation of playback
	count = 0
	while not xbmc.Player().isPlaying():
		print 'Not playing yet...sleep for 2'
		count = count + 2
		if count >= 20:
			return
		else:
			time.sleep(2)
	
	xbmc.executebuiltin('ActivateWindow(fullscreeninfo)')
	time.sleep(5)
	xbmc.executebuiltin('ActivateWindow(fullscreenvideo)')
	
	# Counter for refreshing. This is only done all 30 seconds
	timeCounter = 0
	sleepTime = 5
	osdTime = 5
	exitRetryTime = 2
	
	lastPlaylistPosition = 0
	
	# Loop while playing
	allClips = clips
	
	exitCounter = 0
	
	while exitCounter < 1:
		if xbmc.Player().isPlaying():
			exitCounter = 0
		else:
			exitCounter = exitCounter + 1
		
		if 0 == exitCounter:
			currentPlaylistPosition = playlist.getposition()
			
			if lastPlaylistPosition != currentPlaylistPosition:
				# Tell Putpat that we did Play the last song
				lastClip = allClips[lastPlaylistPosition]
				sendClipToHistory(lastClip, channelId)
				
				lastPlaylistPosition = currentPlaylistPosition
				
				# Wait a bit, so the list item is refreshed
				#time.sleep(2)
				#timeCounter = timeCounter + 2
				
				#if xbmc.Player().isPlaying():
				#	xbmc.executebuiltin('XBMC.ActivateWindow(fullscreeninfo)')
				#
				#time.sleep(osdTime)
				#timeCounter = timeCounter + osdTime
				#
				#if xbmc.Player().isPlaying():
				#	xbmc.executebuiltin('XBMC.Action(PreviousMenu)')
			
			if timeCounter >= 30:
				timeCounter = 0
				
				if (currentPlaylistPosition + 1) >= playlist.size() - 2:
					newClips = None
					
					if url is not None:
						# Normal channel
						newClips = getClips(url)
						newClips = clipsWithoutIntersection(newClips, allClips)
					
					elif sliders is not None:
						# Veequalizer
						history = getLastTwoAssetIds(allClips)
						newClips = getVeequalizerClips(sliders, history)
					
					if xbmc.Player().isPlaying() and newClips is not None and len(newClips) > 2:
						addClipsToPlaylist(newClips, playlist)
						allClips.extend(newClips)
						print 'Just added new clips. Count: ' + str(len(newClips))
					
			timeCounter = timeCounter + sleepTime
			time.sleep(sleepTime)
			
		else:
			timeCounter = timeCounter + exitRetryTime
			time.sleep(exitRetryTime)
	
	playlist.clear()
	print 'Playback stopped'



def sendClipToHistory(object, channelId):
	
	clip = object['clip']
	asset = clip['asset']
	videoFile = asset['video_file']
	duration = videoFile['duration'] / 40.0
	
	params = {}
	params['assetId'] = clip['asset_id']
	params['channelId'] = channelId
	params['secondsPlayed'] = duration
	params['finished'] = True
	try:
		params['onDemand'] = clip['on_demand']
	except:
		pass
	
	
	postObject = {}
	postObject['params'] = params
	postObject['authenticity_token'] = authenticityToken
	print postObject
	result = getJsonObject(baseurl + '/ws.json?method=User.addVideoHistoryItem', postObject)
	print result



def getLastTwoAssetIds(clips):
	
	result = []
	
	maxIndex = len(clips) - 1
	
	for i in range(maxIndex, maxIndex - 2, -1):
		object = clips[i]
		clip = object['clip']
		assetId = clip['asset_id']
		
		result.append(assetId)
	
	return result



def clipsWithoutIntersection(newClips, oldClips):
	
	result = []
	
	for newObject in newClips:
		newClip = newObject['clip']
		newAssetId = newClip['asset_id']
		
		alreadyThere = False
		
		for oldObject in oldClips:
			oldClip = oldObject['clip']
			oldAssetId = oldClip['asset_id']
			
			if newAssetId == oldAssetId:
				alreadyThere = True
				break
		
		if alreadyThere == False:
			result.append(newObject)
	
	return result



def getParams(paramstring):

	result = []
	
	
	if len(paramstring) >= 2:
		params = paramstring
		cleanedparams = params.replace('?','')
		
		if (params[len(params) - 1] == '/'):
			params = params[0:len(params) - 2]
		
		pairsofparams = cleanedparams.split('&')
		result = {}
		
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			
			if (len(splitparams)) == 2:
				result[splitparams[0]] = splitparams[1]
	
	return result



def addLink(name, url, mode, iconimage, authToken, additionalInfos = {}):

	u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&authenticityToken=" + urllib.quote_plus(authToken)
	liz = xbmcgui.ListItem(name, iconImage = "DefaultVideo.png", thumbnailImage = iconimage)
	additionalInfos['title'] = name
	liz.setInfo(type = "Video", infoLabels = additionalInfos)
	liz.setProperty('IsPlayable', 'true')
	xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz)
	
	return liz



def addDir(name, url, mode, iconimage, authToken, additionalInfos = {}):

	u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&authenticityToken=" + urllib.quote_plus(authToken)
	liz = xbmcgui.ListItem(name, iconImage = "DefaultFolder.png", thumbnailImage = iconimage)
	additionalInfos['title'] = name
	liz.setInfo(type = "Video", infoLabels = additionalInfos)
	xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = True)
	
	return liz



params = getParams(sys.argv[2])

url = None
name = None
mode = None
authenticityToken = ''

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
	
try:
	name = urllib.unquote_plus(params["name"])
except:
	pass
	
try:
	mode = int(params["mode"])
except:
	pass

try:
	authenticityToken = urllib.unquote_plus(params["authenticityToken"])
except:
	pass

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)
print "AuthenticityToken: " + str(authenticityToken)

if mode == None or mode == MODE_ROOT:
	showRootMenu()

elif mode == MODE_PLAY:
	play(url)

elif mode == MODE_VEEQUALIZER:
	showVeequalizerPresets()

elif mode == MODE_VEEQUALIZER_PLAY:
	veequalizerPlay(url)
