#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Monitorize your Raspberry Pi
#
# Copyright © 2019  Javier Pastor (aka VSC55)
# <jpastor at cerebelum dot net>
#
# Basado en nginxstatus.py de Lorenzo Carbonell (aka atareao)
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

import importlib

def status(name_srv):
    name_srv = name_srv.strip()
    if not name_srv:
        return False, 'Status Error: Service name is empty!!' #:bangbang:

    utils = importlib.import_module('__utils')
    stdout, stderr = utils.execute('systemctl status '+name_srv)

    if stdout == '':
        return False, 'Status ['+name_srv+'] - Error:'+stderr[:-1] #:rotating_light:
    return True, 'Status ['+name_srv+'] - Ok!' #:like:

#https://apps.timwhitlock.info/emoji/tables/unicode
