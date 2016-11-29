import re
import xbmcgui,xbmcplugin
import sys
import xbmc
import json
from resources.lib import nightcrawler
try:
    import urllib.parse as compat_urllib_parse
except ImportError:  # Python 2
    import urllib as compat_urllib_parse


class Client(nightcrawler.HttpClient):
    CHANNEL_ID_LIST = ['pro7', 'sat1', 'kabel1', 'sixx', 'sat1gold', 'prosiebenmaxx']
    CHANNEL_IDS_STRING = '|'.join(CHANNEL_ID_LIST)
    CHANNEL_DATA = {'pro7': {'name': u'ProSieben'},
                    'sat1': {'name': u'SAT.1'},
                    'kabel1': {'name': u'kabel eins'},
                    'sixx': {'name': u'sixx'},
                    'sat1gold': {'name': u'SAT.1 Gold'},
                    'prosiebenmaxx': {'name': u'ProSieben MAXX'}}

    REGEX_VIDEO = re.compile(
        r'/mega-app/v2/(?P<channel_id>%s)/(tablet|phone)/(?P<type>video)/(?P<video_id>\d+)' % CHANNEL_IDS_STRING)
    REGEX_FORMAT = re.compile(
        r'/mega-app/v2/(?P<channel_id>(%s))/(tablet|phone)/format/show/(%s):(?P<format_id>\d+)' % (
            CHANNEL_IDS_STRING, CHANNEL_IDS_STRING))

    def __init__(self):
        nightcrawler.HttpClient.__init__(self, default_header={'User-Agent': '7TV-App-Android-v1.7.0.8-fb8e88f',
                                                               'Accept-Language': 'en_US',
                                                               'Accept-Encoding': 'gzip'})

        self._device = 'tablet'  # 'phone'
        pass

    def _request(self, url, method='GET', headers=None, post_data=None, params=None, allow_redirects=True):
        if not params:
            params = {}
            pass

        if not headers:
            headers = {}
            pass

        response = super(Client, self)._request(url, method, self._default_header, post_data, params, allow_redirects)

        if method != 'HEAD':
            return response.json()

        return response

    def _screen_objects_to_result(self, json_data, result):
        for json_item in json_data:
            title = nightcrawler.utils.strings.to_unicode(json_item.get('title', json_item.get('video_title', '')))
            screen_objects = json_item.get('screen_objects', [])

            if title and screen_objects and len(screen_objects) > 0:
                result[title] = {}
                self._screen_objects_to_result(screen_objects, result[title])

                # remove empty lists
                if len(result[title]['items']) == 0:
                    del result[title]
                    pass
                pass
            elif screen_objects:
                self._screen_objects_to_result(json_item.get('screen_objects', []), result)
                pass
            elif title:
                if 'items' not in result:
                    result['items'] = []
                    pass

                item = {'title': title}

                format_title = nightcrawler.utils.strings.to_unicode(json_item.get('format_title', ''))
                if format_title is None:
                    format_title = ''
                    pass

                subtitle = nightcrawler.utils.strings.to_unicode(json_item.get('subtitle', ''))
                if subtitle is None:
                    subtitle = ''
                    pass

                # test for video
                video_match = self.REGEX_VIDEO.match(json_item.get('link', ''))
                if video_match:
                    item.update({'type': 'video',
                                 'channel': video_match.group('channel_id'),
                                 'id': json_item['id'],
                                 'images': {'thumbnail': json_item.get('image_url', '')}})

                    # duration
                    duration = int(json_item.get('duration', 0))
                    if duration > 0:
                        item['duration'] = duration
                        pass

                    # published
                    published = json_item.get('start', '')
                    if published:
                        published = nightcrawler.utils.datetime.parse(published)
                        item['published'] = str(published)
                        pass

                    # format based on subtitle or format_title
                    if subtitle:
                        item['format'] = item['title']
                        item['title'] = subtitle
                        pass
                    elif format_title:
                        item['format'] = format_title
                        pass

                    # try to match season and episode
                    season_match = re.search(r'Staffel (?P<season>\d+)', item['title'])
                    if season_match:
                        item['season'] = int(season_match.group('season'))
                        pass
                    episode_match = re.search(r'(Episode|Folge) (?P<episode>\d+)', item['title'])
                    if episode_match:
                        item['episode'] = int(episode_match.group('episode'))
                        pass

                    result['items'].append(item)
                    continue
                    pass

                # test for format
                format_match = self.REGEX_FORMAT.match(json_item.get('link', ''))
                if format_match:
                    item.update({'type': 'format',
                                 'channel': format_match.group('channel_id'),
                                 'id': json_item['id'],
                                 'images': {'thumbnail': json_item.get('image_url', '')}})
                    result['items'].append(item)
                    continue
                    pass
                pass
            pass
        pass

    def _objects_to_result(self, json_data):
        objects = json_data.get('objects', [])
        result = {}
        self._screen_objects_to_result(objects, result)
        return result

    def _screen_to_result(self, json_data, result):
        screen = json_data.get('screen', {})
        self._screen_objects_to_result(screen.get('screen_objects', []), result)
        return result

    def get_homepage(self, channel_id):
        url = "http://contentapi.sim-technik.de/mega-app/v2/%s/%s/homepage" % (channel_id, self._device)
        json_data = self._request(url)

        result = {}
        return self._screen_to_result(json_data, result)

    def get_formats(self, channel_id):
        url = 'http://contentapi.sim-technik.de/mega-app/v2/%s/%s/format' % (channel_id, self._device)
        json_data = self._request(url)
        result = {}
        return self._screen_to_result(json_data, result)

    def get_format_content(self, channel_id, format_id):
        # http://contentapi.sim-technik.de/mega-app/v2/pro7/phone/format/show/pro7:789
        url = 'http://contentapi.sim-technik.de/mega-app/v2/%s/%s/format/show/%s' % (
            channel_id,
            self._device,
            format_id)

        json_data = self._request(url)
        result = {}
        return self._screen_to_result(json_data, result)

    def get_format_videos(self, channel_id, format_id, clip_type='full', page=1, per_page=50):
        def _load_videos(_page):
            # http://contentapi.sim-technik.de/mega-app/v2/tablet/videos/format/pro7:505?clip_type=full&page=1&per_page=50
            url = 'http://contentapi.sim-technik.de/mega-app/v2/%s/videos/format/%s' % (self._device, format_id)
            params = {'clip_type': clip_type,
                      'page': str(_page),
                      'per_page': str(per_page)}
            return self._request(url, params=params)

        current_page_result = _load_videos(page)
        result = self._objects_to_result(current_page_result)

        # test next page
        next_page_result = _load_videos(page + 1)
        next_page_result = self._objects_to_result(next_page_result)
        if len(next_page_result.get('items', [])) > 0:
            result['continue'] = True
            pass

        return result

    def search(self, query):
        # http://contentapi.sim-technik.de/mega-app/v2/phone/search?query=halligalli
        url = 'http://contentapi.sim-technik.de/mega-app/v2/tablet/search'
        json_data = self._request(url, params={'query': query})
        result = {}
        return self._screen_to_result(json_data, result)

    def get_new_videos(self, format_ids=None):
        if not format_ids:
            format_ids = []
            pass

        format_id_string = ','.join(format_ids)
        format_id_string = '[' + format_id_string + ']'
        url = 'http://contentapi.sim-technik.de/mega-app/v2/tablet/videos/favourites'
        json_data = self._request(url, params={'ids': format_id_string})

        # wrap the result into a 'screen' object so we can use common routines
        json_data = {'screen': json_data}
        result = {}
        return self._screen_to_result(json_data, result)

    def get_video_url(self, video_id):
        # first request the web url of the video
        url = 'http://contentapi.sim-technik.de/mega-app/v2/pro7/phone/video/%s' % video_id
        print("get_video_url url :"+url)
        data = self._request(url)
        print("get_video_url Data :")
        print(data)
        client_location = nightcrawler.utils.strings.to_utf8(
            data.get('screen', {}).get('screen_objects', [{'video_link': ''}])[0].get('video_link', ''))

        url = 'https://vas.sim-technik.de/vas/live/v2/videos'
        params = {'access_token': 'seventv-app',
                  'client_location': client_location,
                  'client_name': '7tv-app',
                  'ids': video_id}
        data = self._request(url, params=params)
        is_protected = False
        if data:
            is_protected = data[0].get('is_protected', False)
            pass

        #access_token = 's''e''v''e''n''t''v''-''w''e''b'
        #access_token = 'prosieben'
        access_token = 'seventv-web'
        salt = '01!8d8F_)r9]4s[qeuXfP%'
        #salt = '0''1''r''e''e''6''e''L''e''i''w''i''u''m''i''e''7''i''e''V''8''p''a''h''g''e''i''T''u''i''3''B'
        # http://hbbtv.prosieben.de/common/js/videocenter.js
        # __PATTERN = 'salt\s*:\s*"01(.+?)"'
        source_id = None

        videos = self._get_video_url(video_id, access_token, "", client_location, salt, source_id)
        print "-----------------------"
        print videos
        print "-----------------------"        

        video_format_dict = {12: {'title': '1280x720@3.1mbps', 'height': 720, 'bitrate': 3100},
                             11: {'title': '1280x720@2.3mbps', 'height': 720, 'bitrate': 2300},
                             10: {'title': '960x540@2.0mbps', 'height': 540, 'bitrate': 2000},
                             9: {'title': '960x540@1.5mbps', 'height': 540, 'bitrate': 1500},
                             8: {'title': '768x432@1.8mbps', 'height': 432, 'bitrate': 1800},
                             7: {'title': '768x432@1.5mbps', 'height': 432, 'bitrate': 1500},
                             6: {'title': '640x360@1.1mbps', 'height': 360, 'bitrate': 1100},
                             5: {'title': '640x360@0.6mbps', 'height': 360, 'bitrate': 600},
                             4: {'title': '480x270@0.4mbps', 'height': 270, 'bitrate': 400},
                             3: {'title': '416x234@0.2mbps', 'height': 234, 'bitrate': 200}}
        
        result = []
        url = None

        for video in videos:
            url = video['url']
            match = re.search('tp(\d+).mp4', url)
            if not match:
                continue
            _id = int(match.group(1))

            video_stream = {'title': video_format_dict[_id]['title'],
                            'sort': [video_format_dict[_id]['height'], video_format_dict[_id]['bitrate']],
                            'video': {'height': video_format_dict[_id]['height']},
                            'uri': url}

            # mark the stream protected
            if is_protected:
                video_stream['is_protected'] = True

            result.append(video_stream)

            #if is_protected:
            #    break#

        # always available
        if not is_protected and url:
            for _id in (3, 4, 5):
                _url = re.sub(r'(.+?)(tp\d+.mp4)(.+)', r'\1tp%02d.mp4\3' % _id, url)
                video_stream = {'title': video_format_dict[_id]['title'],
                                'sort': [video_format_dict[_id]['height'], video_format_dict[_id]['bitrate']],
                                'video': {'height': video_format_dict[_id]['height']},
                                'uri': _url}
                result.append(video_stream)
        elif not result:
            result.append({'is_protected': True})

        return result

    def _get_video_url(self, video_id, access_token, client_name, client_location, salt, source_id=None):
        from hashlib import sha1
        #print "video_id :"+video_id 
        #print "access_token :"+access_token
        #print "client_name :"+client_name
        #print "client_location :"+client_location
        #print "salt :"+salt
        
        adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.adaptive", "properties": ["enabled"]}}')        
        struktur = json.loads(adaptivaddon) 
        is_type=""
        if not "error" in struktur.keys() :            
            if struktur["result"]["addon"]["enabled"]==True:
                is_type="inputstream.adaptive"
        if is_type=="":
          adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.mpd", "properties": ["enabled"]}}')        
          struktur = json.loads(adaptivaddon)           
          if not "error" in struktur.keys() :            
            if struktur["result"]["addon"]["enabled"]==True:
                is_type="inputstream.mpd"                
        if is_type=="":
          dialog = xbmcgui.Dialog()
          nr=dialog.ok("Inputstream", "Inputstream fehlt")
          return ""
        #is_type="inputstream.adaptive"
        #      xy=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.mpd", "properties": ["enabled"]}}')
        #      is_type="inputstream.mpd"
           #dialog = xbmcgui.Dialog()
           #nr=dialog.ok("Inputstream", "Inputstream fehlt")
#           return
        print "source_id : "+str(source_id)        
        if source_id is None:
            json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s?' \
                       'access_token=%s&client_location=%s&client_name=%s' \
                       % (video_id, access_token, client_location, client_name)
            json_data = self._request(json_url, headers={'Accept-Encoding': 'gzip'})
            print "Source ID:"
            print json_data
            print "----------"
            for stream in json_data['sources']:
              if  stream['mimetype']=='application/dash+xml':           
                source_id = stream['id']
            print source_id

        client_id_1 = salt[:2] + sha1(
            ''.join([str(video_id), salt, access_token, client_location, salt, client_name]).encode(
                'utf-8')).hexdigest()
        json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources?' \
                   'access_token=%s&client_location=%s&client_name=%s&client_id=%s' \
                   % (video_id, access_token, client_location, client_name, client_id_1)                                      
        json_data = self._request(json_url, headers={'Accept-Encoding': 'gzip'})
        server_id = json_data['server_id']

        client_id_2 = salt[:2] + sha1(
            ''.join([salt, str(video_id), access_token, server_id, client_location, str(source_id), salt,
                     client_name]).encode('utf-8')).hexdigest()                          
        json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources?' \
                   'access_token=%s&client_location=%s&client_name=%s&' \
                   'client_id=%s&callback=_4ma9f3i3r6l2' \
                   % (video_id, access_token, client_location, client_name, client_id_1)        
        client_name = 'kolibri-1.2.5'    
        client_id = salt[:2] + sha1(''.join([salt, video_id, access_token, server_id,client_location, str(source_id), salt, client_name]).encode('utf-8')).hexdigest()
        url_api_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources/url?%s' % (video_id, compat_urllib_parse.urlencode({
            'access_token': access_token,
            'client_id': client_id,
            'client_location': client_location,
            'client_name': client_name,
            'server_id': server_id,
            'source_ids': str(source_id),
        }))
        print "url_api_url :"+url_api_url
        json_data = self._request(url_api_url, headers={'Accept-Encoding': 'gzip'})
        print json_data        
        data=json_data["sources"][0]["url"]               
        userAgent = 'user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36&Origin=http://www.7tv.de&Referer=http://www.7tv.de/fresh-off-the-boat/25-staffel-2-episode-5-tote-hose-an-halloween-ganze-folge&content-type='
        addon_handle = int(sys.argv[1])
        listitem = xbmcgui.ListItem(path=data)         
        #listitem.setProperty('inputstream.mpd.license_type', 'com.widevine.alpha')
        #listitem.setProperty('inputstream.mpd.license_type', 'com.widevine.alpha')
        listitem.setProperty(is_type+".license_type", "com.widevine.alpha")
        listitem.setProperty(is_type+".manifest_type", "mpd")
        listitem.setProperty('inputstreamaddon', is_type)
        try:
          lic=json_data["drm"]["licenseAcquisitionUrl"]        
          token=json_data["drm"]["token"]                
          listitem.setProperty(is_type+'.license_key', lic +"?token="+token+"|"+userAgent+"|R{SSM}|")            
        except:
           pass
        #listitem.setProperty('inputstreamaddon', 'inputstream.mpd')        
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
  
        #print "Daten lic :"+lic
        #print "Daten token :"+token
        #print "Daten data :"+data        
        return ""
