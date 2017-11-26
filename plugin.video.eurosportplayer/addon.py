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
    elif mode == 'all_sports':
        esp.all_sports(client.category_all())
    elif mode == 'events':
        esp.events(client.events())
    elif mode == 'event':
        esp.event(client.event(_id))
    elif mode == 'videos':
        esp.video(client.videos(_id), _id)
    elif 'epg' in mode:
        prev_date = params
        date = _id
        if date == 'date':
            prev_date, date = get_date()
        esp.epg(client.epg(prev_date, date), prev_date, date)
    elif mode == 'play':
        if _id:
            esp.play(client.streams(_id))
    elif mode == 'license_renewal':
        esp.license_renewal(client.license_key())

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', ['root'])[0]
_id = args.get('id', [''])[0]
params = args.get('params', [''])[0]
if not args:
    args = version
log('[{0}] country: {1} language: {2} arguments: {3}'.format(addon_id, country, language, str(args)))

if mode == 'root':
    if uniq_id():
        if client.ACCESS_TOKEN:
            run()
else:
    run()