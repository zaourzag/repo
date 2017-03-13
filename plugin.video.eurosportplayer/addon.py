# -*- coding: utf-8 -*-

from resources.lib.client import Client
from resources.lib import esp
from resources.lib import cache
from resources.lib.common import *

client = Client()

def run():
    if mode == 'root':
        esp.channel(client.channels())
    elif mode == 'sports':
        data = client.catchups()
        cache.cache_data(data)
        esp.sport(data)
    elif mode == 'videos':
        esp.video(cache.get_cache_data(),id)
    elif mode == 'play':
        esp.play(id, client.token())

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', ['root'])[0]
id = args.get('id', [''])[0]
params = args.get('params', [''])[0]
if not args:
    args = version
log('[%s] arguments: %s' % (addon_id, str(args)))

if mode == 'root':
    if uniq_id():
        if email and password:
            run()
        else:
            addon.openSettings()
else:
    run()