#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Monitorize your Raspberry Pi
#
# Copyright © 2019  Lorenzo Carbonell (aka atareao)
# <lorenzo.carbonell.cerezo at gmail dot com>
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

import glob
import os
import importlib
import socket
import time
import pprint
import concurrent.futures
import lib.debug
import lib.modules.module_base
import lib.telegram
import lib.modules.dict_return_check
from lib.config.configControl import *
from lib.object_base import ObjectBase

__all__ = ['Monitor']


class Monitor(ObjectBase):

    # Nº de hilos que se usaran para procesamiento en paralelo como valor por defecto.
    __default_threads = 5

    def __init__(self, dir_base, dir_config, dir_modules, dir_var):
        self.dir_base = dir_base
        self.dir_config = dir_config
        self.dir_modules = dir_modules
        self.dir_var = dir_var

        self.__read_config()
        self.__read_status()
        self.__init_telegram()
        self.debug.print("Monitor Init OK", lib.debug.DebugLevel.debug)

    @staticmethod
    def __check_dir(path_dir):
        if path_dir:
            if not os.path.isdir(path_dir):
                os.makedirs(path_dir, exist_ok=True)

    def __read_config(self):
        if self.dir_config:
            self.config = ConfigControl(os.path.join(self.dir_config, 'config.json'))
            self.config.read()
            self.config_monitor = ConfigControl(os.path.join(self.dir_config, 'monitor.json'))
            self.config_monitor.read()
            self.config_modules = ConfigControl(os.path.join(self.dir_config, 'modules.json'))
            self.config_modules.read()
        else:
            self.config = ConfigControl(None, {})
            self.config_monitor = ConfigControl(None, {})
            self.config_modules = ConfigControl(None, {})

    def __read_status(self):
        if self.dir_var:
            self.__check_dir(self.dir_var)
            self.status = ConfigControl(os.path.join(self.dir_var, 'status.json'), {})
            if not self.status.is_exist:
                self.status.save()
        else:
            self.status = ConfigControl(None, {})

    def clear_status(self):
        # TODO: Pendiente crear funcion clear en el objeto config
        self.debug.print("Clear Status", lib.debug.DebugLevel.info)
        self.__read_status()
        self.status.data = {}
        self.status.save()

    def __init_telegram(self):
        if self.config:
            self.tg = lib.telegram.Telegram(
                self.config.get_conf(['telegram', 'token'], ''),
                self.config.get_conf(['telegram', 'chat_id'], '')
            )
        else:
            self.tg = None

    @property
    def dir_base(self):
        return self.__dir_base

    @dir_base.setter
    def dir_base(self, val):
        self.__dir_base = val

    @property
    def dir_config(self):
        return self.__dir_config

    @dir_config.setter
    def dir_config(self, val):
        self.__dir_config = val

    @property
    def dir_modules(self):
        return self.__dir_modules

    @dir_modules.setter
    def dir_modules(self, val):
        self.__dir_modules = val

    @property
    def dir_var(self):
        return self.__dir_var

    @dir_var.setter
    def dir_var(self, val):
        self.__dir_var = val

    def get_conf(self, find_key=None, default_val=None):
        if self.config_monitor:
            return self.config_monitor.get_conf(find_key, default_val)
        return default_val

    def send_message(self, message, status=None):
        if message and self.tg:
            hostname = socket.gethostname()
            # Hay que enviar "\[" ya que solo "[" se lo come Telegram en modo "Markdown".
            message = "{0} \[{1}]: {2}".format(u'\U0001F4BB', hostname, message)
            if status is True:
                message = "{0} {1}".format(u'\U00002705', message)
            elif status is False:
                message = "{0} {1}".format(u'\U0000274E', message)
            self.tg.send_message(message)

    def check_status(self, status, module, module_sub_key=''):
        l_find = [module]
        if module_sub_key:
            l_find.append(module_sub_key)

        if self.status.get_conf(l_find, not status) != status:
            return True
        return False

    def check_module(self, module_name):
        try:
            self.debug.print("Module: {0}".format(module_name), lib.debug.DebugLevel.info)
            module_import = importlib.import_module(module_name)
            module = module_import.Watchful(self)
            r_mod_check = module.check()

            if isinstance(r_mod_check, lib.modules.dict_return_check.ReturnModuleCheck):
                for (key, value) in r_mod_check.items():
                    self.debug.print("Module: {0} - Key: {1} - Val: {2}".format(module_name, key, value),
                                     lib.debug.DebugLevel.debug)
                    tmp_status = r_mod_check.get_status(key)
                    tmp_message = r_mod_check.get_message(key)
                    tmp_send = r_mod_check.get_send(key)

                    if self.check_status(tmp_status, module_name, key):
                        self.status.set_conf([module_name, key], tmp_status)
                        if tmp_send:
                            self.send_message(tmp_message, tmp_status)
                        self.debug.print('Module: {0}/{1} - New Status: {2}'.format(module_name, key, tmp_status),
                                         lib.debug.DebugLevel.debug)
                return True

            else:
                msg_debug = '\n\n'+'*'*60 + '\n'
                msg_debug += "WARNING: check_module({0}) - Format not implement: {1}\n".format(module_name,
                                                                                               type(r_mod_check))
                msg_debug += 'Data Return: {0}\n'.format(pprint.pprint(r_mod_check))
                msg_debug += '*'*60 + '\n'
                msg_debug += '*'*60 + '\n\n'
                self.debug.print(msg_debug, lib.debug.DebugLevel.warning)

        except Exception as e:
            self.debug.exception(e)
        return False

    def check(self):
        # cont_break = 0  # Debug - Count
        self.debug.print("Check Init: " + time.strftime("%c"), lib.debug.DebugLevel.info)
        list_modules = []
        for module_def in glob.glob(os.path.join(self.dir_modules, '*.py')):
            module_def = os.path.splitext(os.path.basename(module_def))[0]
            if module_def.find('__') == -1:
                # Debug Control Run Modules
                # if cont_break < 1:
                #     list_modules.append(module_def)
                # cont_break = cont_break + 1
                # continue
                # Debug - End
                list_modules.append(module_def)

        changed = False

        self.status.read()

        max_threads = self.get_conf('threads', self.__default_threads)
        self.debug.print("Monitor Max Threads: {0}".format(max_threads), lib.debug.DebugLevel.debug)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_run_module = {executor.submit(self.check_module, module): module for module in list_modules}
            for future in concurrent.futures.as_completed(future_to_run_module):
                module = future_to_run_module[future]
                try:
                    if future.result():
                        changed = True
                except Exception as exc:
                    self.debug.exception(exc)

        self.debug.debug_obj(__name__, self.status.data, "Debug Status Save")
        if changed is True:
            self.status.save()
        self.debug.print("Check End: " + time.strftime("%c"), lib.debug.DebugLevel.info)
