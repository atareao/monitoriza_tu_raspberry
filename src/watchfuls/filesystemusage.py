#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Monitorize your Raspberry Pi
#
# Copyright © 2019  Lorenzo Carbonell (aka atareao)
# <lorenzo.carbonell.cerezo at gmail dot com>
#
# Copyright © 2019  Javier Pastor (aka vsc55)
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

import re
import lib.module_base


class Watchful(lib.module_base.ModuleBase):

    # porcentaje que se usara si no se ha configurado el modulo, o se ha definido un valor que no esté entre 0 y 100.
    __default_alert = 85

    def __init__(self, monitor):
        super().__init__(monitor, __name__)
        self.path_file.set('df', '/bin/df')

    def check(self):
        list_partition = self.get_conf('list', {})

        usage_alert = self.get_conf("alert", self.__default_alert)
        if isinstance(usage_alert, str):
            usage_alert = usage_alert.strip()
        if not usage_alert or usage_alert < 0 or usage_alert > 100:
            usage_alert = self.__default_alert

        cmd = '{0} -x squashfs -x tmpfs  -x devtmpfs'.format(self.path_file.find('df'))
        stdout = self._run_cmd(cmd)
        reg = r'\/dev\/([^\s]*)\s+\d+\s+\d+\s+\d+\s+(\d+)\%\s+([^\n]*)'

        for fs in re.findall(reg, stdout):
            # fs = ('mmcblk0p6', '32', '/boot')
            mount_point = fs[2]
            if mount_point in list_partition.keys():
                for_usage_alert = list_partition[mount_point]
            else:
                for_usage_alert = usage_alert

            if float(fs[1]) > float(for_usage_alert):
                tmp_status = False
                tmp_message = 'Warning partition {0} ({1}) used {2}% {3}'.format(fs[0], fs[2], fs[1], u'\U000026A0')
            else:
                tmp_status = True
                tmp_message = 'Filesystem partition {0} ({1}) used {2}% {3}'.format(fs[0], fs[2], fs[1], u'\U00002705')

            self.dict_return.set(fs[0], tmp_status, tmp_message)

        super().check()
        return self.dict_return


if __name__ == '__main__':

    wf = Watchful(None)
    print(wf.check())
