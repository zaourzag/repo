import os
from BeautifulSoup import BeautifulSoup
import xbmc
import xbmcvfs
import xbmcaddon

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
data_path = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')

class Library:
    def __init__(self):
        self.movie_path = os.path.join(data_path, 'Filme')
        self.tvshow_path = os.path.join(data_path, 'Serien')
        if addon.getSetting('enablelibraryfolder') == 'true':
            movie_path = os.path.join(xbmc.translatePath(addon.getSetting('customlibraryfolder')), 'Filme').decode('utf-8')
            tvshow_path = os.path.join(xbmc.translatePath(addon.getSetting('customlibraryfolder')), 'Serien').decode('utf-8')

    def setupMaxdomeLibrary(self):
        source_path = xbmc.translatePath('special://profile/sources.xml').decode('utf-8')
        source_added = False
        source = {'Maxdome Filme': self.movie_path, 'Maxdome TV Shows': self.tvshow_path}

        if xbmcvfs.exists(source_path):
            srcfile = xbmcvfs.File(source_path)
            soup = BeautifulSoup(srcfile)
            srcfile.close()

        video = soup.find("video")

        for name, path in source.items():
            path_tag = Tag(soup, "path")
            path_tag['pathversion'] = 1
            path_tag.append(path)
            source_text = soup.find(text=name)
            if not source_text:
                source_tag = Tag(soup, "source")
                name_tag = Tag(soup, "name")
                name_tag.append(name)
                source_tag.append(name_tag)
                source_tag.append(path_tag)
                video.append(source_tag)
                source_added = True
            else:
                source_tag = source_text.findParent('source')
                old_path = source_tag.find('path').contents[0]
                if path not in old_path:
                    source_tag.find('path').replaceWith(path_tag)
                    source_added = True

#        if source_added:
#            SaveFile(source_path, str(soup))
#            Dialog.ok(getString(30187), getString(30188), getString(30189), getString(30190))
#            if Dialog.yesno(getString(30191), getString(30192)):
#                xbmc.executebuiltin('RestartApp')

    def writeStrmFile(self, path, asset_id):
        with open(path, 'w+') as f:
            f.write('plugin://' + addon_id + '/?action=play&id=' + str(asset_id))
            f.close()
    
    def addMovie(self, asset_info):
        title = asset_info['title']
        year  = asset_info['productionYear']
        dirname = os.path.join(self.movie_path, '%s (%d)' % (title, year))
        filename = os.path.join(dirname, '%s (%d).strm' % (title, year))
        if os.path.exists(filename):
            return
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self.writeStrmFile(filename, asset_info['id'])

    def addEpisode(self, asset_info):
        title = asset_info['title']
        season_nr = int(asset_info['seasonNumber'])
        episode_nr = int(asset_info['episodeNumber'])
        episode_title = asset_info['episodeTitle']

        dirname = os.path.join(self.tvshow_path, '%s' % (title))
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        season_dir = os.path.join(dirname, 'Staffel %02d' % (season_nr))
        if not os.path.exists(season_dir):
            os.makedirs(season_dir)
        filename = '%s S%02dE%02d.strm' % (title, season_nr, episode_nr)
        filepath = os.path.join(season_dir, filename)
        if os.path.exists(filepath):
            return
        self.writeStrmFile(filepath, asset_info['id'])

