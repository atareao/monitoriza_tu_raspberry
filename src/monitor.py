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
import sys
import importlib
import socket
import pprint
import logging
import concurrent.futures
from lib.telegram import *
from lib.debug import *
from lib.config import *
from lib.module_base import *

__all__ = ['debug', 'monitor', 'Monitor']

debug = None
monitor = None

class Monitor():

    def __init__(self):
        __status_datos = {}
        global debug
        if not debug:
            debug = Debug(True)

        self.__readConfig()
        self.__readStatus()
        self.__initTelegram()
        sys.path.insert(1, self.modules_dir)

    def __readConfig(self):
        self.config_global = Config(os.path.join(self.config_dir, 'config.json')).read()
        self.config_modules = Config(os.path.join(self.config_dir, 'modules.json')).read()

        if self.config_global:
            if 'global' in self.config_global.keys() and 'debug' in self.config_global['global']:
                #debug.enabled = self.config_global['global']['debug']
                pass
        
    def __readStatus(self):
        self.status = Config(os.path.join(self.config_dir, 'status.json'))

    def __initTelegram(self):
        if self.config_global:
            self.tg = Telegram(self.config_global['telegram']['token'], self.config_global['telegram']['chat_id'])

    @property
    def dir(self):
        return os.path.dirname(os.path.abspath(__file__))

    @property
    def modules_dir(self):
        return os.path.join(self.dir, 'watchfuls')

    @property
    def config_dir(self):
        if self.dir.find('src') != -1:
            return os.path.normpath(os.path.join(self.dir, '../data/'))
        else:
            return '/etc/watchful/'


    def send_message(self, message):
        if message:
            hostname = socket.gethostname()
            self.tg.send_message("[{0}]: {1}".format(hostname, message))

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
            debug.print("Module: {0}".format(module_name), DebugLevel.info)
            module_import = importlib.import_module(module_name)
            module = module_import.Watchful()
            status, message = module.check()

            if isinstance(message, dict):
                if module_name not in self.__status_datos.keys():
                    self.__status_datos[module_name] = {}

                for (key, value) in message.items():
                    debug.print("Module: {0} - Key: {1} - Val: {2}".format(module_name, key, value), DebugLevel.debug)
                    if self.chcek_status(value['status'], module_name, key):
                        self.__status_datos[module_name][key] = value['status']
                        self.send_message(value['message'])
                        debug.print('Module: {0}/{1} - New Status: {2}'.format(module_name, key, value['status']), DebugLevel.debug)
                return True
            elif isinstance(message, str):
                if self.chcek_status(status, module_name):
                    self.__status_datos[module_name] = status
                    self.send_message(message)
                    debug.print("Module: {0} - New Status: {1}".format(module_name, status), DebugLevel.debug)
                return True
            else:
                debug.print('WARNING: Format not implement: {0}\nData Status:\n{1}\n{2}\nData Message:\n{3}\n{2}\n{2}\n\n'.format(type(message), pprint.pprint(status),'-'*60, pprint.pprint(message)))

        except Exception as e:
            debug.Exception(e)
        return False

    def check(self):
        list_modules = []
        for module_def in glob.glob(os.path.join(self.modules_dir, '*.py')):
            module_def = os.path.splitext(os.path.basename(module_def))[0]
            if module_def.find('__') == -1:
                list_modules.append(module_def)
                break

        changed = False
        self.__status_datos = self.status.read()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_run_module = {executor.submit(self.check_module, module): module for module in list_modules}
            for future in concurrent.futures.as_completed(future_to_run_module):
                module = future_to_run_module[future]
                try:
                    if future.result():
                        changed=True
                except Exception as exc:
                    debug.Exception(exc)

        debug.print("Debug Status Save:", DebugLevel.debug)
        debug.print(self.__status_datos, DebugLevel.debug)
        if changed is True:
            self.status.save(self.__status_datos)

if __name__ == '__main__':
    debug = Debug(True)
    monitor = Monitor()
    monitor.check()
