# -*- coding: utf-8 -*-

from resources.lib.client import Client
from resources.lib import esp
from resources.lib.common import *

client = Client()

def run():
    if mode == 'root':
        esp.channel(client.channels())
    elif mode == 'sports':
        esp.sport(client.categories())
    elif mode == 'videos':
        esp.video(client.videos(id), id)
    elif 'epg' in mode:
        prev_date = params
        date = id
        if date == 'date':
            prev_date, date = get_date()
        esp.epg(client.epg(prev_date, date), prev_date, date)
    elif mode == 'play':
        if id:
            esp.play(client.streams(id))

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', ['root'])[0]
id = args.get('id', [''])[0]
params = args.get('params', [''])[0]
if not args:
    args = version
log('[{0}] arguments: {1}'.format(addon_id, str(args)))

if mode == 'root':
    if uniq_id():
        if not client.ACCESS_TOKEN:
            client.login()
        if client.ACCESS_TOKEN:
            client.profile()
            run()
else:
    run()