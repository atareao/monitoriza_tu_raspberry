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

import lib.modules.module_base


class Watchful(lib.modules.module_base.ModuleBase):

    # temperatura en ºC que se usara si no se ha configurado el modulo, o se ha definido un valor igual o menor que 0.
    __default_alert = 80

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def check(self):
        # TODO: Pendiente controlar multiples "thermal_zone*" o sensores.

        temp_alert = self.get_conf("alert", self.__default_alert)
        if isinstance(temp_alert, str):
            temp_alert = temp_alert.strip()
        if not temp_alert or temp_alert <= 0:
            temp_alert = self.__default_alert

        temp = self.__cpu_temp()
        if temp <= float(temp_alert):   # Función OK :)
            is_warning = False
        else:                           # Esta echando fuego!!!
            is_warning = True

        if is_warning:
            message = 'Over temperature Warning {0} ºC {1}'.format(temp, u'\U0001F525')
        else:
            message = 'Temperature Ok {0} ºC {1}'.format(temp, u'\U00002705')
        self.dict_return.set("cpu", not is_warning, message)
        super().check()
        return self.dict_return

    @staticmethod
    def __cpu_temp():
        # TODO: Pendiente controlar multiples "thermal_zone*"
        f = open('/sys/class/thermal/thermal_zone0/temp', 'r')
        temp = float(f.read().split('\n')[0]) / 1000.0
        f.close()
        return temp


if __name__ == '__main__':

    wf = Watchful(None)
    print(wf.check())
