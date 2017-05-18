# -*- coding: utf-8 -*-

from resources.lib.client import Client
from resources.lib import laola
from resources.lib import helper
from resources.lib import cache
from resources.lib.common import *

client = Client()

def run():
    if mode == 'root':
        data = client.menu()
        cache.cache_data(data)
        laola.menu(data)
        login()
    elif mode == 'sports':
        laola.sports(cache.get_cache_data(), title)
    elif mode == 'sub_menu':
        laola.sub_menu(client.feeds(params, id))
    elif mode == 'live':
        laola.live(client.live_feed())
    elif mode == 'videos':
        laola.video(client.feeds(params, id))
    elif mode == 'play':
        laola.play(path())
        client.deletesession()
        
def path():
    url = helper.unas_url(client.player(id, params))
    if url:
        return helper.master(client.unas_xml(url))

def login():
    _cookie_ = helper.create_cookie(client.session())
    if not _cookie_:
        _cookie_ = helper.create_cookie(client.login())
        log('[%s] login: %s' % (addon_id, user(_cookie_)))
    addon.setSetting('cookie', _cookie_)
    
def user(_cookie_):
    return helper.user(client.user(_cookie_))

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', ['root'])[0]
title = args.get('title', [''])[0]
id = args.get('id', [''])[0]
params = args.get('params', [''])[0]
if not args:
    args = version
log('[%s] arguments: %s' % (addon_id, str(args)))

run()