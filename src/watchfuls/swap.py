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
import lib.debug
import lib.module_base
import lib.monitor

class Watchful(lib.module_base.ModuleBase):
    #porcentaje de SWAP que se usara si no se ha configurado el modulo, o se ha definido un valor que no esté entre 0 y 100.
    __default_alert=60

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def check(self):
        usage_alert= self.get_conf("alert", self.__default_alert)
        if isinstance(usage_alert, str):
            usage_alert=usage_alert.strip()
        if not usage_alert or usage_alert < 0 or usage_alert > 100:
            usage_alert=self.__default_alert

        stdout, stderr = lib.tools.execute('free')
        globales.GlobDebug.print(stdout, lib.debug.DebugLevel.debug)

        x = re.findall(r'Swap:\s+(\d+)\s+(\d+)', stdout)
        per = float(x[0][1])/float(x[0][0]) * 100.0
        if per < float(usage_alert):
            return True, 'Normal SWAP used {0:.1f}% {1}'.format(per, u'\U00002705')
        return False, 'Excesive SWAP used {0:.1f}% {1}'.format(per, u'\U000026A0')


if __name__ == '__main__':
    wf = Watchful(None)
    print(wf.check())