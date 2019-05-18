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

import re
import lib.tools
import globales
from lib.debug import *
from lib.monitor import *
from lib.module_base import *

class Watchful(ModuleBase):
    
    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def check(self):
        stdout, stderr = lib.tools.execute('free')
        globales.GlobDebug.print(stdout, DebugLevel.debug)
        x = re.findall(r'Swap:\s+(\d+)\s+(\d+)', stdout)
        per = float(x[0][1])/float(x[0][0]) * 100.0
        if per < 50:
            return True, 'Normal swap used {0:.1f}% '.format(per) + u'\U00002705'
        return False, 'Excesive raswapm used {0:.1f}% '.format(per) + u'\U000026A0'


if __name__ == '__main__':
    wf = Watchful()
    print(wf.check())