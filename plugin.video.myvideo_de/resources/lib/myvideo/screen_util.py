import re
from resources.lib import kodimon
from resources.lib.kodimon import KodimonException, VideoItem, DirectoryItem, contextmenu

__author__ = 'L0RE'


def try_set_season_and_episode(video_item):
    """
    First try to get an episode and after that the season
    """
    re_match = re.search("Staffel (\d+)", video_item.get_name())
    if re_match is not None:
        video_item.set_info(kodimon.VideoItem.INFO_SEASON, re_match.group(1))
        pass
    re_match = re.search("(Episode|Folge) (\d+)", video_item.get_name())
    if re_match is not None:
        video_item.set_info(kodimon.VideoItem.INFO_EPISODE, re_match.group(2))
        pass
    pass


def get_screen_object_by_name(screen, screen_object_name):
    screen_objects = screen.get('screen_objects', [])
    for screen_object in screen_objects:
        if screen_object.get('title', '') == screen_object_name:
            return screen_object
        pass
    return {}


def get_screen_object_by_type(screen, screen_object_type):
    screen_objects = screen.get('screen_objects', [])
    for screen_object in screen_objects:
        if screen_object['type'] == screen_object_type:
            return screen_object
        pass
    return {}


def screen_objects_to_items(provider, screen_objects, prepend_format_title=True):
    result = []

    for screen_object in screen_objects:
        screen_object_type = screen_object['type']
        if screen_object_type == 'format_item':
            title = screen_object['title']
            format_id = screen_object['id']
            image = screen_object['image_url']
            format_item = DirectoryItem(title,
                                        provider.create_uri(['format', str(format_id)]),
                                        image=image)
            format_item.set_fanart(provider.get_fanart())

            context_menu = [kodimon.contextmenu.create_add_to_favs(provider.get_plugin(),
                                                                   provider.localize(provider.LOCAL_FAVORITES_ADD),
                                                                   format_item)]
            format_item.set_context_menu(context_menu)

            result.append(format_item)
            pass
        elif screen_object_type == 'video_item' or screen_object_type == 'citylight_item':
            title = ''
            format_title = screen_object.get('format_title', '')
            video_title = screen_object.get('video_title', '')
            if format_title and video_title and prepend_format_title:
                title = '%s - %s' % (format_title, video_title)
            elif video_title:
                title = video_title
            elif format_title:
                title = format_title
            else:
                title = screen_object['id']
                pass

            video_item = VideoItem(title,
                                   provider.create_uri(['play', screen_object['id']]),
                                   image=screen_object['image_url'])
            video_item.set_fanart(provider.get_fanart())

            # duration
            video_item.set_duration_in_seconds(int(screen_object['duration']))

            # aired
            publishing_date = kodimon.parse_iso_8601(screen_object['publishing_date'])
            video_item.set_aired(publishing_date['year'], publishing_date['month'], publishing_date['day'])

            # season & episode
            try_set_season_and_episode(video_item)

            context_menu = [kodimon.contextmenu.create_add_to_watch_later(provider.get_plugin(),
                                                                          provider.localize(provider.LOCAL_WATCH_LATER),
                                                                          video_item)]
            video_item.set_context_menu(context_menu)
            
            result.append(video_item)
            pass
        else:
            raise KodimonException("Unknown screen_object type '%s'" % screen_object_type)
        pass

    return result
