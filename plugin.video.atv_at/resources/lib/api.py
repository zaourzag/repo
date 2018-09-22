# -*- coding: utf-8 -*-

import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
import re
import json
import requests
from . import gui
#import playlistmaker
#import xbmcvfs


addon = xbmcaddon.Addon()
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
icon = os.path.join(addonPath, 'icon.png')
spPIC = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
#stored_Videos = xbmc.translatePath(os.path.join("special://xbmc"+os.sep+"STREAMS_atv"+os.sep)).encode('utf-8').decode('utf-8')
preferredStreamType = addon.getSetting("streamSelection")
showCompleteEPISODES = addon.getSetting("show.all_episodes") == 'true'

#if not xbmcvfs.exists(stored_Videos):
#	xbmcvfs.mkdirs(stored_Videos)

__URL_MAIN_PAGE = 'https://atv.at'
__HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Encoding': 'gzip, deflate','Connection': 'keep-alive','Upgrade-Insecure-Requests': '1'}
headerFIELDS = "User-Agent=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F67.0.3396.62%20Safari%2F537.36"


def USER_from_austria():
	try:
		return 'window.is_not_geo_ip_blocked = true' in requests.get('https://videos.atv.cdn.tvnext.tv/blocked/detect.js', headers=__HEADERS, verify=True, timeout=30).text
	except:
		return False


def list_series():
	url = __URL_MAIN_PAGE+'/mediathek/'
	html = gui.makeREQUEST(url)
	clusters = re.findall('<li class="program">(.*?)</li>', html, re.DOTALL)
	for cluster in clusters:
		try:
			if '<div class="video_indicator">' in cluster:
				url = re.compile(r'href=["\'](.*?)["\']', re.DOTALL).findall(cluster)[0]
				image = re.compile(r'<img src=["\'](.*?)teaser_image_file(.*?)["\'] alt=', re.DOTALL).findall(cluster)
				pic1 = image[0][0]
				pic2 = image[0][1]
				if pic1.startswith('https://static.atv.cdn.tvnext.tv/dynamic/get_asset_resized.php') and 'path=format_pages%252F' in pic1:
					thumb = "https://static.atv.cdn.tvnext.tv/static/assets/cms/format_pages/teaser_image_file"+pic2.split('&amp;percent')[0].replace('%252F', '/')
				else:
					thumb = spPIC+"empty.jpg"
				title = re.compile(r'<h3 class=["\']program_title["\']>(.*?)</h3>', re.DOTALL).findall(cluster)[0]
				title = gui.cleanupTEXT(title)
				gui.add_folder(title, thumb, {'mode': 'cluster', 'url': url})
		except:
			gui.debug("(list_series) Fehler-in-Cluster : {0}".format(str(cluster)))
	gui.end_listing()


def list_cluster(url):
	html = gui.makeREQUEST(url)
	if not list_seasons(html):
		list_videos(html)
	gui.end_listing()


def list_seasons(html):
	index_seasons = html.find('<select class="select jsb_ jsb_Select" data-jsb=')
	if index_seasons != -1:
		try:
			pic = re.compile(r'<meta property=["\']og:image["\'] content=["\'](https://static.atv.cdn.tvnext.tv/static/assets/cms/format_pages/teaser_image_file/.*?)["\'] />', re.DOTALL).findall(html)[0]
			thumb = pic.split('?cb=')[0]
		except:
			thumb = spPIC+"empty.jpg"
		seasons_block = html[index_seasons:html.find('</select>', index_seasons)]
		seasons = re.findall('<option.*?value="(.*?)">(.*?)</option>', seasons_block, re.DOTALL)
		for url, title in seasons:
			title = gui.cleanupTEXT(title)
			gui.add_folder(title, thumb, {'mode': 'episodes', 'url': url})
		return True
	return False


def list_episodes(url):
	html = gui.makeREQUEST(url)
	list_videos(html)
	gui.end_listing()


def list_videos(html):
	videoIsolated_List1 = set()
	videoIsolated_List2 = set()
	videos_2 = re.findall('<li class="teaser">(.*?)</li>', html, re.DOTALL)
	try:
		tvshowtitle = re.compile(r'<h3 class=["\']title uppercase one_line["\']>.+?["\']>(.*?)</a></h3>', re.DOTALL).findall(html)[0].strip()
		tvshowtitle = gui.cleanupTEXT(tvshowtitle)
	except: tvshowtitle = ""
	try: 
		desc = re.compile(r'<h2 class=["\']title["\']>(.*?)<div class=["\']mod_teasers four all_rows jsb_ jsb_ExpandableTeaser["\']', re.DOTALL).findall(html)[0]
		desc = "- "+desc.split('</h2>')[0]+' -\n'+desc.split('</h2>')[1].split('</div>')[0]
		plot = re.sub(r'\<.*?\>', '', desc)
		plot = gui.cleanupTEXT(plot)
	except: plot = ""
	idNumber = "##### Alle Episoden auf einer Seite - Nicht eingeschaltet ! #####"
	if showCompleteEPISODES:
		index_VideoID = html.find('<div class="more jsb_ jsb_MoreTeasersButton" data-jsb="')
		if index_VideoID != -1:
			url_get_ID = html[index_VideoID + 55:html.find('"', index_VideoID + 55)]
			if url_get_ID.startswith('url='):
				url_get_ID = url_get_ID[4:]
			idNumber = url_get_ID.replace('%3A', ':').replace('%2F', '/').replace('%3F', '?').replace('%3D', '=').replace('https://atv.at/uri/fepe/', '').split('/')[0].strip()
		else: idNumber = "##### ID - Nicht gefunden ! #####"
	gui.debug("(list_videos[1]) idNumber : {0}".format(str(idNumber)))
	pageNumber = int(1)
	if not "#####" in idNumber:
		while pageNumber < int(6):
			urlVideos_1 = "https://atv.at/uri/fepe/"+idNumber+"/?page="+str(pageNumber)
			content = gui.makeREQUEST(urlVideos_1)
			gui.debug("(list_videos[1]) urlVideos_1 : {0}".format(urlVideos_1))
			if '<div class="more jsb_ jsb_MoreTeasersButton" data-jsb="' in content:
				pageNumber += int(1)
			else:
				pageNumber += int(4)
			videos_1 = re.findall('<li class="teaser">(.*?)</li>', content, re.DOTALL)
			for video in videos_1:
				try:
					if '<div class="video_indicator">' in video:
						url = re.compile(r'href=["\'](.*?)["\'] ', re.DOTALL).findall(video)[0]
						image = re.compile(r'<img src=["\'](.*?)teaser_image_file(.*?)["\'] width=', re.DOTALL).findall(video)
						pic1 = image[0][0]
						pic2 = image[0][1]
						if pic1.startswith('https://static.atv.cdn.tvnext.tv/dynamic/get_asset_resized.php'):
							if 'path=detail_pages%252F' in pic1:
								thumb = "https://static.atv.cdn.tvnext.tv/static/assets/cms/detail_pages/teaser_image_file"+pic2.split('&amp;percent')[0].replace('%252F', '/')
							elif 'path=media_items%252F' in pic1:
								thumb = "https://static.atv.cdn.tvnext.tv/static/assets/cms/media_items/teaser_image_file"+pic2.split('&amp;percent')[0].replace('%252F', '/')
						else:
							thumb = pic1+'teaser_image_file'+pic2.split('?cb=')[0]
						title = re.compile(r'class=["\']title["\']>(.*?)</', re.DOTALL).findall(video)[0]
						title = gui.cleanupTEXT(title)
						season = ""
						episode = ""
						if "staffel-" in url:
							try: season = url.split('https://atv.at/')[1].split('staffel-')[-1].split('/')[0].strip() # https://atv.at/bauer-sucht-frau-staffel-14/die-hofwochen-folge-12/d1958945/
							except: season = ""
						if "folge-" in url:
							try: episode = url.split('https://atv.at/')[1].split('folge-')[-1].split('/')[0].split('-')[0].strip() # https://atv.at/bauer-sucht-frau-staffel-2/folge-13/v1642204/
							except: episode = ""
						if "episode-" in url and episode=="":
							try: episode = url.split('https://atv.at/')[1].split('episode-')[-1].split('/')[0].split('-')[0].strip() # https://atv.at/bauer-sucht-frau-staffel-3/episode-14-event-teil-1/v1640552/
							except: episode = ""
						if url in videoIsolated_List1:
							continue
						videoIsolated_List1.add(url)
						gui.debug("(list_videos[1]) Serie : {0}".format(tvshowtitle))
						gui.debug("(list_videos[1]) Titel : {0}".format(title))
						gui.debug("(list_videos[1]) Season : {0} / Episode : {1}".format(season, episode))
						gui.debug("(list_videos[1]) Thumb : {0}".format(thumb))
						gui.add_video(title, tvshowtitle, season, episode, plot, thumb, {'mode': 'collect_video_parts', 'url': url, 'photo': thumb})
				except:
					gui.debug("(list_videos[1]) Error-in-Video-1 : {0}".format(str(video)))
	if videos_2 !="":
		for video in videos_2:
			try:
				if '<div class="video_indicator">' in video:
					url = re.compile(r'href=["\'](.*?)["\'] ', re.DOTALL).findall(video)[0]
					image = re.compile(r'<img src=["\'](.*?)teaser_image_file(.*?)["\'] width=', re.DOTALL).findall(video)
					pic1 = image[0][0]
					pic2 = image[0][1]
					if pic1.startswith('https://static.atv.cdn.tvnext.tv/dynamic/get_asset_resized.php'):
						if 'path=detail_pages%252F' in pic1:
							thumb = "https://static.atv.cdn.tvnext.tv/static/assets/cms/detail_pages/teaser_image_file"+pic2.split('&amp;percent')[0].replace('%252F', '/')
						elif 'path=media_items%252F' in pic1:
							thumb = "https://static.atv.cdn.tvnext.tv/static/assets/cms/media_items/teaser_image_file"+pic2.split('&amp;percent')[0].replace('%252F', '/')
					else:
						thumb = pic1+'teaser_image_file'+pic2.split('?cb=')[0]
					title = re.compile(r'class=["\']title["\']>(.*?)</', re.DOTALL).findall(video)[0]
					title = gui.cleanupTEXT(title)
					season = ""
					episode = ""
					if "staffel-" in url:
						try: season = url.split('https://atv.at/')[1].split('staffel-')[-1].split('/')[0].strip() # https://atv.at/bauer-sucht-frau-staffel-14/die-hofwochen-folge-12/d1958945/
						except: season = ""
					if "folge-" in url:
						try: episode = url.split('https://atv.at/')[1].split('folge-')[-1].split('/')[0].split('-')[0].strip() # https://atv.at/bauer-sucht-frau-staffel-2/folge-13/v1642204/
						except: episode = ""
					if "episode-" in url and episode=="":
						try: episode = url.split('https://atv.at/')[1].split('episode-')[-1].split('/')[0].split('-')[0].strip() # https://atv.at/bauer-sucht-frau-staffel-3/episode-14-event-teil-1/v1640552/
						except: episode = ""
					Wanted = url.split('https://atv.at/')[1].split('/')[0][:6]
					gui.debug("(list_videos[2]) Wanted-URL : {0}".format(Wanted))
					if (url in videoIsolated_List1 or 'aufruf' in url.lower() or not Wanted in url):
						continue
					if url in videoIsolated_List2:
						continue
					videoIsolated_List2.add(url)
					gui.debug("(list_videos[2]) Serie : {0}".format(tvshowtitle))
					gui.debug("(list_videos[2]) Titel : {0}".format(title))
					gui.debug("(list_videos[2]) Season : {0} / Episode : {1}".format(season, episode))
					gui.debug("(list_videos[2]) Thumb : {0}".format(thumb))
					gui.add_video(title, tvshowtitle, season, episode, plot, thumb, {'mode': 'collect_video_parts', 'url': url, 'photo': thumb})
			except:
				gui.debug("(list_videos[2]) Error-in-Video-2 : {0}".format(str(video)))
	# now look for more videos button
	if "#####" in idNumber:
		index_more_videos = html.find('<div class="more jsb_ jsb_MoreTeasersButton" data-jsb="')
		if index_more_videos != -1:
			url_more_videos = html[index_more_videos + 55:html.find('"', index_more_videos + 55)]
			if url_more_videos.startswith('url='):
				url_more_videos = url_more_videos[4:]
			gui.add_folder(gui.translation(30601), spPIC+"nextpage.png", {'mode': 'following_page', 'url': url_more_videos})


def get_video_url(url, photo):
	videoIsolated_M3U8 = set()
	videoIsolated_MP4 = set()
	book = []
	COMBINATION = []
	ASSEMBLY = []
	firstURL = ""
	number_MP4 = 0
	number_M3U8 = 0
	pos_MP4 = ""
	pos_M3U8 = ""
	count = 0
	lastCODE = ('_2.mp4', '_3.mp4', '_4.mp4', '_5.mp4', '_6.mp4', '_7.mp4', '_8.mp4', '_9.mp4')
	html = gui.getUrl(url, "GET", False, False, __HEADERS)
	try: 
		desc = re.compile('<p[^>]*>([^<]+)<', re.DOTALL).findall(html)[0]
		plot = gui.cleanupTEXT(desc)
	except: plot = ""
	match = re.search('FlashPlayer" data-jsb="(.*?)">', html)
	if match:
		content = gui.cleanupTEXT(match.group(1))
		DATA = json.loads(content)
		parts = DATA['config']['initial_video']['parts']
		geoblocked_parts = 0
		single_videoURL = False
		for part in parts:
			videotitle = part['tracking']['nurago']['videotitle'].replace('_', ' ').strip() # Bauer sucht Frau Die Hofwochen - Folge 5
			tvshowtitle = part['tracking']['nurago']['programname'].strip() # Bauer sucht Frau
			title = part['tracking']['nurago']['episodename'].strip() # Folge 14 - Die Hofwochen
			NRS_title = part['title'].strip() # Die Hofwochen - Folge 5 1/7
			season = ""
			episode = ""
			if part['tracking']['nurago']['seasonid'] and part['tracking']['nurago']['seasonid'] !="":
				try: season = part['tracking']['nurago']['seasonid'].strip() # 14
				except: season = ""
			if part['tracking']['nurago']['clipreferer'] and "staffel-" in part['tracking']['nurago']['clipreferer'] and season=="":
				try: season = part['tracking']['nurago']['clipreferer'].split('https://atv.at/')[1].split('staffel-')[-1].split('/')[0].strip() # https://atv.at/bauer-sucht-frau-staffel-14/die-hofwochen-folge-12/d1958945/
				except: season = ""
			if part['tracking']['nurago']['episodename'] and "Folge " in part['tracking']['nurago']['episodename']:
				try: episode = part['tracking']['nurago']['episodename'].split('Folge')[1].split('-')[0].split(':')[0].strip() # Folge 14 - Die Hofwochen
				except: episode = ""
			if part['tracking']['nurago']['episodename'] and "Episode " in part['tracking']['nurago']['episodename'] and episode=="":
				try: episode = part['tracking']['nurago']['episodename'].split('Episode')[1].split('-')[0].split(',')[0].strip() # Episode 2
				except: episode = ""
			duration = int(part['tracking']['nurago']['videoduration']) # 1250
			thumb = part['preview_image_url'].split('?cb=')[0].strip() # https://static.atv.cdn.tvnext.tv/static/assets/cms/media_items/teaser_image_file/1930300.jpg
			if not videotitle in book and count < 1:
				count += 1
				gui.log("(get_video_url) -------------------- VideoTitel : {0} --------------------".format(gui.py2_encode(videotitle)))
			gui.debug("(get_video_url) Serie : {0}".format(tvshowtitle))
			gui.debug("(get_video_url) Titel : {0}".format(NRS_title))
			gui.debug("(get_video_url) Season : {0} / Episode : {1}".format(season, episode))
			gui.debug("(get_video_url) Dauer (seconds) : {0}".format(str(duration)))
			gui.debug("(get_video_url) Thumb : {0}".format(thumb))
			if part['is_geo_ip_blocked']:
				geoblocked_parts += 1
			streams = part['sources']
			if not streams:
				continue
			MP4_Part = streams[1]['src'].replace('blocked-', '')
			M3U8_Part = streams[0]['src']
			if any(x in MP4_Part for x in lastCODE):
				firstURL = MP4_Part.split('_')[0]
			elif MP4_Part.startswith('https://multiscreen.atv.cdn.tvnext.tv'):
				firstURL = MP4_Part.split('.mp4')[0]
			for stream in streams:
				if MP4_Part:
					if MP4_Part in videoIsolated_MP4:
						continue
					videoIsolated_MP4.add(MP4_Part)
					number_MP4 += 1
					pos_MP4 = str(number_MP4)+': '
					MP4_Url = MP4_Part
					gui.debug("(get_video_url) MP4_Url : {0}".format(MP4_Url))
				if M3U8_Part:
					if M3U8_Part in videoIsolated_M3U8:
						continue
					videoIsolated_M3U8.add(M3U8_Part)
					number_M3U8 += 1
					pos_M3U8 = str(number_M3U8)+': '
					M3U8_Url = M3U8_Part
					gui.debug("(get_video_url) M3U8_Url : {0}".format(M3U8_Url))
				else:
					pos_M3U8 = str(number_M3U8)+': '
					M3U8_Url = ""
					gui.debug('(get_video_url) -------------------- M3U8_Url : KEINE passende "m3u8" gefunden !!! --------------------')
				COMBINATION.append([pos_MP4, MP4_Url, pos_M3U8, M3U8_Url, videotitle, tvshowtitle, title, NRS_title, season, episode, photo, thumb, duration])
		for pos_MP4, MP4_Url, pos_M3U8, M3U8_Url, videotitle, tvshowtitle, title, NRS_title, season, episode, photo, thumb, duration in COMBINATION:
			ENDnum_MP4 = str(pos_MP4).split(':')[0]
			MP4_Video = str(pos_MP4)+MP4_Url
			M3U8_Video = str(pos_M3U8)+M3U8_Url
			gui.log("(get_video_url) Video  -  MP4 = {0}".format(MP4_Video))
			gui.log("(get_video_url) Video - M3U8 = {0}".format(M3U8_Video))
			if 'https://multiscreen.atv.cdn.tvnext.tv' in firstURL and (M3U8_Url == "" or preferredStreamType == "0"):
				if MP4_Video.startswith('1: rtsp:'):
					single_videoURL = MP4_Video.replace(MP4_Video, firstURL+'.mp4')
				elif not MP4_Video.startswith('1: rtsp:') and 'rtsp://' in MP4_Video:
					single_videoURL = MP4_Video.replace(MP4_Video, firstURL+'_'+ENDnum_MP4+'.mp4')
				else:
					single_videoURL = MP4_Url
			elif (firstURL == ""  or preferredStreamType == "1") and M3U8_Url != "":
				if not "chunklist" in M3U8_Url:
					bestQuality = gui.getUrl(M3U8_Url, "GET", False, False, __HEADERS)
					try:
						newM3U8 = re.compile(r'(https?://.*?.m3u8)', re.DOTALL).findall(bestQuality)[0].replace('blocked-', '')
						single_videoURL = newM3U8
					except: single_videoURL = M3U8_Url
				else:
					single_videoURL = M3U8_Url
			#elif firstURL == "" and MP4_Url.startswith('rtsp:'):
				#return playlistmaker.generateXSPF(COMBINATION)
			ASSEMBLY.append([single_videoURL, title, NRS_title, tvshowtitle, season, episode, plot, photo, thumb, duration])
		if geoblocked_parts == len(parts) and not USER_from_austria():
			return xbmcgui.Dialog().notification(gui.translation(30521), gui.translation(30522), icon, 10000)
		if single_videoURL:
			return ASSEMBLY
	return xbmcgui.Dialog().notification(gui.translation(30523), gui.translation(30524), icon, 10000)
