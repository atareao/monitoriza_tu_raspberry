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
import lib.tools
import lib.dict_files_path
import lib.modules.dict_return_check
from lib.object_base import ObjectBase

__all__ = ['ModuleBase']


class ModuleBase(ObjectBase):

    # Nº de hilos que se usaran en los módulos para procesamiento en paralelo como valor por defecto.
    _default_threads = 5
    path_file = None
    dict_return = None

    def __init__(self, obj_monitor, name=None):
        self._monitor = obj_monitor
        if name:
            self.__nameModule = name
        else:
            self.__nameModule = __name__
        self.path_file = lib.dict_files_path.DictFilesPath()
        self.dict_return = lib.modules.dict_return_check.ReturnModuleCheck()

    @property
    def NameModule(self):
        return self.__nameModule

    def check(self):
        self.debug.debug_obj(self.NameModule, self.dict_return.list, "Data Return")

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
        if default_val is None:
            default_val = {}

        if self.isMonitorExist:
            if not select_module:
                select_module = self.NameModule

            if select_module:
                if findkey is None:
                    return self._monitor.config_modules.get_conf(select_module, default_val)
                else:
                    return self._monitor.config_modules.get_conf([select_module, findkey], default_val)

        if findkey or default_val:
            return default_val
        return []

    def check_status(self, status, module, module_subkey):
        if self._monitor:
            return self._monitor.check_status(status, module, module_subkey)
        return None

    @staticmethod
    def _run_cmd(cmd, return_sterr=False):
        stdout, stderr = lib.tools.execute(cmd)
        if return_sterr:
            return stdout, stderr
        return stdout

    @staticmethod
    def _run_cmd_call(cmd):
        return_code = lib.tools.execute_call(cmd)
        return return_code
