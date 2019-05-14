#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

from lib.module_base import ModuleBase

class Watchful(ModuleBase):

    def __init__(self, monitor, debug = False):
        ModuleBase.__init__(self,__name__, monitor, debug)

    def check(self):
        f = open('/sys/class/thermal/thermal_zone0/temp', 'r')
        temp = float(f.read().split('\n')[0])/1000.0
        f.close()
        if temp <= 80:
            return True, 'Temperature ok {0} ºC '.format(temp) + u'\U00002705'
        return False, 'Over temperature warning {0} ºC '.format(temp) + u'\U0001F525'


if __name__ == '__main__':
    wf = Watchful()
    print(wf.check())