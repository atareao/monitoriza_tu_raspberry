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

import concurrent.futures
import lib.debug
import lib.module_base


class Watchful(lib.module_base.ModuleBase):

    def __init__(self, monitor):
        super().__init__(monitor, __name__)
        self.path_file.set('systemctl', '/bin/systemctl')

    def check(self):
        list_service = []
        for (key, value) in self.get_conf('list', {}).items():
            self._debug.print("Service: {0} - Enabled: {1}".format(key, value), lib.debug.DebugLevel.info)
            if value:
                list_service.append(key)

        dict_return = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.get_conf('threads', self._default_threads)) as executor:
            future_to_service = {executor.submit(self.__service_check, service): service for service in list_service}
            for future in concurrent.futures.as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    dict_return[service] = future.result()
                except Exception as exc:
                    dict_return[service] = {}
                    dict_return[service]['status'] = False
                    dict_return[service]['message'] = 'Service: {0} - *Error: {1}* {1}'.format(service,
                                                                                               str(exc),
                                                                                               u'\U0001F4A5')

        self._debug.debug_obj(self.NameModule, dict_return, "Data Return")
        return True, dict_return

    def __service_check(self, service):
        status, message = self.__service_return(service)
        r_check = {}
        r_check['status'] = status
        r_check['message'] = ''
        if self.check_status(status, self.NameModule, service):
            s_message = 'Service: {0}'.format(service)
            if status:
                s_message = '{0} {1}'.format(s_message, u'\U00002705')
            else:
                s_message = '{0} - *Error: {1}* {2}'.format(s_message, message, u'\U000026A0')
            self.send_message(s_message, status)
        return r_check

    def __service_return(self, service):
        cmd = '{0} status {1}'.format(self.path_file.find('systemctl'), service)
        stdout, stderr = self._run_cmd(cmd, True)
        if stdout == '':
            return False, stderr[:-1]
        return True, ''


if __name__ == '__main__':

    wf = Watchful(None)
    print(wf.check())
