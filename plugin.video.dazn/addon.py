# -*- coding: utf-8 -*-

from resources.lib.client import Client
from resources.lib import dazn
from resources.lib.common import *

client = Client()

def run():
    if mode == 'rails':
        dazn.rails_items(client.rails(id, params), id)
    elif mode == 'rail':
        dazn.rail_items(client.rail(id, params))
    elif mode == 'epg':
        date = params
        if id == 'input_date':
            date = input_date()
        dazn.epg_items(client.epg(date), date)
    elif mode == 'play':
        dazn.playback(client.playback(id))
    elif mode == 'play_context':
        dazn.playback(client.playback(id), title, True)

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', ['rails'])[0]
title = args.get('title', [''])[0]
id = args.get('id', ['home'])[0]
params = args.get('params', [''])[0]
if not args:
    args = version
log('[%s] arguments: %s' % (addon_id, str(args)))

if id == 'home':
    if uniq_id():
        client.startUp()
        if client.TOKEN:
            run()
else:
    run()