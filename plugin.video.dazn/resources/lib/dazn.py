# -*- coding: utf-8 -*-

from common import *
from items import Items

items = Items()

def rails_items(data, id):
    from rails import Rails
    if id == 'home':
        epg = {
            'mode': 'epg',
            'title': utfenc(getString(30212)),
            'plot': 'Schedule',
            'params': 'today'
        }
        items.add_item(epg)
    for i in data.get('Rails', []):
        items.add_item(Rails(i).item)
    items.list_items()
    
def rail_items(data, list=True):
    from tiles import Tiles
    from context import Context
    focus = data.get('StartPosition', False)
    for i in data.get('Tiles', []):
        context = Context()
        item = Tiles(i).item       
        if item.get('related', None):
            cm_items = []
            for i in item['related']:
                if i.get('Videos', []):
                    cm_items.append(Tiles(i).item)
            context.related(cm_items)
        item['cm'] = context.goto(item)
        items.add_item(item)
    if list:
        items.list_items(focus)
        
def epg_items(data, params):
    from context import Context
    from resources import resources
    update = False if params == 'today' else True
    date = epg_date(data['Date'])
    cm = Context().epg_date()
    
    def date_item(day):
        return {
            'mode': 'epg',
            'title': '%s (%s)' % (resources(day.strftime('%A')), day.strftime(date_format)),
            'plot': '%s (%s)' % (resources(date.strftime('%A')), date.strftime(date_format)),
            'params': day,
            'cm': cm
        }
    
    items.add_item(date_item(get_prev_day(date)))
    rail_items(data, list=False)
    items.add_item(date_item(get_next_day(date)))
    items.list_items(upd=update)
    
def playback(data, name=False, context=False):
    from playback import Playback
    items.play_item(Playback(data), name, context)