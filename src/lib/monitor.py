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

import globales
import glob
import os
import sys
import importlib
import socket
import pprint
import concurrent.futures
from lib.telegram import *
from lib.config import *
from lib.debug import *
from lib.module_base import *

__all__ = ['Monitor']

class Monitor(object):

    def __init__(self, dir_base, dir_config, dir_modules, dir_var):
        self.dir_base = dir_base
        self.dir_config = dir_config
        self.dir_modules = dir_modules
        self.dir_var = dir_var

        self.readConfig()
        self.readStatus()
        #self.status = None  #Descomentar para pruebas, omite el contenido status.json, dará error (self.status.save(self.__status_datos))
        self.initTelegram()


    def __checkDir(salf, pathdir):
        if pathdir:
            if not os.path.isdir(pathdir):
                os.makedirs(pathdir, exist_ok=True)

    def readConfig(self):
        if self.dir_config:
            self.config = Config(os.path.join(self.dir_config, 'config.json')).read()
            self.config_monitor = Config(os.path.join(self.dir_config, 'monitor.json')).read()
            self.config_modules = Config(os.path.join(self.dir_config, 'modules.json')).read()
        else:
            self.config = {}
            self.config_monitor = {}
            self.config_modules = {}

    def readStatus(self):
        if self.dir_var:
            self.__checkDir(self.dir_var)
            self.status = Config(os.path.join(self.dir_var, 'status.json'))
            if not self.status.isExist:
                self.status.data = {}
                self.status.save()
        else:
            self.status = None

    def initTelegram(self):
        if self.config:
            self.tg = Telegram(self.config['telegram']['token'], self.config['telegram']['chat_id'])
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


    def read_conf(self, findkey=None, default_val=None):
        if self.config_monitor:
            if findkey:
                if findkey in self.config_monitor.keys():
                    return self.config_monitor[findkey]
        return default_val

    def send_message(self, message):
        if message and self.tg:
            hostname = socket.gethostname()
            #Hay que enviar "\[" ya que solo "[" se lo come Telegram en modo "Markdown".
            self.tg.send_message("{0} \[{1}]: {2}".format(u'\U0001F4BB',hostname, message))


    def chcek_status(self, status, module, module_subkey=''):
        if module_subkey:
            if module not in self.__status_datos.keys() or module_subkey not in self.__status_datos[module].keys() or (module_subkey in self.__status_datos[module].keys() and  self.__status_datos[module][module_subkey] != status):
                return True
        else:
            if module not in self.__status_datos.keys() or (module in self.__status_datos.keys() and  self.__status_datos[module] != status):
                return True
        return False


    def check_module(self, module_name):
        try:
            globales.GlobDebug.print("Module: {0}".format(module_name), DebugLevel.info)
            module_import = importlib.import_module(module_name)
            module = module_import.Watchful(self)
            status, message = module.check()

            if isinstance(message, dict):
                if module_name not in self.__status_datos.keys():
                    self.__status_datos[module_name] = {}

                for (key, value) in message.items():
                    globales.GlobDebug.print("Module: {0} - Key: {1} - Val: {2}".format(module_name, key, value), DebugLevel.debug)
                    if self.chcek_status(value['status'], module_name, key):
                        self.__status_datos[module_name][key] = value['status']
                        self.send_message(value['message'])
                        globales.GlobDebug.print('Module: {0}/{1} - New Status: {2}'.format(module_name, key, value['status']), DebugLevel.debug)
                return True
            elif isinstance(message, str):
                if self.chcek_status(status, module_name):
                    self.__status_datos[module_name] = status
                    self.send_message(message)
                    globales.GlobDebug.print("Module: {0} - New Status: {1}".format(module_name, status), DebugLevel.debug)
                return True
            else:
                msg_debug = '\n\n'+'*'*60 + '\n'
                msg_debug = msg_debug + "WARNING: check_module({0}) - Format not implement: {1}\n".format(module_name, type(message))
                msg_debug = msg_debug + 'Data Status: {0}\n'.format(pprint.pprint(status))
                msg_debug = msg_debug + '*'*40 + '\n'
                msg_debug = msg_debug + 'Data Message: {0}\n'.format(pprint.pprint(message))
                msg_debug = msg_debug + '*'*60 + '\n'
                msg_debug = msg_debug + '*'*60 + '\n\n'
                globales.GlobDebug.print(msg_debug, DebugLevel.warning)

        except Exception as e:
            globales.GlobDebug.Exception(e)
        return False

    def check(self):
        list_modules = []
        for module_def in glob.glob(os.path.join(self.dir_modules, '*.py')):
            module_def = os.path.splitext(os.path.basename(module_def))[0]
            if module_def.find('__') == -1:
                list_modules.append(module_def)

        changed = False
        self.__status_datos = {}
        if self.status:
            self.__status_datos = self.status.read()

        max_threads = self.read_conf('threads',5)
        globales.GlobDebug.print("Monitor Max Threads: {0}".format(max_threads), DebugLevel.debug)
        with concurrent.futures.ThreadPoolExecutor(max_workers= max_threads) as executor:
            future_to_run_module = {executor.submit(self.check_module, module): module for module in list_modules}
            for future in concurrent.futures.as_completed(future_to_run_module):
                module = future_to_run_module[future]
                try:
                    if future.result():
                        changed=True
                except Exception as exc:
                    globales.GlobDebug.Exception(exc)

        globales.GlobDebug.print("Debug Status Save:", DebugLevel.debug)
        globales.GlobDebug.print(self.__status_datos, DebugLevel.debug)
        if changed is True:
            self.status.data = self.__status_datos
            self.status.save()
