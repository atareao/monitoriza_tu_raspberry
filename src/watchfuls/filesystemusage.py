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
        ModuleBase.__init__(self, monitor, __name__)

    def check(self):
        stdout, stderr = lib.tools.execute('df -x squashfs -x tmpfs')
        reg = r'\/dev\/([^\s]*)\s+\d+\s+\d+\s+\d+\s+(\d+)\%\s+([^\n]*)'
        for fs in re.findall(reg, stdout):
            if float(fs[1]) > 85:
                return False, 'Warning partition {0} ({1}) used {2}% '.format(
                    fs[0], fs[2], fs[1]) + u'\U000026A0'
        return True, 'Filesystem used under 80% ' + u'\U00002705'


if __name__ == '__main__':
    wf = Watchful()
    print(wf.check())