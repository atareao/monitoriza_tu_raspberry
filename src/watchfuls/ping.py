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

import lib.tools
import time
from multiprocessing.dummy import Pool as ThreadPool
import lib.debug
import lib.module_base
import lib.monitor


class Watchful(lib.module_base.ModuleBase):

    __default_attempt = 3
    __default_timeout = 5

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def check(self):
        lHost = []
        for (key, value) in self.get_conf('list', {}).items():
            self._debug.print("Ping: {0} - Enabled: {1}".format(key, value), lib.debug.DebugLevel.info)
            if value:
                lHost.append(key)

        lReturn = []
        pool = ThreadPool(self.get_conf('threads', self._default_threads))
        lReturn = pool.map(self.__ping_check, lHost)
        pool.close()
        pool.join()

        msg_debug = '*'*60 + '\n'
        msg_debug = msg_debug + "Debug [{0}] - Data Work:\n".format(self.NameModule)
        msg_debug = msg_debug + "Type: {0}\n".format(type(lReturn))
        msg_debug = msg_debug + str(lReturn) + '\n'
        msg_debug = msg_debug + '*'*60 + '\n'
        self._debug.print(msg_debug, lib.debug.DebugLevel.debug)

        # Convertir list en dictionary
        dReturn = {}
        for valueL1 in lReturn:
            dReturn = {**dReturn, **valueL1}

        msg_debug = '*'*60 + '\n'
        msg_debug = msg_debug + "Debug [{0}] - Data Return:\n".format(self.NameModule)
        msg_debug = msg_debug + "Type: {0}\n".format(type(dReturn))
        msg_debug = msg_debug + str(dReturn) + '\n'
        msg_debug = msg_debug + '*'*60 + '\n'
        self._debug.print(msg_debug, lib.debug.DebugLevel.debug)
        return True, dReturn

    def __ping_check(self, host):
        # TODO: Pendiente poder configurar número de intentos y timeout para cada IP
        status = self.__ping_return(host, self.get_conf('threads', self.__default_timeout), self.get_conf('attempt', self.__default_attempt))

        rCheck = {}
        rCheck[host] = {}
        rCheck[host]['status'] = status
        rCheck[host]['message'] = ''
        if self.chcek_status(status, self.NameModule, host):
            sMessage = 'Ping: {0}'.format(host)
            if status:
                sMessage = '{0} {1}'.format(sMessage, u'\U0001F53C')
            else:
                sMessage = '{0} {1}'.format(sMessage, u'\U0001F53D')
            self.send_message(sMessage, status)
        return rCheck

    def __ping_return(self, host, timeout, attempt):
        counter = 0
        while counter < attempt:
            cmd = 'ping -c 1 -W {0} {1}'.format(timeout, host)
            rCode = self._run_cmd_call(cmd)
            if rCode == 0:
                return True
            time.sleep(1)
            counter += 1
        return False


if __name__ == '__main__':

    wf = Watchful(None)
    print(wf.check())
