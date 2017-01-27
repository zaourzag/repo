# coding=utf-8
#
#  Copyright (C) 2015 Daniel Griner (griner.ch@gmail.com)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import xbmc, xbmcgui, xbmcaddon, os, datetime, time
import json
from zapisession import ZapiSession


__addon__ = xbmcaddon.Addon()
_listMode_ = __addon__.getSetting('channellist')
_channelList_=[]


REMOTE_DBG = False

# append pydev remote debugger
if REMOTE_DBG:
  # Make pydev debugger works for auto reload.
  # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
  try:
    import pysrc.pydevd as pydevd  # with the addon script.module.pydevd, only use `import pydevd`
  # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
    #pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True, suspend=False)
    pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)
  except ImportError:
    sys.stderr.write("Error: You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
    sys.exit(1)

class ZattooDB(object):
  def __init__(self):
    self.conn = None
    profilePath = xbmc.translatePath(__addon__.getAddonInfo('profile'))
    if not os.path.exists(profilePath): os.makedirs(profilePath)
    self.databasePath = os.path.join(profilePath, "zattoo.db")
    self.connectSQL()
    self.zapi=self.zapiSession()

  def zapiSession(self):
    zapiSession   = ZapiSession(xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8'))
    if zapiSession.init_session(__addon__.getSetting('username'), __addon__.getSetting('password')):
      return zapiSession
    else:
      # show home window, zattoobox settings and quit
      xbmc.executebuiltin('ActivateWindow(10000)')
      xbmcgui.Dialog().ok(__addon__.getAddonInfo('name'), __addon__.getLocalizedString(31902))
      __addon__.openSettings()
      zapiSession.renew_session()
      sys.exit()
    
  @staticmethod
  def adapt_datetime(ts):
    # http://docs.python.org/2/library/sqlite3.html#registering-an-adapter-callable
    return time.mktime(ts.timetuple())

  @staticmethod
  def convert_datetime(ts):
    try:
      return datetime.datetime.fromtimestamp(float(ts))
    except ValueError:
      return None

  def connectSQL(self):
    import sqlite3

    sqlite3.register_adapter(datetime.datetime, self.adapt_datetime)
    sqlite3.register_converter('timestamp', self.convert_datetime)

    self.conn = sqlite3.connect(self.databasePath, detect_types=sqlite3.PARSE_DECLTYPES)
    self.conn.execute('PRAGMA foreign_keys = ON')
    self.conn.row_factory = sqlite3.Row

    # check if DB exists
    c = self.conn.cursor()
    try: c.execute('SELECT * FROM showinfos')
    except: self._createTables()


  def _createTables(self):
    import sqlite3
    c = self.conn.cursor()

    try: c.execute('DROP TABLE channels')
    except: pass
    try: c.execute('DROP TABLE programs')
    except: pass
    try: c.execute('DROP TABLE updates')
    except: pass
    try: c.execute('DROP TABLE playing')
    except: pass
    try: c.execute('DROP TABLE showinfos')
    except: pass
    self.conn.commit()

    try:
      c.execute('CREATE TABLE channels(id TEXT, title TEXT, logo TEXT, weight INTEGER, favourite BOOLEAN, PRIMARY KEY (id) )')
      c.execute('CREATE TABLE programs(showID TEXT, title TEXT, channel TEXT, start_date TIMESTAMP, end_date TIMESTAMP, description TEXT, description_long TEXT, year TEXT, country TEXT, genre TEXT, category TEXT, image_small TEXT, image_large TEXT, updates_id INTEGER, FOREIGN KEY(channel) REFERENCES channels(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED, FOREIGN KEY(updates_id) REFERENCES updates(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)')
      c.execute('CREATE TABLE updates(id INTEGER, date TIMESTAMP, type TEXT, PRIMARY KEY (id) )')
      c.execute('CREATE TABLE playing(channel TEXT, start_date TIMESTAMP, action_time TIMESTAMP, current_stream INTEGER, streams TEXT, PRIMARY KEY (channel))')
      c.execute('CREATE TABLE showinfos(showID INTEGER, info TEXT, PRIMARY KEY (showID))')

      c.execute('CREATE INDEX program_list_idx ON programs(channel, start_date, end_date)')
      c.execute('CREATE INDEX start_date_idx ON programs(start_date)')
      c.execute('CREATE INDEX end_date_idx ON programs(end_date)')

      self.conn.commit()
      c.close()

    except sqlite3.OperationalError, ex:
      pass

  def updateChannels(self, rebuild=False):
    c = self.conn.cursor()

    if rebuild == False:
      date = datetime.date.today().strftime('%Y-%m-%d')
      c.execute('SELECT * FROM updates WHERE date=? AND type=? ', [date, 'channels'])
      if len(c.fetchall())>0:
        c.close()  
        return

    # always clear db on update
    c.execute('DELETE FROM channels')
    print "account  "+ self.zapi.AccountData['account']['power_guide_hash']
    api = '/zapi/v2/cached/channels/' + self.zapi.AccountData['account']['power_guide_hash'] + '?details=False'
    channelsData = self.zapi.exec_zapiCall(api, None)

    api = '/zapi/channels/favorites'
    favoritesData = self.zapi.exec_zapiCall(api, None)

    nr = 0
    for group in channelsData['channel_groups']:
      for channel in group['channels']:
        logo = 'http://logos.zattic.com' + channel['qualities'][0]['logo_black_84'].replace('/images/channels', '')
        try:
          favouritePos = favoritesData['favorites'].index(channel['id'])
          weight = favouritePos
          favourite = True
        except:
          weight = 1000 + nr
          favourite = False

        c.execute('INSERT OR IGNORE INTO channels(id, title, logo, weight, favourite) VALUES(?, ?, ?, ?, ?)',
            [channel['id'], channel['title'], logo, weight, favourite])
        if not c.rowcount:
          c.execute('UPDATE channels SET title=?, logo=?, weight=?, favourite=? WHERE id=?',
              [channel['title'], logo, weight, favourite, channel['id']])
        nr += 1
    if nr>0: c.execute('INSERT INTO updates(date, type) VALUES(?, ?)', [datetime.date.today(), 'channels'])
    self.conn.commit()
    c.close()

  def updateProgram(self, date=None, rebuild=False):
    if date is None: date = datetime.date.today()
    else: date = date.date()

    c = self.conn.cursor()

    if rebuild:
      c.execute('DELETE FROM programs')
      self.conn.commit()

    # get whole day
    fromTime = int(time.mktime(date.timetuple()))  # UTC time for zattoo
    toTime = fromTime + 86400  # is 24h maximum zattoo is sending?


    #get program from DB and return if it's not empty
#     if self._isDBupToDate(date, 'programs'):return
    c.execute('SELECT * FROM programs WHERE start_date > ? AND end_date < ?', [fromTime+18000, fromTime+25200]) #get shows between 05:00 and 07:00
    count=c.fetchall()
    if len(count)>0: 
        c.close()
        return

    xbmcgui.Dialog().notification(__addon__.getLocalizedString(31022), date.strftime('%A %d.%m.%Y'), __addon__.getAddonInfo('path') + '/icon.png', 5000, False)

    api = '/zapi/v2/cached/program/power_guide/' + self.zapi.AccountData['account']['power_guide_hash'] + '?end=' + str(toTime) + '&start=' + str(fromTime)

    print "api   "+api
    programData = self.zapi.exec_zapiCall(api, None)

    count=0
    for channel in programData['channels']:
       cid = channel['cid']
       if cid =="chtv":
          continue
       c.execute('SELECT * FROM channels WHERE id==?', [cid])
       countt=c.fetchall()
       if len(countt)==0: 
         print "Sender NICHT : "+cid
       for program in channel['programs']:
        count+=1
        if program['i'] != None:
          image = "http://images.zattic.com/" + program['i']
          #http://images.zattic.com/system/images/6dcc/8817/50d1/dfab/f21c/format_480x360.jpg
        else: image = ""          
        try:
            print 'INSERT OR IGNORE INTO programs(channel, title, start_date, end_date, description, genre, image_small, showID) VALUES(%, %, %, %, %, %, %)',cid, program['t'], program['s'], program['e'], program['et'], ', '.join(program['g']), image, program['id'] 
        except:
            pass
        c.execute('INSERT OR IGNORE INTO programs(channel, title, start_date, end_date, description, genre, image_small, showID) VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
            [cid, program['t'], program['s'], program['e'], program['et'], ', '.join(program['g']), image, program['id'] ])          
        if not c.rowcount:
            c.execute('UPDATE programs SET channel=?, title=?, start_date=?, end_date=?, description=?, genre=?, image_small=? WHERE showID=?',
              [cid, program['t'], program['s'], program['e'], program['et'], ', '.join(program['g']), image, program['id'] ])            
    if count>0: 
      c.execute('INSERT into updates(date, type) VALUES(?, ?)', [date, 'program'])        
      self.conn.commit()    
    c.close()
    
    
  def getChannelList(self, favourites=True):
    #self.updateChannels()
    c = self.conn.cursor()
    if favourites: c.execute('SELECT * FROM channels WHERE favourite=1 ORDER BY weight')
    else: c.execute('SELECT * FROM channels ORDER BY weight')
    channelList = {'index':[]}
    nr=0
    for row in c:
      channelList[row['id']]={
        'id': str(row['id']),
        'title': row['title'],
        'logo': row['logo'],
        'weight': row['weight'],
        'favourite': row['favourite'],
        'nr':nr
      }
      channelList['index'].append(str(row['id']))
      nr+=1
    c.close()
    return channelList

  def get_channelInfo(self, channel_id):
    c = self.conn.cursor()
    c.execute('SELECT * FROM channels WHERE id=?', [channel_id])
    row = c.fetchone()
    channel = {
         'id':row['id'],
         'title':row['title'],
         'logo':row['logo'],
         'weight':row['weight'],
         'favourite':row['favourite']
    }
    c.close()
    return channel


  def getPrograms(self, channels, get_long_description=False, startTime=datetime.datetime.now(), endTime=datetime.datetime.now()):
    import urllib
    c = self.conn.cursor()
    programList = []
 
    for chan in channels['index']:
      c.execute('SELECT * FROM programs WHERE channel = ? AND start_date < ? AND end_date > ?', [chan, endTime, startTime])
      r = c.fetchall()
      for row in r:
        description_long = row['description_long']
        if get_long_description and description_long is None: 
            #description_long = self.getShowInfo(row["showID"],'description')
            description_long = self.getShowLongDescription(row['showID'])
        programList.append({
            'channel': row['channel'],
            'showID' : row['showID'],
            'title' : row['title'],
            'description' : row['description'],
            'description_long' : description_long,
            'year': row['year'],
            'genre': row['genre'],
            'country': row['country'],
            'category': row['category'],
            'start_date' : row['start_date'],
            'end_date' : row['end_date'],
            'image_small' : row['image_small'],
            'image_large': row['image_large']
            })

    c.close()
    return programList

  def getShowLongDescription(self, showID):
        info = self.conn.cursor()
        try:
            info.execute('SELECT * FROM programs WHERE showID= ? ', [showID])
        except:
            info.close()
            return None
        
        show = info.fetchone()
        longDesc = show['description_long']
        if longDesc is None:
            api = '/zapi/program/details?program_id=' + showID + '&complete=True'
            showInfo = self.zapiSession().exec_zapiCall(api, None)
            if showInfo is None:
                longDesc=''
                info.close()
                return longDesc            
            longDesc = showInfo['program']['description']
            info.execute('UPDATE programs SET description_long=? WHERE showID=?', [longDesc, showID ])
            year = showInfo['program']['year']
            if year is None: year=''
            info.execute('UPDATE programs SET year=? WHERE showID=?', [year, showID ])
            category = ', '.join(showInfo['program']['categories'])
            info.execute('UPDATE programs SET category=? WHERE showID=?', [category, showID ])
            country = showInfo['program']['country']
            country = country.replace('|',', ')
            info.execute('UPDATE programs SET country=? WHERE showID=?', [country, showID ])
            
        self.conn.commit()
        info.close()
        return longDesc
        
  def getShowInfo(self, showID, field='all'):
        if field!='all':
            api = '/zapi/program/details?program_id=' + str(showID) + '&complete=True'
            showInfo = self.zapi.exec_zapiCall(api, None)
            return showInfo['program'].get(field, " ")
        
        #save information for recordings
        import json
        c = self.conn.cursor()
        c.execute('SELECT * FROM showinfos WHERE showID= ? ', [int(showID)])
        row = c.fetchone()
        if row is not None:
            showInfoJson=row['info']
            showInfo=json.loads(showInfoJson)
        else:
            api = '/zapi/program/details?program_id=' + str(showID) + '&complete=True'
            showInfo = self.zapi.exec_zapiCall(api, None)
            if showInfo is None: 
                c.close()
                return "NONE"
            showInfo = showInfo['program']
            try: c.execute('INSERT INTO showinfos(showID, info) VALUES(?, ?)',(int(showID), json.dumps(showInfo)))
            except: pass
        self.conn.commit()
        c.close()
        return showInfo
    


  def set_playing(self, channel=None, start=None, streams=None, streamNr=0):
    c = self.conn.cursor()
    c.execute('DELETE FROM playing')
    #c.execute('INSERT INTO playing(channel, start_date, action_time, current_stream,  streams) VALUES(?, ?, ?, ?, ?)', [channel, start, datetime.datetime.now(), streamNr, streams])
    c.execute('INSERT INTO playing(channel, start_date, action_time, current_stream,  streams) VALUES(?, ?, ?, ?, ?)', [channel, start, '1', streamNr, streams])

    self.conn.commit()
    c.close()

  def get_playing(self):
    c = self.conn.cursor()
    c.execute('SELECT * FROM playing')
    row = c.fetchone()
    if row is not None:
      playing = {'channel':row['channel'], 'start':row['start_date'], 'action_time':row['action_time'], 'current_stream':row['current_stream'], 'streams':row['streams']}
    else:
      c.execute('SELECT * FROM channels WHERE weight=?', ['0'] )
      row = c.fetchone() 
      playing = {'channel':row['id'], 'start':datetime.datetime.now(), 'action_time':datetime.datetime.now()}
    c.close()
    return playing

  def set_currentStream(self, nr):
    c = self.conn.cursor()
    c.execute('UPDATE playing SET current_stream=?', [nr])
    self.conn.commit()
    c.close()

  def reloadDB(self):
    '''
    c = self.conn.cursor()
    c.execute('DELETE FROM updates')
    self.conn.commit()
    c.close()
    '''
    self._createTables()

    self.updateChannels(True)
    self.updateProgram(datetime.datetime.now(), True)
  
  
  def get_channeltitle(self, channelid):
    c = self.conn.cursor()
    c.execute('SELECT * FROM channels WHERE id= ? ', [channelid])
    row = c.fetchone()
    if row:
      channeltitle=row['title']
    self.conn.commit()
    c.close()
    return channeltitle 

  def get_channelid(self, channeltitle):
    c = self.conn.cursor()
    c.execute('SELECT * FROM channels WHERE title= ? ', [channeltitle])
    row = c.fetchone()
    if row:
      channelid=row['id']
    self.conn.commit()
    c.close()
    return channelid
  
  def get_channelweight(self, weight):
    c = self.conn.cursor()
    c.execute('SELECT * FROM channels WHERE weight= ? ', [weight])
    row = c.fetchone()
    if row:
      channelid=row['id']
    self.conn.commit()
    c.close()
    return channelid

  def getProgInfo(self, notify=False, startTime=datetime.datetime.now(), endTime=datetime.datetime.now()):
        fav = False
        if __addon__.getSetting('onlyfav') == 'true': fav = True
        channels = self.getChannelList(fav)

        c = self.conn.cursor()

        # for startup-notify
        if notify:
            PopUp = xbmcgui.DialogProgressBG()
            counter=len(channels)
            bar = 0         # Progressbar (Null Prozent)
            PopUp.create('ZattooBoxExt lade Programm Informationen ...', '')
            PopUp.update(bar)
        
        for chan in channels['index']:
            print str(chan) + ' - ' + str(startTime) 
            #try:
            
            c.execute('SELECT * FROM programs WHERE channel = ? AND start_date < ? AND end_date > ?', [chan, endTime, startTime])
            r=c.fetchall()
            
            for row in r:
                print str(row['channel']) + ' - ' + str(row['showID'])
                if notify:
                    bar += 1
                    percent = int(bar * 100 / counter) 
                description_long = row["description_long"]
                
                if description_long is None: 
                    print 'Lang ' + str(row['channel'])
                    if notify:
                        PopUp.update(percent,'ZattooBoxExt lade Programm Informationen ...', 'Programm Information für ' + str(row['channel']))
                    description_long = self.getShowLongDescription(row["showID"])
        c.close()
        if notify:
            PopUp.close()
        return 
