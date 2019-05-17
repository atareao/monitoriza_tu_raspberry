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

from lib.debug import *
from monitor import *

__all__ = ['ModuleBase']

class ModuleBase(object):
    def __init__(self, name=None):
        global debug
        global monitor
        if name:
            self.__nameModule = name
        else:
            self.__nameModule = __name__

    @property
    def NameModule(self):
        return self.__nameModule

    def check(self):
        pass

    def send_message(self, message):
        if message:
            if monitor:
                monitor.send_message(message)

    def read_conf(self, findkey=None, default_val=None, select_module=None):
        if monitor:
            if not select_module:
                select_module = self.NameModule

            if select_module:
                if select_module in monitor.config_modules.keys():
                    if not findkey:
                        return monitor.config_modules[select_module]
                    if findkey in monitor.config_modules[select_module].keys():
                        return monitor.config_modules[select_module][findkey]
                    else:
                        return default_val

        if findkey or default_val:
            return default_val
        return []
        
if __name__ == '__main__':
    debug = Debug(True)
    moduel = ModuleBase()
    print(moduel.check())
