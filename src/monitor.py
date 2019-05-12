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
import config
import socket
import concurrent.futures
import pprint
from telegram import Telegram

class Monitor():
    status_datos = {}
    debugMode = False

    def __init__(self):
        self.dir = os.path.dirname(os.path.abspath(__file__))
        self.watchfuls_dir = os.path.join(self.dir, 'watchfuls')
        sys.path.insert(1, self.watchfuls_dir)
        if self.dir.find('src') != -1:
            config_dir = os.path.normpath(os.path.join(self.dir, '../data/'))
        else:
            config_dir = '/etc/watchful/'
        self.status = config.Config(os.path.join(config_dir, 'status.json'))
        self.config = config.Config(os.path.join(config_dir, 'config.json')).read()
        self.tg = Telegram(self.config['token'], self.config['chat_id'])

    def debug(self, message):
        if self.debugMode:
            if isinstance(message, str):
                print(message)
            else:
                pprint.pprint(message)

    def tg_send_message(self, message):
        if message:
            hostname = socket.gethostname()
            self.tg.send_message("[{0}]: {1}".format(hostname, message))


    def chcek_status(self, status, module, module_subkey=''):
        if module_subkey:
            if module not in self.status_datos.keys() or module_subkey not in self.status_datos[module].keys() or (module_subkey in self.status_datos[module].keys() and  self.status_datos[module][module_subkey] != status):
                return True
        else:
            if module not in self.status_datos.keys() or (module in self.status_datos.keys() and  self.status_datos[module] != status):
                return True
        return False

    def check_module(self, module_name):
        try:
            self.debug("Module: {0}".format(module_name))
            module = importlib.import_module(module_name)
            watchful = module.Watchful(self)
            status, message = watchful.check()

            if isinstance(message, dict):
                if module_name not in self.status_datos.keys():
                    self.status_datos[module_name] = {}

                for (key, value) in message.items():
                    self.debug("Module: {0} - Key: {1} - Val: {2}".format(module_name, key, value))
                    if self.chcek_status(value['status'], module_name, key):
                        self.status_datos[module_name][key] = value['status']
                        self.tg_send_message(value['message'])
                        self.debug('Module: {0}/{1} - New Status: {2}'.format(module_name, key, value['status']))
                return True
            elif isinstance(message, str):
                if self.chcek_status(status, module_name):
                    self.status_datos[module_name] = status
                    self.tg_send_message(message)
                    self.debug("Module: {0} - New Status: {1}".format(module_name, status))
                return True
            else:
                print('Format not implement: {0}'.format(type(message)))
                print('Status:')
                pprint.pprint(status)
                print('-------------')
                print('Message:')
                pprint.pprint(message)
                print('-------------')
                print('-------------')
                print('')

        except Exception as e:
            print("Check_Module - Module: {0} - Exception: {1}".format(module_name, e))

        return False

    def check(self):
        listmodules = []
        changed = False
        self.status_datos = self.status.read()
        watchfuls = glob.glob(os.path.join(self.watchfuls_dir, '*.py'))
        for watchful_def in watchfuls:
            watchful_def = os.path.splitext(os.path.basename(watchful_def))[0]
            if watchful_def.find('__') == -1:
                listmodules.append(watchful_def)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_run_module = {executor.submit(self.check_module, module): module for module in listmodules}
            for future in concurrent.futures.as_completed(future_to_run_module):
                module = future_to_run_module[future]
                try:
                    if future.result():
                        changed=True
                except Exception as exc:
                    print('Check - Module: {0} - Exception: {1}'.format(module, exc))


        self.debug(self.status_datos)
        if changed is True:
            self.status.save(self.status_datos)

if __name__ == '__main__':
    monitor = Monitor()
    monitor.check()
