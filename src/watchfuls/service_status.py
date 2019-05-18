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
import lib.tools
import globales
from lib.debug import *
from lib.monitor import *
from lib.module_base import *

class Watchful(ModuleBase):

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def check(self):
        listservice = []
        for (key, value) in self.read_conf('list').items():
            globales.GlobDebug.print("Service: {0} - Enabled: {1}".format(key, value), DebugLevel.info)
            if value:
                listservice.append(key)

        returnDict = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.read_conf('threads',5)) as executor:
            future_to_service = {executor.submit(self.__service_check, service): service for service in listservice}
            for future in concurrent.futures.as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    returnDict[service]=future.result()
                except Exception as exc:
                    returnDict[service]={}
                    returnDict[service]['status']=False
                    returnDict[service]['message']='Service: {0} - Error: {1}'.format(service, exc)
        
        msg_debug = '*'*60 + '\n'
        msg_debug = msg_debug + "Debug [{0}] - Data Return:\n".format(self.NameModule)
        msg_debug = msg_debug + "Type: {0}\n".format(type(returnDict))
        msg_debug = msg_debug + str(returnDict) + '\n'
        msg_debug = msg_debug + '*'*60 + '\n'
        globales.GlobDebug.print(msg_debug, DebugLevel.debug)
        return True, returnDict

    def __service_check(self, service):
        status, message = self.__service_return(service)
        rCheck = {}
        rCheck['status']=status
        rCheck['message']=''
        if self.chcek_status(status, self.NameModule, service):
            if status:
                self.send_message('Service: {0} - Status: '.format(service) + u'\U00002705')
            else:
                self.send_message('Service: {0} - *Error: {1}* '.format(service, message) + u'\U0000274E')
        return rCheck

    def __service_return(self, service):
        stdout, stderr = lib.tools.execute('systemctl status '+service)
        if stdout == '':
            return False, stderr[:-1]
        return True, ''


if __name__ == '__main__':
    wf = Watchful()
    print(wf.check())
