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

    #porcentaje que se usara si no se ha configurado el modulo, o se ha definido un valor que no esté entre 0 y 100.
    __default_alert=85

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def check(self):

        list_partition=self.get_conf('list', {})

        usage_alert= self.get_conf("alert", self.__default_alert)
        if isinstance(usage_alert, str):
            usage_alert=usage_alert.strip()
        if not usage_alert or usage_alert < 0 or usage_alert > 100:
            usage_alert=self.__default_alert

        stdout, stderr = lib.tools.execute('df -x squashfs -x tmpfs  -x devtmpfs')
        reg = r'\/dev\/([^\s]*)\s+\d+\s+\d+\s+\d+\s+(\d+)\%\s+([^\n]*)'

        returnDict = {}
        for fs in re.findall(reg, stdout):
            mount_point=fs[2]
            returnDict[mount_point]={}
            if mount_point in list_partition.keys():
                for_usage_alert=list_partition[mount_point]
            else:
                for_usage_alert=usage_alert

            if float(fs[1]) > float(for_usage_alert):
                returnDict[mount_point]['status']=False
                returnDict[mount_point]['message']='Warning partition {0} ({1}) used {2}% {3}'.format(fs[0], fs[2], fs[1], u'\U000026A0')
            else:
                returnDict[mount_point]['status']=True
                returnDict[mount_point]['message']='Filesystem used {0}% {1}'.format(fs[1], u'\U00002705')

        msg_debug = '*'*60 + '\n'
        msg_debug = msg_debug + "Debug [{0}] - Data Return:\n".format(self.NameModule)
        msg_debug = msg_debug + "Type: {0}\n".format(type(returnDict))
        msg_debug = msg_debug + str(returnDict) + '\n'
        msg_debug = msg_debug + '*'*60 + '\n'
        globales.GlobDebug.print(msg_debug, lib.debug.DebugLevel.debug)
        return True, returnDict


if __name__ == '__main__':
    wf = Watchful(None)
    print(wf.check())