# -*- coding: utf-8 -*-
import urllib2
import urlparse
import json

def get_playlist_url(cid, SESSION):
    from resources.lib.api import get_json_data
    json_data = get_json_data('http://zattoo.com/zapi/watch', SESSION, {'stream_type':'hls', 'cid':cid})
    return json.loads(json_data)['stream']['url']
    
def get_stream_url(cid, SESSION, MAX_BITRATE):
    playlist_url = get_playlist_url(cid, SESSION)
    m3u8_data = urllib2.urlopen(playlist_url).read()
    url_parts = [line for line in m3u8_data.split('\n') if '.m3u8' in line]
    prefix_url = urlparse.urljoin(playlist_url, '/')
    if MAX_BITRATE == '3000000':
        suffix_url = url_parts[0]
    elif MAX_BITRATE == '1500000':
        if len(url_parts) == 4:
            suffix_url = url_parts[1]
        else:
            suffix_url = url_parts[0]
    elif MAX_BITRATE == '900000':
        if len(url_parts) == 4:
            suffix_url = url_parts[2]
        else:
            suffix_url = url_parts[1]
    else:
        suffix_url = url_parts[-1]
    return prefix_url + suffix_url