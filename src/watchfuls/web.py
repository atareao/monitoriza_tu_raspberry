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
import lib.tools
import globales
import lib.debug
import lib.module_base
import lib.monitor

class Watchful(lib.module_base.ModuleBase):

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def check(self):
        listurl = []
        for (key, value) in self.get_conf('list', {}).items():
            globales.GlobDebug.print("Web: {0} - Enabled: {1}".format(key, value), lib.debug.DebugLevel.info)
            if value:
                listurl.append(key)

        returnDict = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.get_conf('threads', self._default_threads)) as executor:
            future_to_url = {executor.submit(self.__web_check, url): url for url in listurl}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    returnDict[url]=future.result()
                except Exception as exc:
                    returnDict[url]={}
                    returnDict[url]['status']=False
                    returnDict[url]['message']='Web: {0} - Error: {1}'.format(url, exc)
        
        msg_debug = '*'*60 + '\n'
        msg_debug = msg_debug + "Debug [{0}] - Data Return:\n".format(self.NameModule)
        msg_debug = msg_debug + "Type: {0}\n".format(type(returnDict))
        msg_debug = msg_debug + str(returnDict) + '\n'
        msg_debug = msg_debug + '*'*60 + '\n'
        globales.GlobDebug.print(msg_debug, lib.debug.DebugLevel.debug)
        return True, returnDict

    def __web_check(self, url):
        status=self.__web_return(url)

        rCheck = {}
        rCheck['status']=status
        rCheck['message']=''
        if self.chcek_status(status, self.NameModule, url):
            sMessage='Web: {0}'.format(url)
            if status:
                sMessage='{0} {1}'.format(sMessage, u'\U0001F53C')
            else:
                sMessage='{0} {1}'.format(sMessage, u'\U0001F53D')
            self.send_message(sMessage, status)
        return rCheck

    @classmethod
    def __web_return(self, url):
        #TODO: Pendiente añadir soporte https.
        cmd = 'curl -sL -w "%{http_code}\n" http://'+url+' -o /dev/null'
        stdout, stderr =  lib.tools.execute(cmd)
        if stdout.find('200') == -1:
           return False
        return True

if __name__ == '__main__':
    wf = Watchful(None)
    print(wf.check())
