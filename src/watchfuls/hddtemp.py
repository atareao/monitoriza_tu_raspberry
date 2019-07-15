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
import telnetlib
from lib import Switch
from lib.debug import DebugLevel
from lib.modules import ModuleBase


class Watchful(ModuleBase):

    __default_enabled = True
    __default_port = 7634
    __default_alert = 50
    __default_threads = 5
    __default_timeout = 5

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def __debug(self, msg: str, level: DebugLevel = DebugLevel.debug):
        super().debug.print(">> PlugIn >> {0} >> {1}".format(self.name_module, msg), level)

    def check(self):
        list_hosts = self.__check_get_list_hosts()
        self.__check_run(list_hosts)
        super().check()
        return self.dict_return

    def __check_get_list_hosts(self):
        return_list = []
        for (key, value) in self.get_conf('list', {}).items():
            is_enabled = self.__default_enabled
            with Switch(value, check_isinstance=True) as case:
                if case(bool):
                    is_enabled = value
                elif case(dict):
                    is_enabled = value.get("enabled", is_enabled)

            self.__debug("{0} - Enabled: {1}".format(key, is_enabled), DebugLevel.info)
            if is_enabled:
                if not value.get("host", None):
                    self.__debug("{0} - Host is not defined!".format(key), DebugLevel.warning)
                else:
                    new_hddtemp = self.Hddtemp_Info(key)
                    new_hddtemp.host = value.get("host")
                    new_hddtemp.port = value.get("port", self.__default_port)
                    new_hddtemp.alert = self.get_conf('alert', self.__default_alert)
                    new_hddtemp.exclude = value.get("exclude", [])
                    return_list.append(new_hddtemp)

        return return_list

    def __check_run(self, list_hosts):
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.get_conf('threads', self._default_threads)) as executor:
            future_to_hddtemp = {executor.submit(self.__hddtemp_check, hddtemp): hddtemp for hddtemp in list_hosts}
            for future in concurrent.futures.as_completed(future_to_hddtemp):
                hddtemp = future_to_hddtemp[future]
                try:
                    future.result()
                except Exception as exc:
                    message = 'HDD: {0} - *Error: {1}* {2}'.format(hddtemp, exc, u'\U0001F4A5')
                    self.dict_return.set(hddtemp, False, message)

    def __hddtemp_check(self, hddtemp):
        if self.__hddtemp_return(hddtemp):
            for (key, value) in hddtemp.list_hdd.items():
                if key not in hddtemp.exclude:
                    # print("dev:", key)
                    # print("prop:", value)
                    hdd_name = hddtemp.label + '_' + key
                    hdd_dev = key
                    hdd_alert = value['ALERT']
                    hdd_temp = value['TEMP']
                    hdd_unit = value['TEMP_UNIT']
                    status = True if hdd_alert >= hdd_temp else False
                    s_message = '({}): *{}* *({}º{})*'.format(hddtemp.label, hdd_dev, hdd_temp, hdd_unit)
                    if status:
                        s_message += u'\U0001F53C'
                    else:
                        s_message += u'\U0001F53D'

                    other_data = value
                    self.dict_return.set(hdd_name, status, s_message, False, other_data)

                    if self.check_status(status, self.name_module, hdd_name):
                        self.send_message(s_message, status)

        else:
            self.__debug("{0} >> Exception: {1}".format(hddtemp.label, hddtemp.error), DebugLevel.warning)
            s_message = 'HddTemp: {} - *Error:* *{}*'.format(hddtemp.label, hddtemp.error)
            s_message += u'\U0001F53D'

            other_data = {'message': str(hddtemp.error)}
            self.dict_return.set(hddtemp.label, False, s_message, False, other_data)

            if self.check_status_custom(False, hddtemp.label, hddtemp.error):
                self.send_message(s_message, False)

    def __hddtemp_return(self, hddtemp):
        timeout = self.get_conf('timeout', self.__default_timeout)
        try:
            if timeout > 0:
                tn = telnetlib.Telnet(hddtemp.host, hddtemp.port, timeout)
            else:
                tn = telnetlib.Telnet(hddtemp.host, hddtemp.port)
            # decode('ascii') removes the B char that appears at the beginning of the string
            read_all = str(tn.read_all().decode('ascii'))

        except Exception as exc:
            hddtemp.error = exc
            return False

        list_hdd = read_all.split("||")
        for value in list_hdd:
            item_hdd = str(value).split("|")
            # Remove items None.
            item_hdd = list(filter(None, item_hdd))

            # /dev/sda|ST2000VN004-2E4164|29|C
            new_hdd = {
                'DEV': str(item_hdd[0]).strip(),
                'MODEL': str(item_hdd[1]).strip(),
                'TEMP': int(item_hdd[2]),
                'TEMP_UNIT': str(item_hdd[3]).strip(),
                'ALERT': int(hddtemp.alert)
            }
            hddtemp.list_hdd[new_hdd['DEV']] = new_hdd
        return True

    def check_status_custom(self, status, hddtemp, status_msg):
        return_status = super().check_status(status, self.name_module, hddtemp)

        if status or return_status:
            b_return = return_status
        else:
            msg_status_old = super().get_status_find(hddtemp, self.name_module).get("other_data", {}).get("message", '')
            if str(status_msg) != str(msg_status_old):
                b_return = True
            else:
                b_return = return_status
        return b_return

    class Hddtemp_Info(object):

        __label = ""
        __host = ""
        __port = 0
        __alert = 0
        __exclude = []
        __list_hdd = {}
        __error = ""

        def __init__(self, label):
            self.label = label

        @property
        def label(self) -> str:
            return self.__label

        @label.setter
        def label(self, val: str):
            self.__label = val

        @property
        def host(self) -> str:
            return self.__host

        @host.setter
        def host(self, val: str):
            self.__host = val

        @property
        def port(self) -> int:
            return self.__port

        @port.setter
        def port(self, val: int):
            self.__port = val

        @property
        def alert(self) -> int:
            return self.__alert

        @alert.setter
        def alert(self, val: int):
            self.__alert = val

        @property
        def exclude(self) -> list:
            return self.__exclude

        @exclude.setter
        def exclude(self, val: list):
            self.__exclude = val

        @property
        def list_hdd(self) -> dict:
            return self.__list_hdd

        @list_hdd.setter
        def list_hdd(self, val: dict):
            self.__list_hdd = val

        @property
        def error(self) -> str:
            return self.__error

        @error.setter
        def error(self, val: str):
            self.__error = val
