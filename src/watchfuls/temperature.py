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

from lib.linux.thermal_info_collection import ThermalInfoCollection
from lib.modules.module_base import ModuleBase
from enum import Enum


class Watchful(ModuleBase):

    # temperatura en ºC que se usara si no se ha configurado el modulo, o se ha definido un valor igual o menor que 0.
    __default_alert = 80
    __default_enabled = True

    class ConfigOptions(Enum):
        enabled = 1
        alert = 2
        label = 3

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def check(self):
        termal_info = ThermalInfoCollection(True)

        for item in termal_info.nodes:
            if not self.__get_conf(self.ConfigOptions.enabled, item.dev):
                continue

            dev_name = item.dev
            type_name = item.type
            type_label = self.__get_conf(self.ConfigOptions.label, dev_name, type_name)
            temp = item.temp
            temp_alert = self.__get_conf(self.ConfigOptions.alert, dev_name)

            if temp <= temp_alert:  # Función OK :)
                is_warning = False
            else:  # Esta echando fuego!!!
                is_warning = True

            message = "Sensor {0}, ".format(type_label)
            if is_warning:
                message += '*over temperature Warning {0:.1f} ºC* {1}'.format(temp, u'\U0001F525')
            else:
                message += 'temperature Ok {0:.1f} ºC {1}'.format(temp, u'\U00002705')
            other_data = {'name': dev_name, 'type': type_name, 'temp': temp}
            self.dict_return.set(dev_name, not is_warning, message, other_data=other_data)

        super().check()
        return self.dict_return

    def __get_conf(self, opt_find: ConfigOptions, dev_name: str, default_val=None):
        # Sec - Get Default Val
        if default_val is None:
            if opt_find == self.ConfigOptions.alert:
                val_def = self.get_conf(opt_find.name, self.__default_alert)

            elif opt_find == self.ConfigOptions.enabled:
                val_def = self.get_conf(opt_find.name, self.__default_enabled)

            else:
                if opt_find is None:
                    raise ValueError("opt_find it can not be None!")
                else:
                    raise TypeError("{0} is not valid option!".format(opt_find.name))
        else:
            val_def = default_val

        # Sec - Get Data
        find_key = [opt_find.name]
        if dev_name:
            find_key.insert(0, dev_name)
            find_key.insert(0, "list")
        value = self.get_conf(find_key, val_def)

        # Sec - Format Return Data
        if opt_find == self.ConfigOptions.alert:
            value = str(value).strip()
            if not value or not value.isnumeric() or float(value) <= 0:
                value = val_def
            return float(value)

        elif opt_find == self.ConfigOptions.enabled:
            return bool(value)

        elif opt_find == self.ConfigOptions.label:
            value = str(value).strip()
            if not value:
                value = val_def
            return str(value)

        else:
            return value


if __name__ == '__main__':

    wf = Watchful(None)
    print(wf.check())
