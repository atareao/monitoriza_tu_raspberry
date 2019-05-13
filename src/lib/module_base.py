#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Monitorize your Raspberry Pi
#
# Copyright © 2019  Javier Pastor (aka VSC55)
# <jpastor at cerebelum dot net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pprint

class ModuleBase(object):
    _monitor = None
    _nameModule = ''

    def __init__(self, name='', monitor=None, debug = False):
        self._debugMode = debug
        self._monitor = monitor
        if name:
            self._nameModule = name
        else:
            self._nameModule = __name__

    @property
    def NameModule(self):
        return self._nameModule

    @property
    def debugMode(self):
        return self._debugMode

    @debugMode.setter
    def debugMode(self, value):
        self._debugMode = value

    def debug(self, message):
        if self.debugMode:
            if isinstance(message, str):
                print(message)
            else:
                pprint.pprint(message)

    @property
    def monitor(self):
        return self._monitor

    def check(self):
        pass

    def send_message(self, message):
        if message:
            if self.monitor:
                self.monitor.tg_send_message(message)


        
if __name__ == '__main__':
    moduel = ModuleBase()
    print(moduel.check())
