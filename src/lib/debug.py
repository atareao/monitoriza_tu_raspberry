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

    def __init__(self, enable=False):
        self.enabled = enable

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, val):
        self.__enabled = val

    def print(self, message, level=DebugLevel.debug, force=False):
        if self.enabled is True or force is True or level == DebugLevel.warning or level == DebugLevel.error or level == DebugLevel.emergency:
            if isinstance(message, str):
                print(message)
            else:
                pprint.pprint(message)

    def Exception(self, ex=None):
        msg_print = 'Exception in user code:\n'
        msg_print = msg_print + '-'*60+'\n'
        if ex:
            msg_print = msg_print + 'Exception: ' + str(ex) + '\n'
            msg_print = msg_print + '-'*60+'\n'
        msg_print = msg_print + str(traceback.format_exc()) + '\n'
        msg_print = msg_print + '-'*60+'\n'
        print(msg_print)


if __name__ == '__main__':
    pass
#    debug = Debug(False)
#    try:
#        debug.print("Msg Test 1 - Enabled = False and Level Debug - No Show")
#        debug.print("Msg Test 2 - Level Error - Yes Show", DebugLevel.error)
#        debug.print("Msg Test 3 - Force = True and Level Debug - Yes Show", DebugLevel.debug, True)
#        debug.enabled = True
#        debug.print("Msg Test 4 - Enabled = True and Level Debug - Yes Show")
#        test = 1 + A
#    except Exception as exc:
#        debug.Exception()
