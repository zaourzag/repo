from functools import partial
import re
from resources.lib import kodimon
from resources.lib.kodimon import DirectoryItem, VideoItem, KodimonException
from resources.lib.kodimon.helper import FunctionCache
from resources.lib.myvideo import Client
from . import screen_util

__author__ = 'L0RE'


class Provider(kodimon.AbstractProvider):
    def __init__(self, plugin=None):
        kodimon.AbstractProvider.__init__(self, plugin)

        self._client = Client()
        pass

    @kodimon.RegisterPath('^\/format\/(?P<format_id>\d+)\/(?P<category>.*)\/$')
    def _on_format_category(self, path, params, re_match):
        self._set_content_type_and_sort_methods()

        result = []

        format_id = re_match.group('format_id')
        category = re_match.group('category')

        json_data = self.call_function_cached(partial(self._client.get_format, format_id),
                                              seconds=FunctionCache.ONE_HOUR)
        screen = json_data['screen']
        screen_object = screen_util.get_screen_object_by_name(screen, category)
        result.extend(screen_util.screen_objects_to_items(self, screen_object.get('screen_objects', []),
                                                          prepend_format_title=False))

        return result

    @kodimon.RegisterPath('^\/format\/(?P<format_id>\d+)\/$')
    def _on_format(self, path, params, re_match):
        self._set_content_type_and_sort_methods()

        result = []

        format_id = re_match.group('format_id')
        json_data = self.call_function_cached(partial(self._client.get_format, format_id),
                                              seconds=FunctionCache.ONE_HOUR)
        screen = json_data['screen']
        screen_objects = screen['screen_objects']
        for screen_object in screen_objects:
            screen_object_type = screen_object['type']
            title = screen_object.get('title', '')
            if screen_object_type == 'sushi_bar' and title != 'Ganze Folgen' and len(
                    screen_object.get('screen_objects', [])) > 0:
                category_item = DirectoryItem(title,
                                              self.create_uri(['format', format_id, title]))
                category_item.set_fanart(self.get_fanart())
                result.append(category_item)
                pass
            pass

        screen_object = screen_util.get_screen_object_by_name(screen, 'Ganze Folgen')
        result.extend(screen_util.screen_objects_to_items(self, screen_object.get('screen_objects', []),
                                                          prepend_format_title=False))

        return result

    @kodimon.RegisterPath('^\/screen\/(?P<screen_id>\d+)\/(?P<sub_screen_id>.*)\/$')
    def _on_sub_screen(self, path, params, re_match):
        result = []

        screen_id = re_match.group('screen_id')
        sub_screen_id = re_match.group('sub_screen_id')
        self._set_content_type_and_sort_methods(screen_id == '40')

        json_data = self.call_function_cached(partial(self._client.get_screen, screen_id),
                                              seconds=FunctionCache.ONE_HOUR)
        screen = json_data['screen']
        screen_type = screen['type']
        if screen_type == 'FormatGrid':
            screen_objects = screen.get('screen_objects', [])
            if len(screen_objects) > 0:
                screen_objects = screen_objects[0]
                pass
            screen_object = screen_util.get_screen_object_by_name(screen_objects, sub_screen_id)
            result.extend(screen_util.screen_objects_to_items(self, screen_object.get('screen_objects', [])))
            pass
        elif screen_type == 'BasicPage' or screen_type == 'home':
            screen_object = screen_util.get_screen_object_by_name(screen, sub_screen_id)
            result.extend(screen_util.screen_objects_to_items(self, screen_object.get('screen_objects', [])))
            pass
        else:
            raise KodimonException("Unknown screen type '%s'" % screen_type)

        return result

    @kodimon.RegisterPath('^\/screen\/(?P<screen_id>\d+)\/$')
    def _on_screen(self, path, params, re_match):
        result = []

        screen_id = re_match.group('screen_id')
        json_data = self.call_function_cached(partial(self._client.get_screen, screen_id),
                                              seconds=FunctionCache.ONE_HOUR)
        screen = json_data['screen']
        screen_type = screen['type']
        if screen_type == 'FormatGrid':
            screen_objects = screen.get('screen_objects', [])
            if len(screen_objects) > 0:
                screen_objects = screen_objects[0].get('screen_objects', [])
                pass

            for screen_object in screen_objects:
                title = screen_object['title']
                sub_screen_item = DirectoryItem(title,
                                                self.create_uri(['screen', screen_id, title]))
                sub_screen_item.set_fanart(self.get_fanart())
                result.append(sub_screen_item)
                pass
            pass
        elif screen_type == 'BasicPage' or screen_type == 'home':
            screen_objects = screen['screen_objects']
            for screen_object in screen_objects:
                screen_object_type = screen_object['type']
                if screen_object_type != 'home_header':
                    title = screen_object['title']
                    sub_screen_item = DirectoryItem(title,
                                                    self.create_uri(['screen', screen_id, title]))
                    sub_screen_item.set_fanart(self.get_fanart())
                    result.append(sub_screen_item)
                    pass
                pass
            pass
        else:
            raise KodimonException("Unknown screen type '%s'" % screen_type)

        return result

    @kodimon.RegisterPath('/play/(?P<video_id>\d+)/')
    def _on_play(self, path, params, re_match):
        video_id = re_match.group('video_id')
        json_data = self._client.get_video_url(video_id)
        video_url = json_data['VideoURL']
        video_item = VideoItem(video_id,
                               video_url)
        return video_item

    def on_search(self, search_text, path, params, re_match):
        self._set_content_type_and_sort_methods()

        result = []

        json_data = self.call_function_cached(partial(self._client.search, search_text), seconds=FunctionCache.ONE_HOUR)
        screen = json_data['screen']

        category = params.get('category', 'Alle')

        screen_objects = screen['screen_objects']

        # list all sub categories of the search
        if category == 'Alle':
            for screen_object in screen_objects:
                title = screen_object['title']
                if title != 'Alle' and len(screen_object.get('screen_objects', [])) > 0:
                    new_params = {}
                    new_params.update(params)
                    new_params['category'] = title
                    search_category_item = DirectoryItem(title,
                                                         self.create_uri([path], new_params))
                    search_category_item.set_fanart(self.get_fanart())
                    result.append(search_category_item)
                    pass
                pass
            pass

        screen_object = screen_util.get_screen_object_by_name(screen, category)
        result.extend(screen_util.screen_objects_to_items(self, screen_object.get('screen_objects', [])))

        return result

    def on_root(self, path, params, re_match):
        result = []

        # search
        search_item = DirectoryItem('[B]'+self.localize(self.LOCAL_SEARCH)+'[/B]',
                                    self.create_uri([self.PATH_SEARCH, 'list']))
        search_item.set_fanart(self.get_fanart())
        result.append(search_item)

        if len(self.get_favorite_list().list()) > 0:
            fav_item = kodimon.DirectoryItem('[B]' + self.localize(self.LOCAL_FAVORITES) + '[/B]',
                                             self.create_uri([self.PATH_FAVORITES, 'list']))
            fav_item.set_fanart(self.get_fanart())
            result.append(fav_item)
            pass

        # watch later
        if len(self.get_watch_later_list().list()) > 0:
            fav_item = kodimon.DirectoryItem('[B]' + self.localize(self.LOCAL_WATCH_LATER) + '[/B]',
                                             self.create_uri([self.PATH_WATCH_LATER, 'list']))
            fav_item.set_fanart(self.get_fanart())
            result.append(fav_item)
            pass

        json_data = self.call_function_cached(partial(self._client.get_home), seconds=FunctionCache.ONE_HOUR)
        menu_items = json_data['menubar']['channels'][0]['menu_items']
        for menu_item in menu_items:
            title = menu_item['displayName']

            link_match = re.match('\/(.+)\/v(\d+)\/(.+)\/screen\/(?P<screen_id>\d+)', menu_item['link'])
            if link_match:
                screen_id = link_match.group('screen_id')

                menu_item = DirectoryItem(title,
                                          self.create_uri(['screen', screen_id]))
                menu_item.set_fanart(self.get_fanart())
                result.append(menu_item)
                pass
            pass

        return result

    def _set_content_type_and_sort_methods(self, movies=False):
        if movies:
            self.set_content_type(kodimon.constants.CONTENT_TYPE_MOVIES)
        else:
            self.set_content_type(kodimon.constants.CONTENT_TYPE_EPISODES)
            pass

        self.add_sort_method(kodimon.constants.SORT_METHOD_NONE,
                             kodimon.constants.SORT_METHOD_VIDEO_YEAR,
                             kodimon.constants.SORT_METHOD_VIDEO_TITLE,
                             kodimon.constants.SORT_METHOD_VIDEO_RUNTIME)
        pass

    def get_fanart(self):
        return self.create_resource_path('media', 'fanart.jpg')

    pass
