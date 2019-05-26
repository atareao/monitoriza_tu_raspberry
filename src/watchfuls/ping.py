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
import lib.modules.module_base
import concurrent.futures


class Watchful(lib.modules.module_base.ModuleBase):

    __default_attempt = 3
    __default_timeout = 5

    def __init__(self, monitor):
        super().__init__(monitor, __name__)
        self.path_file.set('ping', '/bin/ping')

    def check(self):
        list_host = []
        for (key, value) in self.get_conf('list', {}).items():
            self.debug.print("Ping: {0} - Enabled: {1}".format(key, value), lib.debug.DebugLevel.info)
            if value:
                list_host.append(key)

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.get_conf('threads', self._default_threads)) as executor:
            future_to_ping = {executor.submit(self.__ping_check, host): host for host in list_host}
            for future in concurrent.futures.as_completed(future_to_ping):
                host = future_to_ping[future]
                try:
                    future.result()
                except Exception as exc:
                    message = 'Ping: {0} - *Error: {1}* {2}'.format(host, exc, u'\U0001F4A5')
                    self.dict_return.set(host, False, message)

        super().check()
        return self.dict_return

    def __ping_check(self, host):
        # TODO: Pendiente poder configurar número de intentos y timeout para cada IP
        status = self.__ping_return(host,
                                    self.get_conf('threads', self.__default_timeout),
                                    self.get_conf('attempt', self.__default_attempt)
                                    )

        s_message = 'Ping: {0} '.format(host)
        if status:
            s_message += u'\U0001F53C'
        else:
            s_message += u'\U0001F53D'

        self.dict_return.set(host, status, s_message, False)
        if self.check_status(status, self.NameModule, host):
            self.send_message(s_message, status)

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
