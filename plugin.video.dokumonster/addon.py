#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2012 Tristan Fischer (sphere@dersphere.de)
#     Copyright (C) 2017 mdmdmdmdmd
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from datetime import datetime
import time
from string import ascii_lowercase, digits
import json
import requests
import urllib
from xbmcswift2 import Plugin, xbmc, xbmcgui
from resources.lib.api import DokuMonsterApi, NetworkError

PER_PAGE = 50

plugin = Plugin()
api = DokuMonsterApi(default_count=PER_PAGE)

STRINGS = {
    'topics': 30001,
    'new_docus': 30002,
    'tags': 30003,
    'all': 30004,
    'top_docus': 30005,
    'search': 30006,
    'network_error': 30200
}


class DialogSelect(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.listing = kwargs.get("listing")
        self.title = kwargs.get("title")
        self.totalitems = 0
        self.result = None

    def autofocus_listitem(self):
        pass

    def close_dialog(self, cancelled=False):
        if cancelled:
            self.result = False
        else:
            self.result = self.list_control.getSelectedItem()
        self.close()

    def onInit(self):
        self.list_control = self.getControl(6)
        self.getControl(3).setVisible(False)
        self.list_control.setEnabled(True)
        self.list_control.setVisible(True)
        self.set_cancel_button()
        self.getControl(5).setVisible(False)
        self.getControl(1).setLabel(self.title)
        self.list_control.addItems(self.listing)
        self.setFocus(self.list_control)
        self.totalitems = len(self.listing)
        self.autofocus_listitem()

    def onAction(self, action):
        if action.getId() in (9, 10, 92, 216, 247, 257, 275, 61467, 61448, ):
            self.close_dialog(True)
        if (action.getId() == 7 or action.getId() == 100) and xbmc.getCondVisibility(
                "Control.HasFocus(3) | Control.HasFocus(6)"):
            self.close_dialog()

    def onClick(self, controlID):
        if controlID == 5:
            self.result = True
            self.close()
        else:
            self.close_dialog(True)

    def set_cancel_button(self):
        try:
            self.getControl(7).setLabel(xbmc.getLocalizedString(222))
            self.getControl(7).setVisible(True)
            self.getControl(7).setEnabled(True)
        except Exception:
            pass


@plugin.route('/')
def show_root():
    items = (
        # FIXME: Reihe
        {'label': _('topics'), 'path': plugin.url_for(
            endpoint='show_topics'
        )},
        {'label': _('new_docus'), 'path': plugin.url_for(
            endpoint='show_new_docus'
        )},
        {'label': _('tags'), 'path': plugin.url_for(
            endpoint='show_tags'
        )},
        {'label': _('all'), 'path': plugin.url_for(
            endpoint='show_initials'
        )},
        {'label': _('top_docus'), 'path': plugin.url_for(
            endpoint='show_top_docus'
        )},
        {'label': _('search'), 'path': plugin.url_for(
            endpoint='search'
        )},
    )
    return plugin.finish(items)


@plugin.route('/tags/')
def show_tags():
    return __finish_paginate('show_tags', api.get_tags, tags=True)


@plugin.route('/tags/<tag>/')
def show_docus_by_tag(tag):
    return __finish_paginate('show_docus_by_tag', api.get_docus_by_tag, tag=tag)


@plugin.route('/initals/')
def show_initials():
    items = []
    for char in list(ascii_lowercase + digits):
        items.append({
            'label': char.upper(),
            'path': plugin.url_for(
                endpoint='show_docus_by_initial',
                initial=char
            )
        })
    return plugin.finish(items)


@plugin.route('/initals/<initial>/')
def show_docus_by_initial(initial):
    return __finish_paginate(
        'show_docus_by_initial', api.get_docus_by_initial, initial=initial
    )


@plugin.route('/topics/')
def show_topics():
    return __finish_paginate('show_topics', api.get_topics, tags=True)


@plugin.route('/top_docus/')
def show_top_docus():
    return __finish_paginate('show_top_docus', api.get_top_docus)


@plugin.route('/new_docus/')
def show_new_docus():
    return __finish_paginate('show_new_docus', api.get_newest_docus)


@plugin.route('/search/')
def search():
    query = __keyboard(_('search'))
    if query:
        url = plugin.url_for('search_result', query=query)
        plugin.redirect(url)


@plugin.route('/search/<query>/')
def search_result(query):
    return __finish_paginate(
        'search_result', api.get_docus_by_query, query=query
    )


@plugin.route('/play/<docu_link>')
def play(docu_link):
    media = api.get_docu(docu_link)
    plugin.log.info(repr(media))
    source, media_type = media.get('source'), media.get('type')
    playback_url = None
    if source == 'youtube.com':
        if requests.head("http://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={0}&format=json".format(
                media.get('id'))).status_code == 200:
            if media_type == 'video':
                playback_url = (
                    'plugin://plugin.video.youtube/'
                    '?action=play_video&videoid=%s' % media.get('id')
                )
            elif media_type == 'playlist':
                playback_url = (
                    'plugin://plugin.video.youtube/'
                    '?action=play_all&playlist=%s' % media.get('id')
                )
        else:
            results = []
            title = media.get('title')
            for media in _youtube_search(urllib.quote_plus(title.encode(encoding='utf-8'))):
                label = media["label"]
                label2 = media["plot"]
                image = ""
                if media.get('art'):
                    if media['art'].get('thumb'):
                        image = (media['art']['thumb'])
                listitem = xbmcgui.ListItem(label=label, label2=label2, iconImage=image)
                listitem.setProperty("path", media["file"])
                results.append(listitem)
            title = "{0} \"{1}\"".format(_("Select mirror for"), title.encode(encoding='utf-8'))
            dialog = DialogSelect("DialogSelect.xml", "", listing=results, title=title)
            time.sleep(0.1)
            xbmc.executebuiltin("dialog.Close(busydialog)")
            dialog.doModal()
            result = dialog.result
            if not result:
                return
            playback_url = result.getProperty("path")
    elif source == 'vimeo.com':
        if media_type == 'video':
            playback_url = (
                'plugin://plugin.video.vimeo/'
                '?action=play_video&videoid=%s' % media.get('id')
            )
    if playback_url:
        plugin.log.info('Using playback url: %s' % playback_url)
        return plugin.set_resolved_url(playback_url)
    else:
        plugin.log.error(repr(media))
        plugin.notify(msg=_('Not Implemented yet'))


def _youtube_search(query):
    FIELDS_BASE = ["dateadded", "file", "lastplayed", "plot", "title", "art", "playcount"]
    FIELDS_FILE = FIELDS_BASE + ["streamdetails", "director", "resume", "runtime"]
    FIELDS_FILES = FIELDS_FILE + [
        "plotoutline", "sorttitle", "cast", "votes", "trailer", "year", "country", "studio",
        "genre", "mpaa", "rating", "tagline", "writer", "originaltitle", "imdbnumber", "premiered", "episode",
        "showtitle",
        "firstaired", "watchedepisodes", "duration", "season"]
    data = {
        "jsonrpc": "2.0",
        "method": "Files.GetDirectory",
        "id": 1,
        "params": {
            "properties": FIELDS_FILES,
            "directory": "plugin://plugin.video.youtube/kodion/search/query/?q={0}".format(query)
        }
    }
    json_response = xbmc.executeJSONRPC(json.dumps(data))
    json_object = json.loads(json_response.decode('utf-8'))
    result = []
    if 'result' in json_object:
        for key, value in json_object['result'].iteritems():
            if not key == "limits" and (isinstance(value, list) or isinstance(value, dict)):
                result = value
    result = [i for i in result if not i["filetype"] == "directory"]
    return result


def __finish_paginate(endpoint, api_func, tags=False, *args, **kwargs):
    is_update = 'page' in plugin.request.args
    page = plugin.request.args.get('page', ['1'])[0]
    docus, total_count = api_func(*args, page=page, **kwargs)
    if tags:
        items = __format_tags(docus)
    else:
        items = __format_docus(docus)
    if int(page) > 1:
        p = str(int(page) - 1)
        items.insert(0, {
            'label': '<< Page %s <<' % p,
            'info': {'count': 0},
            'path': plugin.url_for(
                endpoint,
                page=p,
                **kwargs
            )
        })
    if int(page) * PER_PAGE < int(total_count):
        p = str(int(page) + 1)
        items.append({
            'label': '>> Page %s >>' % p,
            'info': {'count': len(docus) + 2},
            'path': plugin.url_for(
                endpoint,
                page=p,
                **kwargs
            )
        })
    finish_kwargs = {
        'sort_methods': ('PLAYLIST_ORDER', 'DATE'),
        'update_listing': is_update
    }
    if plugin.get_setting('force_viewmode') == 'true':
        finish_kwargs['view_mode'] = 'thumbnail'
    return plugin.finish(items, **finish_kwargs)


def __format_docus(docus, skip_playlists=True):
    items = []
    for i, docu in enumerate(docus):
        try:
            d = datetime.strptime(docu['online'], '%Y-%m-%dT%H:%M:%S')
        except TypeError:
            d = datetime(*(time.strptime(docu['online'], '%Y-%m-%dT%H:%M:%S')[0:6]))
        pub_date = '%02d.%02d.%04d' % (d.day, d.month, d.year)
        title = u'%s' % docu['title']
        item = {
            'label': title,
            'label2': docu['description'].replace('\n\r', '[CR]') or '',
            'info': {
                'count': i + 1,
                'tagline': docu['description'].replace('\n\r', '[CR]') or '',
                'date': pub_date
            },
            'path': plugin.url_for(
                endpoint='play',
                docu_link=docu['link']
            ),
            'is_playable': True
        }
        items.append(item)
    return items


def __format_tags(tags):
    items = []
    for i, tag in enumerate(tags):
        item = {
            'label': '%s [%s]' % (tag.get('name'), tag.get('count')),
            'info': {'count': i + 1},
            'path': plugin.url_for(endpoint='show_docus_by_tag', tag=tag['id'])
        }
        items.append(item)
    return items


def __keyboard(title, text=''):
    keyboard = xbmc.Keyboard(text, title)
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        return keyboard.getText()


def _(string_id):
    if string_id in STRINGS:
        return plugin.get_string(STRINGS[string_id])
    else:
        plugin.log.warning('String is missing: %s' % string_id)
        return string_id


if __name__ == '__main__':
    try:
        plugin.run()
    except NetworkError:
        plugin.notify(msg=_('network_error'))
