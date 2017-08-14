# -*- coding: utf-8 -*-

from resources.lib.client import Client
from resources.lib import wtatv
from resources.lib.common import *

client = Client()

def run():
    if mode == 'home':
        wtatv.home_items()
    elif mode == 'events':
        wtatv.event_items(client.events())
    elif mode == 'features':
        wtatv.video_items(client.features())
    elif mode == 'ondemand':
        wtatv.video_items(client.ondemand())
    elif mode == 'play_live':
        wtatv.play_live(client.streaming(id))
    elif mode == 'play_vod':
        wtatv.play_vod(client.vod(id))

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', ['home'])[0]
title = args.get('title', [''])[0]
id = args.get('id', ['home'])[0]
params = args.get('params', [''])[0]
if not args:
    args = version
log('[%s] arguments: %s' % (addon_id, str(args)))

if args == version:
    if uniq_id():
        if not cookie:
            client.login()
        run()
else:
    run()