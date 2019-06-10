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

import os.path
import concurrent.futures
import pymysql
import pymysql.cursors
from lib import Switch
from lib.debug import DebugLevel
from lib.modules import ModuleBase
from enum import Enum


class ConfigOptions(Enum):
    enabled = 1
    # alert = 2
    # label = 3
    host = 100
    port = 101
    user = 102
    password = 103
    db = 104
    socket = 105


class Watchful(ModuleBase):

    __default_enabled = True
    __default_port = 3306

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def __debug(self, msg: str, level: DebugLevel = DebugLevel.debug):
        super().debug.print(">> PlugIn >> {0} >> {1}".format(self.name_module, msg), level)

    def check(self):
        list_db = self.__check_get_list_db()
        self.__check_run(list_db)
        super().check()
        return self.dict_return

    def __check_get_list_db(self):
        return_list = []
        for (key, value) in self.get_conf('list', {}).items():
            if isinstance(value, bool):
                is_enabled = value
            elif isinstance(value, dict):
                is_enabled = self.__get_conf(ConfigOptions.enabled, key)
            else:
                is_enabled = self.__default_enabled

            self.__debug("{0} - Enabled: {1}".format(key, is_enabled), DebugLevel.info)

            if is_enabled:
                return_list.append(key)

        return return_list

    def __check_run(self, list_db):
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.get_conf('threads', self._default_threads)) as executor:
            future_to_db = {executor.submit(self.__db_check, db): db for db in list_db}
            for future in concurrent.futures.as_completed(future_to_db):
                db = future_to_db =[future]
                try:
                    future.result()
                except Exception as exc:
                    message = 'MySQL: {0} - *Error: {1}* {2}'.format(db, exc, u'\U0001F4A5')
                    self.dict_return.set(db, False, message)

    def __db_check(self, db):
        tmp_socket = self.__get_conf(ConfigOptions.socket, db)
        tmp_host = self.__get_conf(ConfigOptions.host, db)
        tmp_port = self.__get_conf(ConfigOptions.port, db)
        tmp_user = self.__get_conf(ConfigOptions.user, db)
        tmp_pass = self.__get_conf(ConfigOptions.password, db)
        tmp_db = self.__get_conf(ConfigOptions.db, db)

        status, message = self.__db_return(db, tmp_socket, tmp_host, tmp_port, tmp_user, tmp_pass, tmp_db)

        s_message = 'MySQL: '
        if status == "OK":
            s_message += '*{0}* {1}'.format(db, u'\U00002705')
            status = True
        else:
            s_message += '{0} - *Error:* '.format(db)
            with Switch(status) as case:
                if case("1045"):
                    # OperationalError(1045, "Access denied for user 'user'@'server' (using password: NO)")
                    # OperationalError(1045, "Access denied for user 'user'@'server' (using password: YES)")
                    s_message += "*Access denied* {0}".format('\U0001F510')
                elif case("2003"):
                    # OperationalError(2003, "Can't connect to MySQL server on 'host1' (timed out)")
                    # OperationalError(2003, "Can't connect to MySQL server on 'host1' ([Errno 113] No route to host)")
                    # OperationalError(2003, "Can't connect to MySQL server on 'host1' ([Errno 111] Connection refused)"
                    s_message += "*Can't connect to MySQL server*"
                    with Switch(message, check_contain=True) as sub_case:
                        if sub_case('(timed out)'):
                            s_message += ' *(timed out)*'
                        elif sub_case('[Errno 111]'):
                            s_message += ' *(connection refused)*'
                        elif sub_case('[Errno 113]'):
                            s_message += ' *(no route to host)*'
                        else:
                            s_message += ' *(?????)*'
                    s_message += '\U000026A0'
                    # s_message += "*Can't connect to MySQL server (time out)* {0}".format('\U000026A0')
                else:
                    s_message += '*{0}* {1}'.format(message, '\U000026A0')
            status = False

        other_data = {'message': message}
        self.dict_return.set(db, status, s_message, False, other_data)

        if self.check_status_custom(status, db, message):
            self.send_message(s_message, status)

    def __db_return(self, db_name, socket, host, port, user, password, db):
        return_status = 0
        return_msg = ""
        connect_socket = True if len(str(socket).strip()) > 0 else False
        try:
            if connect_socket:
                if not os.path.exists(socket):
                    return "SOCKET_NOT_EXIST", "Socket file is not exist!"

                connection = pymysql.connect(unix_socket=socket,
                                             db=db,
                                             charset='utf8mb4',
                                             cursorclass=pymysql.cursors.DictCursor)
            else:
                connection = pymysql.connect(host=host,
                                             port=port,
                                             user=user,
                                             password=password,
                                             db=db,
                                             charset='utf8mb4',
                                             connect_timeout=10,
                                             cursorclass=pymysql.cursors.DictCursor)

        except Exception as e:
            self.debug.print(">> PlugIn >> {0} >> {1} >> Exception: {2}".format(self.name_module, db_name, repr(e)),
                             DebugLevel.error)
            return_msg = repr(e)

            err_array = str(e).split(",")
            err_code = err_array[0][1:]
            with Switch(err_code) as case:
                if case("2003") and connect_socket:
                    return "SOCKET_ERROR", "Socket file is not work!"
                elif case("1045", "2003"):
                    return_status = err_code
                else:
                    return_status = "-9999"

        if not return_msg:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SHOW GLOBAL STATUS")
                    # for row in cursor:
                    #     print("ROW:", row)

                    # result = cursor.fetchone()
                    # print("RESULT SQL:", result)
                    return_status = "OK"

            except Exception as e:
                self.debug.print(">> PlugIn >> {0} >> {1} >> Exception: {2}".format(self.name_module, db_name, repr(e)),
                                 DebugLevel.error)
                return_msg = repr(e)
                return_status = "-9999"

            finally:
                connection.close()

        return return_status, return_msg

    def __get_conf(self, opt_find: Enum, dev_name: str, default_val=None):
        # Sec - Get Default Val
        if default_val is None:
            with Switch(opt_find) as case:
                if case(ConfigOptions.port):
                    val_def = self.get_conf(opt_find.name, self.__default_port)

                elif case(ConfigOptions.socket,
                          ConfigOptions.host,
                          ConfigOptions.user,
                          ConfigOptions.password,
                          ConfigOptions.db):
                    val_def = self.get_conf(opt_find.name, "")

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
            if case(ConfigOptions.port):
                value = str(value).strip()
                if not value or not value.isnumeric() or int(value) <= 0:
                    value = val_def
                return int(value)

            elif case(ConfigOptions.enabled):
                return bool(value)

            elif case(ConfigOptions.socket,
                      ConfigOptions.host,
                      ConfigOptions.user,
                      ConfigOptions.password,
                      ConfigOptions.db):
                value = str(value).strip()
                if not value:
                    value = val_def
                return str(value)

            else:
                return value

    def check_status_custom(self, status, db, status_msg):
        return_status = super().check_status(status, self.name_module, db)

        if status or return_status:
            b_return = return_status
        else:
            msg_status_old = super().get_status_find(db, self.name_module).get("other_data", {}).get("message", '')
            if status_msg != msg_status_old:
                b_return = True
            else:
                b_return = return_status
        return b_return
