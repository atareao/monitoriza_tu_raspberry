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
from lib.debug import DebugLevel
from lib.modules import ModuleBase


class Watchful(ModuleBase):

    def __init__(self, monitor):
        super().__init__(monitor, __name__)
        self.paths.set('systemctl', '/bin/systemctl')

    def check(self):
        list_service = []
        for (key, value) in self.get_conf('list', {}).items():
            enabled = value['enabled']
            remediation = value['remediation']
            self.debug.print(">> PlugIn >> {0} >> Service: {1} - Enabled: {2} - Remediation: {3}".format(self.name_module, key, enabled, remediation),
                             DebugLevel.info)
            if enabled:
                list_service.append({"service": key, "remediation": remediation})

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.get_conf('threads', self._default_threads)) as executor:
            future_to_service = {executor.submit(self.__service_check, service): service for service in list_service}
            for future in concurrent.futures.as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    future.result()
                except Exception as exc:
                    message = 'Service: {0} - *Error: {1}* {2}'.format(service, exc, u'\U0001F4A5')
                    self.dict_return.set(service, False, message)

        super().check()
        return self.dict_return

    def __service_check(self, service):
        service_name = service['service']
        status, error, message = self.__service_return(service_name)

        s_message = 'Service: {0} '.format(service_name)
        if status:
            s_message += ' - *Running* ' + u'\U00002705'
        else:
           if message:
                s_message += '- *Error: {0}* '.format(message)
            else:
                s_message += '- *Stop* '
            s_message += u'\U000026A0'
            if service['remediation']:
                self.__service_remediation(service_name)
 
        other_data = {'error': error, 'status_detail': message}
        self.dict_return.set(service_name, status, s_message, False, other_data)

        if self.check_status(status, self.name_module, service_name):
            self.send_message(s_message, status)

    def __service_remediation(self, service_name):
        cmd = '{0} start {1}'.format(self.paths.find('systemctl'), service_name)
        self._run_cmd(cmd)

    def __service_return(self, service_name):
        cmd = '{0} status {1}'.format(self.paths.find('systemctl'), service_name)
        stdout, stderr = self._run_cmd(cmd, True)
        if stdout == '':
            return False, True, stderr[:-1]

        for line in stdout.split('\n'):
            s_line = line.split()
            if str(s_line[0]) == 'Active:':
                if str(s_line[1]) == "active":
                    #    Active: active (running) since Mon 2019-05-27 11:28:46 CEST; 1min 48s ago
                    if str(s_line[2]) == "(running)":
                        return True, False, self.__clear_str(s_line[2])
                    else:
                        return False, False, self.__clear_str(s_line[2])
                elif str(s_line[1]) == "inactive":
                    #    Active: inactive (dead) since Mon 2019-05-27 11:30:51 CEST; 1s ago
                    if str(s_line[2]) == "(dead)":
                        return False, False, ''
                    else:
                        return False, False, self.__clear_str(s_line[2])
                else:
                    return False, True, line

        return False, 'Not detect status in the data!!!'

    @staticmethod
    def __clear_str(text: str) -> str:
        if text:
            return str(text).strip().replace("(", "").replace(")", "")
