# -*- coding: utf-8 -*-

from common import *
import base64,pyDes

class Credentials:

    def __init__(self):
        self.email = addon.getSetting('email')
        self.password = addon.getSetting('password')
        self.set_credentials()

    def encode(self, data):
        k = pyDes.triple_des(uniq_id(t=2), pyDes.CBC, "\0\0\0\0\0\0\0\0", padmode=pyDes.PAD_PKCS5)
        d = k.encrypt(data)
        return base64.b64encode(d)

    def decode(self, data):
        k = pyDes.triple_des(uniq_id(t=2), pyDes.CBC, "\0\0\0\0\0\0\0\0", padmode=pyDes.PAD_PKCS5)
        d = k.decrypt(base64.b64decode(data))
        return d

    def set_credentials(self):
        if self.email and self.password:
            self.email = self.decode(self.email)
            self.password = self.decode(self.password)
        else:
            self.email = dialog.input(getString(30002), type=xbmcgui.INPUT_ALPHANUM)
            self.password = dialog.input(getString(30003), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
            if store_creds:
                addon.setSetting('email', self.encode(self.email))
                addon.setSetting('password', self.encode(self.password))