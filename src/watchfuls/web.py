#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Monitorize your Raspberry Pi
#
# Copyright © 2019  Lorenzo Carbonell (aka atareao)
# <lorenzo.carbonell.cerezo at gmail dot com>
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
from lib import Switch
from lib.debug import DebugLevel
from lib.modules import ModuleBase


class Watchful(ModuleBase):

    __default_enabled = True
    __default_http_code = 200

    def __init__(self, monitor):
        super().__init__(monitor, __name__)
        self.paths.set('curl', '/usr/bin/curl')

    def check(self):
        list_url = []
        for (key, value) in self.get_conf('list', {}).items():

            is_enabled = self.__default_enabled
            with Switch(value, check_isinstance=True) as case:
                if case(bool):
                    is_enabled = value
                elif case(dict):
                    is_enabled = value.get("enabled", is_enabled)

            self.debug.print(">> PlugIn >> {0} >> Web: {1} - Enabled: {2}".format(self.name_module, key, is_enabled),
                             DebugLevel.info)
            if is_enabled:
                list_url.append(key)

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.get_conf('threads', self._default_threads)) as executor:
            future_to_url = {executor.submit(self.__web_check, url): url for url in list_url}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    future.result()
                except Exception as exc:
                    message = 'Web: {0} - Error: {1}'.format(url, exc)
                    self.dict_return.set(url, False, message)

        super().check()
        return self.dict_return

    def __web_check(self, url):
        code = int(self.__web_return(url))
        code_true = self.get_conf_in_list("code", url, self.__default_http_code)
        status = True if code == code_true else False

        s_message = 'Web: {0} - *({1})*'.format(url, code)
        if status:
            s_message += u'\U0001F53C'
        else:
            s_message += u'\U0001F53D'

        other_data = {'code': code}
        self.dict_return.set(url, status, s_message, False, other_data)

        if self.check_status(status, self.name_module, url):
            self.send_message(s_message, status)

    def __web_return(self, url):
        # TODO: Pendiente añadir soporte https.
        cmd = self.paths.find('curl')
        cmd += ' -sL -w "%{http_code}" http://' + url + ' -o /dev/null'
        stdout = self._run_cmd(cmd)
        return str(stdout).strip()
