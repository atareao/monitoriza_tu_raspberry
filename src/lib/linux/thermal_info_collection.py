#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Monitorize your Raspberry Pi
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

__all__ = ['ThermalInfoCollection']

import os
import glob


class ThermalInfoCollection(object):

    __path_thermal = '/sys/class/thermal'

    class ThermalNode(object):

        __path_thermal = '/sys/class/thermal'

        def __init__(self, dev):
            self.dev = dev

        @property
        def dev(self) -> str:
            return self.__dev

        @dev.setter
        def dev(self, val: str):
            if val.strip():
                self.__dev = val
            else:
                pass
                # TODO: Pendiente Controlar si no se define dev.

        @property
        def type(self) -> str:
            type_return = self.__read_file(self.__path_type)
            if type_return is not None:
                type_return = str(type_return).strip()
            else:
                type_return = "Unknown"
            return type_return

        @property
        def temp(self) -> float:
            temp_return = self.__read_file(self.__path_temp)
            if temp_return is not None:
                temp_return = float(temp_return.split('\n')[0]) / 1000.0
            else:
                temp_return = float(0)
            return temp_return

        def __read_file(self, path_file, default_none=None):
            if self.__is_exist_file(path_file):
                output = default_none
                with open(path_file, 'r') as f_buffer:
                    output = f_buffer.read()
                return output
            else:
                return default_none

        def __is_exist_file(self, path_check):
            if str(self.dev).strip():
                if os.path.isfile(self.__path_temp):
                    return True
            return False

        @property
        def __path_dev(self):
            return os.path.join(self.__path_thermal, self.dev)

        @property
        def __path_temp(self):
            return os.path.join(self.__path_dev, 'temp')

        @property
        def __path_type(self):
            return os.path.join(self.__path_dev, 'type')

    def __init__(self, autodetect=False):
        self.nodes = []
        if autodetect:
            self.detect()

    def clear(self):
        self.nodes.clear()

    def count(self) -> int:
        return self.nodes.count

    def detect(self):
        self.clear()
        for dev_lnk in glob.glob(os.path.join(self.__path_thermal, '*')):
            dev_name = os.path.splitext(os.path.basename(dev_lnk))[0]
            self.__add_sensor(dev_name)

    def __add_sensor(self, dev: str):
        if dev.strip():
            node = self.ThermalNode(dev)
            self.nodes.append(node)
            return True
        else:
            return False


if __name__ == "__main__":

    x = ThermalInfoCollection()
    x.detect()

    for item in x.nodes:
        print("Dev:", item.dev, "- Type:", item.type, "- Temp:", item.temp)
        print("")
