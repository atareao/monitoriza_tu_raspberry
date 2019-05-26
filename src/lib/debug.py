#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Monitorize your Raspberry Pi
#
# Copyright © 2019  Javier Pastor (aka VSC55)
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

import pprint
import traceback
from enum import Enum

__all__ = ['DebugLevel', 'Debug']


class DebugLevel(Enum):
    null = 0
    debug = 1
    info = 2
    warning = 3
    error = 4
    emergency = 5


class Debug(object):

    def __init__(self, enable: bool = True, level: DebugLevel = DebugLevel.info):
        self.enabled = enable
        self.level = level

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, val):
        self.__enabled = val

    @property
    def level(self) -> DebugLevel:
        return self.__level

    @level.setter
    def level(self, val: DebugLevel = DebugLevel.null):
        self.__level = val

    def print(self, message, msg_level: DebugLevel = DebugLevel.debug, force: bool = False):
        show_msg = True
        if self.enabled is False:
            show_msg = False
        elif force is False:
            if self.level.value > msg_level.value:
                show_msg = False

        if show_msg:
            if isinstance(message, str):
                print(message)
            else:
                pprint.pprint(message)

    @staticmethod
    def exception(ex=None):
        # str_obj = pprint.pformat(ex)
        msg_print = 'Exception in user code:\n'
        msg_print += '-'*60+'\n'
        if ex:
            msg_print += 'Exception: ' + str(ex) + '\n'
            msg_print += '-'*60+'\n'
        msg_print += str(traceback.format_exc()) + '\n'
        msg_print += '-'*60+'\n'
        print(msg_print)

    def debug_obj(self, name_module, obj_debug, obj_info="Data Object"):
        str_obj = pprint.pformat(obj_debug)
        msg_debug = '*' * 60 + '\n'
        msg_debug += "Debug [{0}] - {1}:\n".format(name_module, obj_info)
        msg_debug += "Type: {0}\n".format(type(obj_debug))
        msg_debug += str_obj + '\n'
        msg_debug += '*' * 60 + '\n'
        self.print(msg_debug, DebugLevel.debug)


if __name__ == '__main__':

    x = Debug()
    try:
        x.print("Msg Test 1 - Enabled = False and Level Debug - No Show")
        x.print("Msg Test 2 - Level Error - Yes Show", DebugLevel.error)
        x.print("Msg Test 3 - Force = True and Level Debug - Yes Show", DebugLevel.debug, True)
        x.level = DebugLevel.debug
        x.print("Msg Test 4 - Level = debug - Yes Show")
        val = 10 * (1/0)
    except Exception as e:
        x.exception(e)
