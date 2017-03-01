import urlparse
import xbmcgui
import xbmcaddon

import maxdome as maxdome
import navigation as nav

addon_handle = int(sys.argv[1])
plugin_base_url = sys.argv[0]
params = dict(urlparse.parse_qsl(sys.argv[2][1:]))
addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()

base_url = "plugin://" + xbmcaddon.Addon().getAddonInfo('id')
cookie_path = xbmc.translatePath(addon.getAddonInfo('profile')) + 'COOKIES'
username = addon.getSetting('email')
password = addon.getSetting('password')
region = addon.getSetting('region').lower()

mas = maxdome.MaxdomeSession(username, password, cookie_path, region)
nav = nav.Navigation(mas)

# Router for all plugin actions
if params:
    if 'switchview' in params:
        nav.switchPackageView()
    if 'action' in params:
        if params['action'] == 'list':
            if 'page' in params:
                nav.getPage(params['page'])
            elif 'url' in params:
                path = params['url']
                listAssets(mas.Assets.parseHtmlAssets(path))
            elif 'id' in params:
                navid = params['id']
                use_filter = False
                start = 1
                if 'use_filter' in params:
                    if params['use_filter'].lower() == 'true':
                        use_filter = True
                if 'start' in params:
                    start = params['start']
                nav.listAssets(params['id'], use_filter=use_filter, start=start)
        elif params['action'] == 'play':
            if 'id' in params:
                assetid = params['id']
                nav.playAsset(assetid)
        elif params['action'] == 'export':
            if 'id' in params:
                xbmc.executebuiltin('ActivateWindow(busydialog)')
                mas.Assets.exportAsset(params['id'])
                xbmc.executebuiltin('Dialog.Close(busydialog)')
                dlg = xbmcgui.Dialog()
                if dlg.yesno('Bibliothek', 'Bibliothek jetzt aktualisieren?'):
                    xbmc.executebuiltin('UpdateLibrary(video)')
        elif params['action'] == 'add':
            mas.Assets.addToNotepad(params['id'])
            xbmc.executebuiltin('Container.Refresh')
        elif params['action'] == 'del':
            mas.Assets.deleteFromNotepad(params['id'])
            xbmc.executebuiltin('Container.Refresh')
        elif params['action'] == 'buy':
            nav.playAsset(params['id'])
else:
    nav.mainMenu()


