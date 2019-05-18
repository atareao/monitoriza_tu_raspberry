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

import globales
import os
import sys
from lib.debug import *
from lib.config import *
from lib.monitor import *

def _dir():
    return os.path.dirname(os.path.abspath(__file__))

def _modules_dir():
    return os.path.join(_dir(), 'watchfuls')

def _config_dir():
    if _dir().find('src') != -1:
        return os.path.normpath(os.path.join(_dir(), '../data/'))
    else:
        return '/etc/watchful/'

def _var_dir():
    if _dir().find('src') != -1:
        return '/var/lib/watchful/dev'
    else:
        return '/var/lib/watchful/'

if __name__ == "__main__":
    globales.GlobDebug = Debug(True)

    Config_General = Config(os.path.join(_config_dir(), 'config.json')).read()
    if Config_General:
        if 'global' in Config_General.keys() and 'debug' in Config_General['global']:
            globales.GlobDebug.enabled = Config_General['global']['debug']

    sys.path.insert(1, _modules_dir())

    #globales.GlobDebug.enabled = True

    globales.GlobMonitor = Monitor(_dir(), _config_dir(), _modules_dir(), _var_dir())
    globales.GlobMonitor.check()
