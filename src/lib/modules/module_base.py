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
import lib.tools

from lib import Switch
from lib import ObjectBase
from lib import DictFilesPath
from lib.config import ConfigTypeReturn
from lib.modules import ReturnModuleCheck
from enum import Enum

__all__ = ['ModuleBase']


class ModuleBase(ObjectBase):

    # Nº de hilos que se usaran en los módulos para procesamiento en paralelo como valor por defecto.
    _default_threads = 5
    path_file = None
    dict_return = None

    def __init__(self, obj_monitor, name=None):
        self._monitor = obj_monitor
        if name:
            self.__name_module = name
        else:
            self.__name_module = __name__

        self.path_file = DictFilesPath()
        self.dict_return = ReturnModuleCheck()

    def check(self):
        self.debug.debug_obj(self.name_module, self.dict_return.list, "Data Return")

    @property
    def name_module(self):
        return self.__name_module

    @property
    def is_monitor_exist(self):
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
            if self.is_monitor_exist:
                self._monitor.send_message(message, status)

    def get_conf(self, findkey=None, default_val=None, select_module: str = None, str_split: str = None,
                 r_type: ConfigTypeReturn = ConfigTypeReturn.STR):
        if default_val is None:
            default_val = {}

        if self.is_monitor_exist:
            if not select_module:
                select_module = self.name_module

            if select_module:
                if findkey is None:
                    return self._monitor.config_modules.get_conf(select_module, default_val)
                else:
                    keys_list = self._monitor.config_modules.convert_find_key_to_list(findkey, str_split)
                    keys_list.insert(0, select_module)
                    return self._monitor.config_modules.get_conf(keys_list, default_val, str_split=str_split,
                                                                 r_type=r_type)

        if findkey or default_val:
            return default_val
        return []

    def get_conf_in_list(self, opt_find: str, key: str, def_val=None):
        with Switch(opt_find, check_isinstance=True) as case:
            if case(Enum):
                find_key = [opt_find.name]
            elif case(str):
                find_key = [opt_find]
            elif case(list):
                find_key = opt_find.copy()
            elif case(int, float):
                find_key = [str(opt_find)]
            elif case(tuple):
                find_key = list(opt_find)
            else:
                raise TypeError("opt_find is not valid type ({0})!".format(type(opt_find)))

        if key:
            find_key.insert(0, key)
            find_key.insert(0, "list")
        value = self.get_conf(find_key, def_val)
        return value

    def check_status(self, status, module, module_subkey):
        if self.is_monitor_exist:
            return self._monitor.check_status(status, module, module_subkey)
        return None

    @staticmethod
    def _run_cmd(cmd, return_sterr: bool = False):
        stdout, stderr = lib.tools.execute(cmd)
        if return_sterr:
            return stdout, stderr
        return stdout

    @staticmethod
    def _run_cmd_call(cmd):
        return_code = lib.tools.execute_call(cmd)
        return return_code
