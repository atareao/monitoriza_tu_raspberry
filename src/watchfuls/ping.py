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
import concurrent.futures
from lib import Switch
from lib.debug import DebugLevel
from lib.modules import ModuleBase
from enum import Enum


class ConfigOptions(Enum):
    enabled = 1
    # alert = 2
    label = 3
    timeout = 100
    attempt = 101


class Watchful(ModuleBase):

    __default_attempt = 3
    __default_timeout = 5
    __default_enabled = True

    def __init__(self, monitor):
        super().__init__(monitor, __name__)
        self.path_file.set('ping', '/bin/ping')

    def __debug(self, msg: str, level: DebugLevel = DebugLevel.debug):
        super().debug.print(">> PlugIn >> {0} >> {1}".format(self.name_module, msg), level)

    def check(self):
        list_host = self.__check_get_list_hosts()
        self.__check_run(list_host)
        super().check()
        return self.dict_return

    def __check_get_list_hosts(self):
        return_list = []
        for (key, value) in self.get_conf('list', {}).items():
            if isinstance(value, bool):
                is_enabled = value
            elif isinstance(value, dict):
                is_enabled = self.__get_conf(ConfigOptions.enabled, key)
            else:
                is_enabled = self.__default_enabled

            self.__debug("Ping: {0} - Enabled: {1}".format(key, is_enabled), DebugLevel.info)

            if is_enabled:
                return_list.append(key)

        return return_list

    def __check_run(self, list_host):
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

    def __ping_check(self, host):
        # TODO: Pendiente poder configurar número de intentos y timeout para cada IP

        tmp_host_name = self.__get_conf(ConfigOptions.label, host, host)
        tmp_timeout = self.__get_conf(ConfigOptions.timeout, host)
        tmp_attempt = self.__get_conf(ConfigOptions.attempt, host)

        status = self.__ping_return(host, tmp_timeout, tmp_attempt)

        s_message = 'Ping: *{0}* '.format(tmp_host_name)
        if status:
            s_message += u'\U0001F53C'
        else:
            s_message += u'\U0001F53D'

        self.dict_return.set(host, status, s_message, False)

        if self.check_status(status, self.name_module, host):
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

    def __get_conf(self, opt_find: Enum, dev_name: str, default_val=None):
        # Sec - Get Default Val
        if default_val is None:
            with Switch(opt_find) as case:
                if case(ConfigOptions.attempt):
                    val_def = self.get_conf(opt_find.name, self.__default_attempt)

                elif case(ConfigOptions.timeout):
                    val_def = self.get_conf(opt_find.name, self.__default_timeout)

                elif case(ConfigOptions.enabled):
                    val_def = self.get_conf(opt_find.name, self.__default_enabled)

                else:
                    if opt_find is None:
                        raise ValueError("opt_find it can not be None!")
                    else:
                        raise TypeError("{0} is not valid option!".format(opt_find.name))
        else:
            val_def = default_val

        # Sec - Get Data
        value = self.get_conf_in_list(opt_find, dev_name, val_def)

        # Sec - Format Return Data
        with Switch(opt_find) as case:
            if case(ConfigOptions.attempt, ConfigOptions.timeout):
                value = str(value).strip()
                if not value or not value.isnumeric() or int(value) <= 0:
                    value = val_def
                return int(value)

            elif case(ConfigOptions.enabled):
                return bool(value)

            elif case(ConfigOptions.label):
                value = str(value).strip()
                if not value:
                    value = val_def
                return str(value)

            else:
                return value


if __name__ == '__main__':

    wf = Watchful(None)
    print(wf.check())
