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

__all__ = ['Monitor']


class Monitor(object):

    # Nº de hilos que se usaran para procesamiento en paralelo como valor por defecto.
    __default_threads = 5
    debug = None

    def __init__(self, dir_base, dir_config, dir_modules, dir_var, obj_debug=None):
        self.debug = obj_debug
        if not self.debug:
            self.debug = lib.debug.Debug(True)
        self.dir_base = dir_base
        self.dir_config = dir_config
        self.dir_modules = dir_modules
        self.dir_var = dir_var

        self.readConfig()
        self.readStatus()
        self.initTelegram()
        self.debug.print("Monitor Init OK", lib.debug.DebugLevel.debug)

    def __checkDir(self, pathdir):
        if pathdir:
            if not os.path.isdir(pathdir):
                os.makedirs(pathdir, exist_ok=True)

    def readConfig(self):
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

    def readStatus(self):
        if self.dir_var:
            self.__checkDir(self.dir_var)
            self.status = ConfigControl(os.path.join(self.dir_var, 'status.json'), {})
            if not self.status.is_exist:
                self.status.save()
        else:
            self.status = ConfigControl(None, {})

    def clearStatus(self):
        # TODO: Pendiente crear funcion clear en el objeto config
        self.debug.print("Clear Status", lib.debug.DebugLevel.info)
        self.readStatus()
        self.status.data = {}
        self.status.save()

    def initTelegram(self):
        if self.config:
            self.tg = lib.telegram.Telegram(
                self.config.get_conf(['telegram', 'token'], ''),
                self.config.get_conf(['telegram', 'chat_id'], ''),
                self.debug
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

    def get_conf(self, findkey=None, default_val=None):
        if self.config_monitor:
            return self.config_monitor.get_conf(findkey, default_val)
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

    def check_status(self, status, module, module_subkey=''):
        if module_subkey:
            if module not in self.__status_datos.keys() or module_subkey not in self.__status_datos[module].keys() or (module_subkey in self.__status_datos[module].keys() and self.__status_datos[module][module_subkey] != status):
                return True
        else:
            if module not in self.__status_datos.keys() or (module in self.__status_datos.keys() and self.__status_datos[module] != status):
                return True
        return False

    def check_module(self, module_name):
        try:
            self.debug.print("Module: {0}".format(module_name), lib.debug.DebugLevel.info)
            module_import = importlib.import_module(module_name)
            module = module_import.Watchful(self)
            r_mod_check = module.check()

            if isinstance(r_mod_check, lib.modules.dict_return_check.ReturnModuleCheck):
                if module_name not in self.__status_datos.keys():
                    self.__status_datos[module_name] = {}

                for (key, value) in r_mod_check.items():
                    self.debug.print("Module: {0} - Key: {1} - Val: {2}".format(module_name, key, value),
                                     lib.debug.DebugLevel.debug)
                    tmp_status = r_mod_check.get_status(key)
                    tmp_message = r_mod_check.get_message(key)
                    tmp_send = r_mod_check.get_send(key)

                    if self.check_status(tmp_status, module_name, key):
                        self.__status_datos[module_name][key] = tmp_status
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
            self.debug.Exception(e)
        return False

    def check(self):
        # cont_break = 0  # Debug - Count
        self.debug.print("Check Init: " + time.strftime("%c"), lib.debug.DebugLevel.debug)
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

        # TODO: Mantener self.__status_datos hasta crear función de modificar la configuración en Config.
        self.__status_datos = {}
        if self.status:
            self.__status_datos = self.status.read(True)

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
                    self.debug.Exception(exc)

        self.debug.debug_obj(__name__, self.__status_datos, "Debug Status Save")
        if changed is True:
            self.status.data = self.__status_datos
            self.status.save()
        self.debug.print("Check End: " + time.strftime("%c"), lib.debug.DebugLevel.debug)
