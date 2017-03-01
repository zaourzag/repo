# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import sys, os
from urllib import unquote_plus, quote_plus
from resources.lib._json import read_json
from resources.lib.listing import add_entries, parameters_string_to_dict

xbmc.log('plugin.video.bookmark - init video addon')

addonID = "plugin.video.bookmark"
addon = xbmcaddon.Addon(id=addonID)
home = addon.getAddonInfo('path').decode('utf-8')
dir_userdata = xbmc.translatePath(addon.getAddonInfo('profile'))
dir_db = os.path.join(dir_userdata, 'db') + '/'
dir_resources = os.path.join(home, 'resources') + '/'
#reduce(os.path.join, [home, "resources"])
fanart = ''
#view_mode_id = int('503')
pluginhandle = int(sys.argv[1])
loglevel = 1
log_msg = 'plugin.video.bookmark - '
TRANSLATE = addon.getLocalizedString

skip_root = False
enab_fana = False
if addon.getSetting('skip_root') == 'true': skip_root = True
if addon.getSetting('enab_fana') == 'true': enab_fana = True


def root():
    add_entries([{"name": "Addons", "mode": "addons", "type": "dir"}])


def get_addons():
    xbmc.log(log_msg + '!GET ADDONS!', loglevel)
    addons = []
    addons_listing = []
    path = dir_db
    xbmc.log(log_msg + 'path: ' + path, loglevel)
    for subdir, dirs, files in os.walk(path):
        for db_file in files:
            filepath = subdir + os.sep + db_file
            if filepath.endswith(".json"):
                name = db_file[:db_file.rfind(".json")]
                addons.append(name)
    for name in addons:
        addon_id = name  # url = addon_id
        name = get_addon_name(addon_id)
        thumb = get_addon_icon(addon_id)
        fanart = get_addon_fanart(addon_id)
        cm = get_cm(["addons"], addon_id)
        addons_listing.append({
            "name": name, "url": addon_id, "mode": "episodes", "type": "dir",
            "infolabels": {"title": name},
            "images": {"thumb": thumb, "fanart": fanart},
            "cm": cm})
    add_entries(addons_listing)


def get_episodes(name):
    xbmc.log(log_msg + '!GET EPISODES!', loglevel)
    xbmc.log(log_msg + 'from addon: ' +name, loglevel)
    items = []
    addon_id = name
    db_file = dir_db + addon_id + '.json'
    db_all = read_json(db_file)
    name = get_addon_name(addon_id)
    if addon_id != 'unknown' and addon_id != 'Kodi-DB':
        name = TRANSLATE(30011)+' '+name
        thumb = get_addon_icon(addon_id)
        fanart = get_addon_fanart(addon_id)
        items.append({"name": name, "url": addon_id, "mode": "to_addon", "type": "dir",
                      "images": {"thumb": thumb, "fanart": fanart},
                      "infolabels": {"title": name}})
    for i in reversed(db_all):
        try:
            name = i['name']
            url = i['link']
            plot = i['plot']
            iconimage = i['icon']
            duration = i['dura']
            date_added = i['date']
            fanart = ''
            if enab_fana:
                if 'fana' in i:
                    fanart = i['fana']
            cm = get_cm(["episodes"])
            items.append({
                "name": name, "url": url, "mode": "play", "type": "video",
                "infolabels": {"title": name, "duration": duration, "writer": addon_id, "plot": plot, "aired": date_added},
                "images": {"thumb": iconimage, "fanart": fanart}, "cm": cm})
        except KeyError:
            pass
    add_entries(items)


def change_addon(addon_id):
    xbmc.log(log_msg + '!CHANGE ADDON!', loglevel)
    xbmc.log(log_msg + 'AddonID: ' + addon_id, loglevel)
    xbmc.executebuiltin("RunAddon(%s)" % addon_id)


def get_cm(menu_list, url=''):
    menu = []
    for cm in menu_list:
        if cm == "addons":
            # TODO FIX
            menu.append((TRANSLATE(30023), 'XBMC.RunPlugin(%s?mode=delete_addon&url=%s)' % (sys.argv[0], url)))
        if cm == "episodes":
            menu.append((TRANSLATE(30022), 'XBMC.RunPlugin(%s?mode=delete_entry)' % (sys.argv[0])))
    return menu


def play(url):
    try:
        video_url = url
        listitem = xbmcgui.ListItem(path=video_url)
        xbmcplugin.setResolvedUrl(pluginhandle, succeeded=True, listitem=listitem)
    except ValueError:
        pass


def check_for_old_dbs():
    dirs_to_check = [dir_resources, dir_userdata]
    for dir in dirs_to_check:
        dirs, files = xbmcvfs.listdir(dir)
        for file in files:
            if file.endswith('.json'):  # json file exists
                xbmc.log(log_msg + 'FOUND OLD DB!')
                move_dbs(dir)  # move dbs to userdata
                break   # exit after file found and move_dbs


def move_dbs(cur_dir):
    dir = cur_dir
    dirs, files = xbmcvfs.listdir(dir)
    for file in files:
        if file.endswith('.json') and xbmcvfs.exists(xbmc.translatePath(dir + file)):  # file endswith json and exists
            db_file = xbmc.translatePath(dir + file)
            xbmcvfs.copy(db_file, db_file + '.backup')
            new_db_file = xbmc.translatePath(dir_db + file)
            success = xbmcvfs.copy(db_file, new_db_file)
            if success == 1 and xbmcvfs.exists(new_db_file):
                #delete = xbmcvfs.delete(xbmc.translatePath(dir + file))
                pass


def get_addon_icon(addon_id):
    return xbmc.translatePath("special://home/addons/%s/icon.png" % addon_id)


def get_addon_fanart(addon_id):
    return xbmc.translatePath("special://home/addons/%s/fanart.jpg" % addon_id)

'''
def check_for_old_dbs():
    dirs, files = xbmcvfs.listdir(resourcesDir)
    for file in files:
        if file.endswith('.json'):  # json file exists
            xbmc.log(log_msg + 'FOUND OLD DB!')
            move_dbs()  # move dbs to userdata
            break   # exit after file found and move_dbs
'''




# old move dbs function
'''
def move_dbs():
    dirs, files = xbmcvfs.listdir(resourcesDir)
    for file in files:
        if file.endswith('.json') and xbmcvfs.exists(xbmc.translatePath(resourcesDir + file)):  # file endswith json and exists
            db_file = xbmc.translatePath(resourcesDir + file)
            xbmcvfs.copy(db_file, db_file + '.backup')
            new_db_file = xbmc.translatePath(userdataDir + file)
            success = xbmcvfs.copy(db_file, new_db_file)
            if success == 1 and xbmcvfs.exists(new_db_file):
                delete = xbmcvfs.delete(xbmc.translatePath(resourcesDir + file))
'''


# very old move_dbs function
'''
def move_dbs():
    import fnmatch
    dirs, files = xbmcvfs.listdir(resourcesDir)
    for file in files:
        if fnmatch.fnmatch(file, '*.json'):
            success = xbmcvfs.copy(xbmc.translatePath(resourcesDir + file), xbmc.translatePath(userdataDir + file))
            if success == 1:
                delete = xbmcvfs.delete(xbmc.translatePath(resourcesDir + file))
'''


def get_addon_name(addon_id):
    retval = 'unknown'
    try:
        retval = xbmcaddon.Addon(addon_id).getAddonInfo('name')
    except RuntimeError:
        pass
    if addon_id == 'Kodi-DB':
        retval = "Kodi-DB"
    return retval


def delete_entry():
    xbmc.log(log_msg + '!DELETE!', loglevel)
    xbmc.executebuiltin("XBMC.RunScript(%scontext_rem.py)" % dir_resources)
    xbmc.sleep(100)
    xbmc.executebuiltin("Container.Refresh")


def delete_addon(addon_id):
    xbmc.log("addon_id")
    xbmc.log(addon_id)
    name = get_addon_name(addon_id)
    line1 = TRANSLATE(30110) + ' (%s)' % name
    retval_rule = xbmcgui.Dialog().yesno("Bookmark Addon", line1)
    if retval_rule == 1:
        db_file = dir_db + addon_id + '.json'
        xbmcvfs.delete(db_file)
    xbmc.sleep(100)
    xbmc.executebuiltin("Container.Refresh")


params = parameters_string_to_dict(sys.argv[2])
mode = params.get('mode')
url = params.get('url')
if type(url) == type(str()):
    url = unquote_plus(url)


if mode == 'addons':
    get_addons()
elif mode == 'episodes':
    get_episodes(url)
elif mode == 'play':
    play(url)
elif mode == 'to_addon':
    change_addon(url)
elif mode == 'delete_entry':
    delete_entry()
elif mode == 'delete_addon':
    delete_addon(url)
else:
    if not skip_root:
        root()
    else:
        get_addons()


xbmcplugin.endOfDirectory(pluginhandle)

check_for_old_dbs()
