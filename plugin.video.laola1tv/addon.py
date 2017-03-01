# -*- coding: utf-8 -*-

from resources.lib.client import Client
from resources.lib import items
from resources.lib import helper
from resources.lib import cache
from resources.lib.common import *

client = Client()

def run():
    if mode == 'root':
        data = client.menu()
        cache.cache_data(data)
        items.menu(data)
        login()
    elif mode == 'sports':
        items.sports(cache.get_cache_data(), title)
    elif mode == 'sub_menu':
        items.sub_menu(client.feeds(params, id))
    elif mode == 'live':
        items.live(client.live_feed())
    elif mode == 'videos':
        items.video(client.feeds(params, id))
    elif mode == 'play':
        items.play(path())
        client.deletesession()
        
def path():
    url = helper.unas_url(client.player(id, params))
    if url:
        return helper.master(client.unas_xml(url))

def login():
    client.logout()
    login_data = client.login()
    _cookie_   = helper.create_cookie(login_data)
    addon.setSetting('cookie', _cookie_)
    log('[%s] login: %s' % (addon_id, user(_cookie_)))
    
def user(_cookie_):
    return helper.user(client.user(_cookie_))

args   = urlparse.parse_qs(sys.argv[2][1:])
mode   = args.get('mode', ['root'])[0]
title  = args.get('title', [''])[0]
id     = args.get('id', [''])[0]
params = args.get('params', [''])[0]
if not args:
    args = version
log('[%s] arguments: %s' % (addon_id, str(args)))

if mode == 'root':
    if email and password:
        run()
    else:
        addon.openSettings()
else:
    run()