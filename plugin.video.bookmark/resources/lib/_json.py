# -*- coding: utf-8 -*-
import json
import io, os
import xbmc, xbmcvfs, xbmcaddon

addonID = "plugin.video.bookmark"
addon = xbmcaddon.Addon(id=addonID)
addon_data_dir = xbmc.translatePath(addon.getAddonInfo('profile'))
addon_db_dir = os.path.join(addon_data_dir, 'db') + '/'

log_msg = 'plugin.video.bookmark - _json_lib -'


def read_json(db_file):
    xbmc.log(log_msg + '!READ JSON!', 1)
    xbmc.log(log_msg + 'File: '+db_file, 1)
    if xbmcvfs.exists(db_file):
        xbmc.log(log_msg+'File Exists', 1)
        with open(db_file) as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    data = upgrade_db(data)
                    write_json(db_file, data)
                    xbmc.log("DIIICT!!!")
                f.close()
            except ValueError:
                data = []
    else:
        xbmc.log(log_msg + 'File Not Exists', 1)
        data = []
    return data


def write_json(db_file, data):
    xbmc.log(log_msg + '!WRITE JSON!', 1)
    xbmc.log(log_msg + 'File: ' + db_file, 1)
    create_dir(addon_data_dir)
    create_dir(addon_db_dir)
    with io.open(db_file, 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(data, ensure_ascii=False)))
        f.close()


def check_dir(directory):
    return xbmcvfs.exists(directory)


def create_dir(directory):
    if not xbmcvfs.exists(directory):
        xbmcvfs.mkdir(directory)


def upgrade_db(data):
    xbmc.log(log_msg + '!UPGRADE DB!', 1)
    new_data = []
    for i in data:
        name = data[i]['name']
        url = data[i]['link']
        plot = data[i]['plot']
        iconimage = data[i]['icon']
        duration = data[i]['dura']
        date_added = data[i]['date']
        fanart = ''
        if 'fana' in data[i]:
            fanart = data[i]['fana']
        entry = {'name': name,
                 'link': url,
                 'icon': iconimage,
                 'fana': fanart,
                 'plot': plot,
                 'dura': duration,
                 'date': date_added}
        new_data.append(entry)
    return new_data
