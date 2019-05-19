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

import lib.monitor
import lib.debug

__all__ = ['ModuleBase']

class ModuleBase(object):

    #Nº de hilos que se usaran en los módulos para procesamiento en paralelo como valor por defecto.
    _default_threads = 5

    def __init__(self, parent_monitor, name=None):
        self._monitor = parent_monitor
        if name:
            self.__nameModule = name
        else:
            self.__nameModule = __name__

    @property
    def NameModule(self):
        return self.__nameModule

    def check(self):
        pass

    @property
    def isMonitorExist(self):
        if self._monitor and isinstance(self._monitor, lib.monitor.Monitor):
            return True
        return False

    @property
    def _monitor(self):
        return self.__monitor

    @_monitor.setter
    def _monitor(self, val):
        if isinstance(val, lib.monitor.Monitor):
            self.__monitor = val
        else:
            raise ValueError('Type not valid, only Monitor valid type.')

    def send_message(self, message, status=None):
        if message:
            if self._monitor:
                self._monitor.send_message(message, status)

    def get_conf(self, findkey=None, default_val=None, select_module=None):
        if default_val == None:
            default_val = {}

        if self.isMonitorExist:
            if not select_module:
                select_module = self.NameModule

            if select_module:
                if findkey == None:
                    return self._monitor.config_modules.get_conf(select_module, default_val)
                else:
                    return self._monitor.config_modules.get_conf([select_module, findkey], default_val)

        #    if select_module:
        #        if select_module in self.monitor.config_modules.keys():
        #            if not findkey:
        #                return self.monitor.config_modules[select_module]
        #            if findkey in self.monitor.config_modules[select_module].keys():
        #                return self.monitor.config_modules[select_module][findkey]
        #            else:
        #                return default_val

        if findkey or default_val:
            return default_val
        return []

    def chcek_status(self, status, module, module_subkey):
        if self._monitor:
            return self._monitor.chcek_status(status, module, module_subkey)
        return None