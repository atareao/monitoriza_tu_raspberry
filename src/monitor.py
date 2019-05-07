#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Monitorize your Raspberry Pi
#
# Copyright © 2019  Lorenzo Carbonell (aka atareao)
# <lorenzo.carbonell.cerezo at gmail dot com>
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
from telegram import Telegram

class Monitor():

    def __init__(self):
        self.dir = os.path.dirname(os.path.abspath(__file__))
        self.watchfuls_dir = os.path.join(self.dir, 'watchfuls')
        sys.path.insert(1, self.watchfuls_dir)
        if self.dir.find('src') != -1:
            config_dir = os.path.normpath(os.path.join(self.dir, '../data/'))
        else:
            config_dir = '/etc/watchful/'
        self.status = config.Config(os.path.join(config_dir, 'status.json'))
        init = config.Config(os.path.join(config_dir, 'config.json')).read()
        self.tg = Telegram(init['token'], init['chat_id'])

    def check(self):
        changed = False
        data = self.status.read()
        watchfuls = glob.glob(os.path.join(self.watchfuls_dir, '*.py'))
        for watchful_def in watchfuls:
            try:
                watchful_def = os.path.splitext(os.path.basename(watchful_def))[0]
                if watchful_def.find('__') == -1:
                    print(watchful_def)
                    module = importlib.import_module(watchful_def)
                    watchful = module.Watchful()
                    status, message = watchful.check()
                    if watchful_def not in data.keys() or (watchful_def in data.keys()
                        and data[watchful_def] != status):
                        data[watchful_def] = status
                        print(watchful_def, status)
                        self.tg.send_message(message)
                        changed = True
            except Exception as e:
                print(e)
        if changed is True:
            self.status.save(data)

if __name__ == '__main__':
    monitor = Monitor()
    monitor.check()
 