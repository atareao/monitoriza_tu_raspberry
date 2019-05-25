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
import lib.debug
import lib.module_base


class Watchful(lib.module_base.ModuleBase):

    def __init__(self, monitor):
        super().__init__(monitor, __name__)
        self.path_file.set('curl', '/usr/bin/curl')

    def check(self):
        list_url = []
        for (key, value) in self.get_conf('list', {}).items():
            self._debug.print("Web: {0} - Enabled: {1}".format(key, value), lib.debug.DebugLevel.info)
            if value:
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
        status = self.__web_return(url)
        if self.check_status(status, self.NameModule, url):
            s_message = 'Web: {0}'.format(url)
            if status:
                s_message = '{0} {1}'.format(s_message, u'\U0001F53C')
            else:
                s_message = '{0} {1}'.format(s_message, u'\U0001F53D')
            self.send_message(s_message, status)
        self.dict_return.set(url, status, s_message, False)

    def __web_return(self, url):
        # TODO: Pendiente añadir soporte https.
        cmd = self.path_file.find('curl')
        cmd += ' -sL -w "%{http_code}\n" http://' + url + ' -o /dev/null'
        stdout = self._run_cmd(cmd)
        if stdout.find('200') == -1:
            return False
        return True


if __name__ == '__main__':

    wf = Watchful(None)
    print(wf.check())
