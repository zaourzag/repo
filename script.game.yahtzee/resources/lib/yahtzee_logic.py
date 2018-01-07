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

# http://www.holderied.de/kniffel/
# Autor: Felix Holderied 

# ported to C# by Mark König 2009, http://www.team-mediaportal.com
# ported to Python by Mark König 2018, http://www.kodinerds.net (partly)

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
