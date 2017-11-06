# -*- coding: utf-8 -*-

from resources.lib.client import Client
from resources.lib import dazn
from resources.lib.common import *

client = Client()

def run():
    if mode == 'rails':
        dazn.rails_items(client.rails(_id, params), _id)
    elif 'rail' in mode:
        dazn.rail_items(client.rail(_id, params), mode)
    elif 'epg' in mode:
        date = params
        if _id == 'date':
            date = get_date()
        dazn.epg_items(client.epg(date), date, mode)
    elif mode == 'play':
        dazn.playback(client.playback(_id))
    elif mode == 'play_context':
        dazn.playback(client.playback(_id), title, True)
    elif mode == 'is_settings':
        is_settings()
    elif mode == 'is_helper':
        is_helper()

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', ['rails'])[0]
title = args.get('title', [''])[0]
_id = args.get('id', ['home'])[0]
params = args.get('params', [''])[0]
if not args:
    args = version
log('[{0}] country: {1} language: {2} arguments: {3}'.format(addon_id, country, language, str(args)))

if args == version:
    if uniq_id():
        client.startUp()
        if client.TOKEN:
            run()
else:
    run()