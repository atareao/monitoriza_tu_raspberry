#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Monitorize your Raspberry Pi
#
# Copyright © 2019  Lorenzo Carbonell (aka atareao)
# <lorenzo.carbonell.cerezo at gmail dot com>

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

from lib.linux import Mem
from lib.debug import DebugLevel
from lib.modules import ModuleBase


class Watchful(ModuleBase):

    # porcentaje de RAM/SWAP que se usara si no se ha configurado el modulo, o se ha definido un
    # valor que no esté entre 0 y 100.
    __default_alert_ram = 60
    __default_alert_swap = 60

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def __check_config(self, key_conf, default_val):
        val_conf = self.get_conf(key_conf, default_val)

        if isinstance(val_conf, str):
            val_conf = val_conf.strip()
            if not val_conf.isnumeric():
                val_conf = default_val
                self.debug("PlugIn > {0} > Warning, config {1} type incorrect!".format(self.name_module, key_conf),
                           DebugLevel.warning)
            else:
                val_conf = int(val_conf)

        if not val_conf or val_conf < 0 or val_conf > 100:
            val_conf = default_val
            self.debug("PlugIn > {0} > Warning, config {1} value not valid!".format(self.name_module, key_conf),
                       DebugLevel.warning)

        return val_conf

    def check(self):
        x = {
            'ram': {
                'caption': 'RAM',
                'alarm': self.__check_config("alert_ram", self.__default_alert_ram),
                'used': Mem().ram.used_percent
            },
            'swap': {
                'caption': 'SWAP',
                'alarm': self.__check_config("alert_swap", self.__default_alert_swap),
                'used': Mem().swap.used_percent
            }
        }

        for (key, value) in x.items():
            per = float(value['used'])
            alert = float(value['alarm'])
            if per < alert:
                is_warning = False
            else:
                is_warning = True

            message = '{0} used {1:.1f}%'.format(value['caption'], per)
            if is_warning:
                message = 'Excessive {0} {1}'.format(message, u'\U000026A0')
            else:
                message = 'Normal {0} {1}'.format(message, u'\U00002705')

            other_data = {'used': per, 'alert': alert}
            self.dict_return.set(key, not is_warning, message, other_data=other_data)

        super().check()
        return self.dict_return


if __name__ == '__main__':

    wf = Watchful(None)
    print(wf.check())
