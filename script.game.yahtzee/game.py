#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2018 Mark König (mark.koenig@kleiner-schelm.de)
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

import os
import random
from random import randint
import time
import thread
import string
import sys
from decimal import Decimal

import xbmc
import xbmcaddon
import xbmcgui

addon = xbmcaddon.Addon()

ADDON_NAME = addon.getAddonInfo('name')
ADDON_PATH = addon.getAddonInfo('path').decode('utf-8')
MEDIA_PATH = os.path.join(
    xbmc.translatePath(ADDON_PATH),
    'resources',
    'skins',
    'default',
    'media'
)
LIB_PATH = os.path.join(
    xbmc.translatePath(ADDON_PATH),
    'resources',
    'lib'
)

ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

class Game(xbmcgui.WindowXML):

    pointsP1 = []
    pointsP2 = []
    pointsP3 = []
    pointsP4 = []

    hold = []
    dice = []

    soundOn = True

    round = 0
    actualTry = 1
    actualPlayer = 0

    player = 2
    computer = 0
    gameOn = False

    diceOn = False
    diceCnt = 0
    diceFinished = 0

# ----------------------------------------------------------------------------------------------------

    def onInit(self):
        # init vars

        # init points
        for i in range(15):
            self.pointsP1.append(-1)
            self.pointsP2.append(-1)
            self.pointsP3.append(-1)
            self.pointsP4.append(-1)

        for i in range(5):
            self.hold.append(False)
            self.dice.append(6)

        # set points
        self.updatePoints()

        # get controls

        # init the grid

        # start the timer thread
        thread.start_new_thread(self.timer_thread, ())
        # start the game

        y = YahtzeeLogic()
        #y.ReadRestgewinn()
        
        self.updateToggleButtons(0)

    def onAction(self, action):
        action_id = action.getId()
        focus_id = self.getFocusId()
        
        if action_id == ACTION_PREVIOUS_MENU:
            self.closeApp()
        if action_id == ACTION_NAV_BACK:
            self.closeApp()            

    def closeApp(self):
        dialog = xbmcgui.Dialog()        
        confirmed = dialog.yesno(addon.getLocalizedString(3025),
                                 addon.getLocalizedString(3045),
                                 addon.getLocalizedString(3046)
                                )
        if confirmed:
            self.close()

    def onFocus(self, control_id):
        self.updateToggleButtons(control_id)

    def onClick(self, control_id):

        # set points
        if(control_id >= 5299) and (control_id < 5320):
            btn = control_id - 5300 + 1

            if(self.gameOn and not self.diceOn and (self.actualTry > 0)):
                points = self.GetValuePlayer(self.actualPlayer)
                if(points[btn-1] == -1):

                    calc = YahtzeePoint()
                    value = calc.GetCalc(btn, self.dice)

                    if(value == 0):
                        dialog = xbmcgui.Dialog()        
                        confirmed = dialog.yesno(addon.getLocalizedString(3042),
                                                 addon.getLocalizedString(3043),
                                                 addon.getLocalizedString(3044),
                                                 addon.getLocalizedString(3012 + btn)
                                                 )
                                         
                        if confirmed:
                            self.SetValuePlayer(self.actualPlayer, btn-1, 0)
                            self.updatePoints()
                            self.NextPlayer()
                    else:
                        self.SetValuePlayer(self.actualPlayer, btn-1, value)
                        self.updatePoints()
                        self.NextPlayer()

        # new game
        if(control_id == 5002):
            if(self.gameOn):
                 dialog = xbmcgui.Dialog()
                 confirmed = dialog.yesno(addon.getLocalizedString(3034),
                                          addon.getLocalizedString(3035),
                                          addon.getLocalizedString(3036)
                                          )
                 if confirmed:
                     self.NewGame()
            else:
                self.NewGame()

        # set player
        if(control_id == 5003):
            if(not self.gameOn):
                if(self.player<4):
                    self.player = self.player + 1
                else:
                    self.player = 1

                if(self.player + self.computer) > 4:
                   self.computer = 4 - self.player
                self.updateToggleButtons(0)

        # set computer
        if(control_id == 5004):
            if(not self.gameOn):
                if self.computer < (4 - self.player):
                    # not implemeneted yet
                    #self.computer = self.computer + 1
                    pass
                else:
                    self.computer = 0
                self.updateToggleButtons(0)

        # sound on/off
        if(control_id == 5005):
            self.soundOn = not self.soundOn
            self.updateToggleButtons(control_id)

        # dice
        if(control_id == 5008):
            if(not self.gameOn):
            
                self.NewGame()
                
                self.gameOn = True
                self.actualPlayer = 1
                actualTry = 1

                self.diceOn = True
                
                if(self.soundOn):
                    xbmc.playSFX(MEDIA_PATH + '\\dice.wav')
                    
                self.diceOn = True
                self.diceFinished = False

                self.updateToggleButtons(control_id);
            else:
                if(self.actualTry < 3):
                    self.actualTry = self.actualTry + 1
                    self.diceOn = True
                    self. diceFinished = False

                    if(self.soundOn):
                        xbmc.playSFX(MEDIA_PATH + '\\dice.wav')
                    self.diceOn = True
                    self.diceFinished = False

                    self.updateToggleButtons(control_id);

        # give me a tip
        if(control_id == 5009):
            dialog = xbmcgui.Dialog()
            confirmed = dialog.ok(addon.getLocalizedString(3025),
                                  '..... sooon'
                                  )

        # whats this
        if(control_id == 5010):
            dialog = xbmcgui.Dialog()
            confirmed = dialog.ok(addon.getLocalizedString(3025),
                                  addon.getLocalizedString(3050)
                                  )

        if(self.actualTry > 0) and self.gameOn and not self.diceOn and self.diceFinished:
            if(control_id == 5200):
                self.hold[0] = not self.hold[0]
                self.updateToggleButtons(control_id)
            if(control_id == 5201):
                self.hold[1] = not self.hold[1]
                self.updateToggleButtons(control_id)
            if(control_id == 5202):
                self.hold[2] = not self.hold[2]
                self.updateToggleButtons(control_id)
            if(control_id == 5203):
                self.hold[3] = not self.hold[3]
                self.updateToggleButtons(control_id)
            if(control_id == 5204):
                self.hold[4] = not self.hold[4]
                self.updateToggleButtons(control_id)

    def timer_thread(self):
        while not xbmc.abortRequested:
            if(self.diceOn):
                self.diceCnt = self.diceCnt +1
                if(self.diceCnt < 10):
                    for i in range(5):
                        if (self.hold[i] == False):
                            x =randint(1, 6)
                            self.p0x = self.getControl(5100+ i)
                            self.p0x.setImage('w%s.png' % x)
                            self.dice[i] = x
                else:
                    self.diceOn = False
                    self.diceFinished = True   
            else:
                self.diceCnt = 0
            xbmc.sleep(200)

    def GetValuePlayer(self, playerNo):
        if(playerNo == 1):
            return self.pointsP1
        if(playerNo == 2):
            return self.pointsP2
        if(playerNo == 3):
            return self.pointsP3
        if(playerNo == 4):
            return self.pointsP4

    def SetValuePlayer(self, playerNo, field, value):
    
        points = self.GetValuePlayer(playerNo)
        points[field] = value
        
        top = 0
        for i in range(6):
            if(points[i] > 0):
                top = top + points[i]
                if(top > 62):
                    top = top + 35      
        bottom = 0
        for i in range(7,14):
            if(points[i] > 0):
                bottom = bottom + points[i]
                
        points[6] = top
        points[14] = top + bottom      

    def NewGame(self):

          self.round = 1
          self.gameOn = False
          self.diceOn = False
          self.diceFinished = False
          
          for i in range(15):
              self.pointsP1[i] = -1
              self.pointsP2[i] = -1
              self.pointsP3[i] = -1
              self.pointsP4[i] = -1
              
          # reset hold
          for i in range(5):
              self.hold[i] = False

          self.updateToggleButtons(0)
          self.updatePoints()

    def NextPlayer(self):
          self.actualTry = 0
          self.actualPlayer = self.actualPlayer + 1

          #reset hold
          for i in range(5):
              self.hold[i] = False

          if (self.actualPlayer > self.player):
              self.actualPlayer = 1
              self.round = self.round + 1
              if (self.round  == 14):
                  self.gameOn = False # game over
                  if(self.soundOn):
                      xbmc.playSFX(MEDIA_PATH + '\\applaus.wav')   

          self.updateToggleButtons(0);

    def updateToggleButtons(self, control_id):

        # update player settings
        self.p0x = self.getControl(5003)
        self.p0x.setLabel(addon.getLocalizedString(3002) + str(self.player))
        
        self.p0x = self.getControl(5004)
        self.p0x.setLabel(addon.getLocalizedString(3003) + str(self.computer))

        # update actual player
        self.p0x = self.getControl(5006)
        if(self.gameOn):
            self.p0x.setLabel(addon.getLocalizedString(3006) + ' ' + str(self.actualPlayer))
        else:
            self.p0x.setLabel(addon.getLocalizedString(3005))

        # protect for startup
        self.p0x = self.getControl(5007)
        self.p0x.setLabel(addon.getLocalizedString(3007) + ' ' + str(self.actualTry) + ' ' +
                          addon.getLocalizedString(3008) + ' 3')

        if len(self.hold) < 4:
            return

        # set fcous / set for the hold button
        for i in range(5):
            self.p0x = self.getControl(5900 + i)

            if(self.hold[i] == False):
                self.p0x.setImage('t_button.png')
            else:
                self.p0x.setImage('t_button_sel.png')

            if(control_id == (5200 + i)):
                if(self.hold[i] == False):
                    self.p0x.setImage('t_button_active.png')
                else:
                    self.p0x.setImage('t_button_active_sel.png')

        # set fcous / set for the sound button
        self.p0x = self.getControl(6005)
        if(self.soundOn == False):
            self.p0x.setImage('t_button.png')
        else:
            self.p0x.setImage('t_button_sel.png')
        if(control_id == (5005)):
            if(self.soundOn == False):
                self.p0x.setImage('t_button_active.png')
            else:
                self.p0x.setImage('t_button_active_sel.png')

    def updatePoints(self):
        for i in range(15):
            self.p0x = self.getControl(5400+ i)
            if(self.pointsP1[i] >= 0):
                self.p0x.setLabel(str(self.pointsP1[i]))
            else:
                self.p0x.setLabel('..')
            self.p0x = self.getControl(5500+ i)
            if(self.pointsP2[i] >= 0):
                self.p0x.setLabel(str(self.pointsP2[i]))
            else:
                self.p0x.setLabel('..')
            self.p0x = self.getControl(5600+ i)
            if(self.pointsP3[i] >= 0):
                self.p0x.setLabel(str(self.pointsP3[i]))
            else:
                self.p0x.setLabel('..')
            self.p0x = self.getControl(5700+ i)
            if(self.pointsP4[i] >= 0):
                self.p0x.setLabel(str(self.pointsP4[i]))
            else:
                self.p0x.setLabel('..')

    def log(self, msg):
        xbmc.log('[ADDON][%s] %s' % ('TEST', msg.encode('utf-8')),
                 level=xbmc.LOGNOTICE)

# ----------------------------------------------------------------------------------------------------

    # http://www.holderied.de/kniffel/
    # Autor: Felix Holderied 

    # ported to C# by Mark König 2009, http://www.team-mediaportal.com
    # ported to Python by Mark König 2018, http://www.kodinerds.net (partly)

class YahtzeeLogic(object):

    restgewinn = []  # Einzulesende Erwartungswerte

    wuerfe = (
    0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 16, 22, 23, 24, 25,
    26, 33, 34, 35, 36, 44, 45, 46, 55, 56, 66, 111, 112, 113,
    114, 115, 116, 122, 123, 124, 125, 126, 133, 134, 135, 136,
    144, 145, 146, 155, 156, 166, 222, 223, 224, 225, 226, 233,
    234, 235, 236, 244, 245, 246, 255, 256, 266, 333, 334, 335,
    336, 344, 345, 346, 355, 356, 366, 444, 445, 446, 455, 456,
    466, 555, 556, 566, 666, 1111, 1112, 1113, 1114, 1115, 1116,
    1122, 1123, 1124, 1125, 1126, 1133, 1134, 1135, 1136, 1144,
    1145, 1146, 1155, 1156, 1166, 1222, 1223, 1224, 1225, 1226,
    1233, 1234, 1235, 1236, 1244, 1245, 1246, 1255, 1256, 1266,
    1333, 1334, 1335, 1336, 1344, 1345, 1346, 1355, 1356, 1366,
    1444, 1445, 1446, 1455, 1456, 1466, 1555, 1556, 1566, 1666,
    2222, 2223, 2224, 2225, 2226, 2233, 2234, 2235, 2236, 2244,
    2245, 2246, 2255, 2256, 2266, 2333, 2334, 2335, 2336, 2344,
    2345, 2346, 2355, 2356, 2366, 2444, 2445, 2446, 2455, 2456,
    2466, 2555, 2556, 2566, 2666, 3333, 3334, 3335, 3336, 3344,
    3345, 3346, 3355, 3356, 3366, 3444, 3445, 3446, 3455, 3456,
    3466, 3555, 3556, 3566, 3666, 4444, 4445, 4446, 4455, 4456,
    4466, 4555, 4556, 4566, 4666, 5555, 5556, 5566, 5666, 6666,
    11111, 11112, 11113, 11114, 11115, 11116, 11122, 11123,
    11124, 11125, 11126, 11133, 11134, 11135, 11136, 11144,
    11145, 11146, 11155, 11156, 11166, 11222, 11223, 11224,
    11225, 11226, 11233, 11234, 11235, 11236, 11244, 11245,
    11246, 11255, 11256, 11266, 11333, 11334, 11335, 11336,
    11344, 11345, 11346, 11355, 11356, 11366, 11444, 11445,
    11446, 11455, 11456, 11466, 11555, 11556, 11566, 11666,
    12222, 12223, 12224, 12225, 12226, 12233, 12234, 12235,
    12236, 12244, 12245, 12246, 12255, 12256, 12266, 12333,
    12334, 12335, 12336, 12344, 12345, 12346, 12355, 12356,
    12366, 12444, 12445, 12446, 12455, 12456, 12466, 12555,
    12556, 12566, 12666, 13333, 13334, 13335, 13336, 13344,
    13345, 13346, 13355, 13356, 13366, 13444, 13445, 13446,
    13455, 13456, 13466, 13555, 13556, 13566, 13666, 14444,
    14445, 14446, 14455, 14456, 14466, 14555, 14556, 14566,
    14666, 15555, 15556, 15566, 15666, 16666, 22222, 22223,
    22224, 22225, 22226, 22233, 22234, 22235, 22236, 22244,
    22245, 22246, 22255, 22256, 22266, 22333, 22334, 22335,
    22336, 22344, 22345, 22346, 22355, 22356, 22366, 22444,
    22445, 22446, 22455, 22456, 22466, 22555, 22556, 22566,
    22666, 23333, 23334, 23335, 23336, 23344, 23345, 23346,
    23355, 23356, 23366, 23444, 23445, 23446, 23455, 23456,
    23466, 23555, 23556, 23566, 23666, 24444, 24445, 24446,
    24455, 24456, 24466, 24555, 24556, 24566, 24666, 25555,
    25556, 25566, 25666, 26666, 33333, 33334, 33335, 33336,
    33344, 33345, 33346, 33355, 33356, 33366, 33444, 33445,
    33446, 33455, 33456, 33466, 33555, 33556, 33566, 33666,
    34444, 34445, 34446, 34455, 34456, 34466, 34555, 34556,
    34566, 34666, 35555, 35556, 35566, 35666, 36666, 44444,
    44445, 44446, 44455, 44456, 44466, 44555, 44556, 44566,
    44666, 45555, 45556, 45566, 45666, 46666, 55555, 55556,
    55566, 55666, 56666, 66666)

    def ReadRestgewinn(self):
     
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Yahtzee', 'Loading values, please wait!')
     
        fobj = open(ADDON_PATH + '\\Yahtzee.dat', "r")
        data = fobj.read()
        fobj.close()
         
        sp = data.split(';')

        for i in range(len(sp) - 1):
            self.restgewinn.append(Decimal(sp[i].replace(',','.')))
            p =  i * 100 / 524288
            pDialog.update(p)
        pDialog.close()

    def IndexSpielstand(self, spielstand):

        tempindex = 0
        for i in range(13):
            if (spielstand[i] >= 0):
                tempindex = tempindex + 2**i

        tempindex *= 64
        if (Summe(ss, 0, 5) >= 63):
            tempindex += 63
        else:
            tempindex += Summe(ss, 0, 5)

        return (tempindex);

    def Summe(self, spielstand, von, bis):

        s = 0
        for i in range(von, bis + 1):
            if(spielstand[i] >= 0):
                s += spielstand[i]

        return (s)

    def IndexWurf(self, wurf):

        temp = sorted(wurf)
        for i in range(252):
            if (wuerfe[i + 210] == temp):
                return i
        return -1

# ----------------------------------------------------------------------------------------------------

class YahtzeePoint(object):

    def GetCalc(self, button, dice):
        val = 0

        if(button == 1):
            val = self.AddUpDice(1, dice)
        elif(button == 2):
            val = self.AddUpDice(2, dice)
        elif(button == 3):
            val = self.AddUpDice(3, dice)
        elif(button == 4):
            val = self.AddUpDice(4, dice)
        elif(button == 5):
            val = self.AddUpDice(5, dice)
        elif(button == 6):
            val = self.AddUpDice(6, dice)
        elif(button == 8):
            val = self.CalculateThreeOfAKind(dice)
        elif(button == 9):
            val = self.CalculateFourOfAKind(dice)
        elif(button == 10):
            val = self.CalculateFullHouse(dice)
        elif(button == 11):
            val = self.CalculateSmallStraight(dice)
        elif(button == 12):
            val = self.CalculateLargeStraight(dice)
        elif(button == 13):
            val = self.CalculateYahtzee(dice)
        elif(button == 14):
            val = self.AddUpChance(dice)

        return val

    def AddUpDice(self, no, dice):
        val = 0

        for i in range(5):
            if(dice[i] == no):
                val = val + no;

        return val

    def CalculateThreeOfAKind(self, dice):
        val = 0
        ThreeOfAKind = False

        for x in range(6):
            cnt = 0
            for i in range(5):
                if (dice[i] == (x + 1)):
                    cnt = cnt + 1
                if (cnt > 2):
                    ThreeOfAKind = True
                    break

        if (ThreeOfAKind):
            for i in range(5):
                val = val + dice[i]

        return val

    def CalculateFourOfAKind(self, dice):
        val = 0
        FourOfAKind = False

        for x in range(6):
            cnt = 0
            for i in range(5):
                if (dice[i] == (x + 1)):
                    cnt = cnt + 1
                if (cnt > 3):
                    FourOfAKind = True
                    break

        if (FourOfAKind):
            for i in range(5):
                val = val + dice[i]

        return val

    def CalculateFullHouse(self, dice):
        val = 0
        i = sorted(dice)

        if ((((i[0] == i[1]) and (i[1] == i[2])) and # Three of a Kind
           (i[3] == i[4]) and # Two of a Kind
           (i[2] != i[3])) or
           ((i[0] == i[1]) and # Two of a Kind
           ((i[2] == i[3]) and (i[3] == i[4])) and # Three of a Kind
           (i[1] != i[2]))):
            val = 25;

        return val

    def CalculateSmallStraight(self, dice):
        val = 0
        i = sorted(dice)

        # Problem can arise hear, if there is more than one of the same number, so
        # we must move any doubles to the end

        for j in range(4):
            if (i[j] == i[j + 1]):
                temp = i[j]
                for k in range(j, 4):
                    i[k] = i[k + 1]
                i[4] = temp

        if(((i[0] == 1) and (i[1] == 2) and (i[2] == 3) and (i[3] == 4)) or
            ((i[0] == 2) and (i[1] == 3) and (i[2] == 4) and (i[3] == 5)) or
            ((i[0] == 3) and (i[1] == 4) and (i[2] == 5) and (i[3] == 6)) or
            ((i[1] == 1) and (i[2] == 2) and (i[3] == 3) and (i[4] == 4)) or
            ((i[1] == 2) and (i[2] == 3) and (i[3] == 4) and (i[4] == 5)) or
            ((i[1] == 3) and (i[2] == 4) and (i[3] == 5) and (i[4] == 6))):
            val = 30

        return val

    def CalculateLargeStraight(self, dice):
        val = 0
        i = sorted(dice)

        if (((i[0] == 1) and (i[1] == 2) and (i[2] == 3) and (i[3] == 4) and (i[4] == 5)) or
            ((i[0] == 2) and (i[1] == 3) and (i[2] == 4) and (i[3] == 5) and (i[4] == 6))):

            val = 40

        return val

    def CalculateYahtzee(self, dice):

        for x in range(6):
            cnt = 0
            for i in range(5):
                if (dice[i] == (x + 1)):
                    cnt = cnt + 1
                if (cnt > 4):
                    return 50
        return 0

    def AddUpChance(self,dice):
        val = 0

        for i in range(5):
            val = val + dice[i]

        return val

# ----------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    game = Game(
        'script-%s-main.xml' % ADDON_NAME,
        ADDON_PATH,
        'default',
        '720p'
    )
    game.doModal()
    del game

sys.modules.clear()
