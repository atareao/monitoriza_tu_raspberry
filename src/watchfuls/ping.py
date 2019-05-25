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

import time
import lib.debug
import lib.module_base
from multiprocessing.dummy import Pool as ThreadPool


class Watchful(lib.module_base.ModuleBase):

    __default_attempt = 3
    __default_timeout = 5

    def __init__(self, monitor):
        super().__init__(monitor, __name__)
        self.path_file.set('ping', '/bin/ping')

    def check(self):
        list_host = []
        for (key, value) in self.get_conf('list', {}).items():
            self._debug.print("Ping: {0} - Enabled: {1}".format(key, value), lib.debug.DebugLevel.info)
            if value:
                list_host.append(key)

        list_return = []
        pool = ThreadPool(self.get_conf('threads', self._default_threads))
        list_return = pool.map(self.__ping_check, list_host)
        pool.close()
        pool.join()

        self._debug.debug_obj(self.NameModule, list_return, "Data Work")

        # Convertir list en dictionary
        dict_return = {}
        for valueL1 in list_return:
            dict_return = {**dict_return, **valueL1}

        self._debug.debug_obj(self.NameModule, dict_return, "Data Return")
        return True, dict_return

    def __ping_check(self, host):
        # TODO: Pendiente poder configurar número de intentos y timeout para cada IP
        status = self.__ping_return(host,
                                    self.get_conf('threads', self.__default_timeout),
                                    self.get_conf('attempt', self.__default_attempt)
                                    )

        r_check = {}
        r_check[host] = {}
        r_check[host]['status'] = status
        r_check[host]['message'] = ''
        if self.check_status(status, self.NameModule, host):
            s_message = 'Ping: {0}'.format(host)
            if status:
                s_message = '{0} {1}'.format(s_message, u'\U0001F53C')
            else:
                s_message = '{0} {1}'.format(s_message, u'\U0001F53D')
            self.send_message(s_message, status)
        return r_check

    def __ping_return(self, host, timeout, attempt):
        counter = 0
        while counter < attempt:
            cmd = '{0} -c 1 -W {1} {2}'.format(self.path_file.find('ping'), timeout, host)
            r_code = self._run_cmd_call(cmd)
            if r_code == 0:
                return True
            time.sleep(1)
            counter += 1
        return False


if __name__ == '__main__':

    wf = Watchful(None)
    print(wf.check())
