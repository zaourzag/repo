import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin

HOST_AND_PATH = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])


def make_info_view_possible():
    xbmcplugin.setContent(ADDON_HANDLE, 'movies')


def add_folder(title, thumb, url_params, context_menu_items=None):
    item = xbmcgui.ListItem(title, thumbnailImage=thumb)
    if context_menu_items is not None:
        item.addContextMenuItems(context_menu_items)
    make_info_view_possible()
    return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url='%s?%s' % (HOST_AND_PATH, urllib.urlencode(url_params)),
                                       listitem=item, isFolder=True)


def add_video(title,
              thumb=None,
              url_params=None,
              video_info_labels=None,
              duration_in_seconds=None,
              fanart=None,
              video_url=None,
              icon=None,
              is_playable='true',
              context_menu_items=None,
              subtitle_list=None):
    """
    Callback function to pass directory contents back to XBMC as a list.

    :param title: primary title of video
    :param thumb: path to thumbnail
    :param url_params: dictionary of url parameters
    :param video_info_labels: {
            genre: string (Comedy)
            year: integer (2009)
            episode: integer (4) ...
        }
    :param fanart: path to fanart image
    :param video_url: direct url to video
    :param icon: path to icon
    :param is_playable: boolean
    :param context_menu_items: [('title', 'xbmc.function')]
    :param subtitle_list: ['url to srt']
    :return: boolean for successful completion
    """
    item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    item.setInfo(type='video', infoLabels=video_info_labels)
    item.setProperty('IsPlayable', is_playable)
    item.setProperty('fanart_image', fanart)
    if duration_in_seconds is not None:
        item.addStreamInfo('video', {'duration': duration_in_seconds})
    if context_menu_items is not None:
        item.addContextMenuItems(context_menu_items)
    if subtitle_list is not None:
        try:
            item.setSubtitles(subtitle_list)
        except AttributeError:
            pass  # requires xbmc version >= 14 (Helix)
    url = video_url or '%s?%s' % (HOST_AND_PATH, urllib.urlencode(url_params))
    return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=item)


def end_listing():
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def play(url):
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, xbmcgui.ListItem(path=url))


def play_playlist(playlist):
    # playlist = [(title,image_url,stream_url),(title,image_url,stream_url),...]
    p = xbmc.PlayList(1)
    p.clear()
    # workaround for http://forum.kodi.tv/showthread.php?tid=219833
    if playlist:
        title, image, video_url = playlist[0]
        p.add(video_url, xbmcgui.ListItem(title, thumbnailImage=image))
        for title, image, video_url in playlist:
            p.add(video_url, xbmcgui.ListItem(title, thumbnailImage=image))
    xbmc.Player().play(p)


def get_search_input(heading, default_text=''):
    keyboard = xbmc.Keyboard(default_text, heading)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()


def info_view():
    xbmc.executebuiltin('Container.SetViewMode(504)')


def warning(header, text):
    xbmc.executebuiltin('Notification(%s,%s)' % (header, text))
