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

import importlib
import concurrent.futures
import pprint

class Watchful():
    debugMode = False

    def __init__(self, monitor):
        self.monitor = monitor
        pass

    def debug(self, message):
        if self.debugMode:
            if isinstance(message, str):
                print(message)
            else:
                pprint.pprint(message)

    def check(self):
        listservice = []
        for (key, value) in self.monitor.config['service_status'].items():
            self.debug("Service: {0} - Enabled: {1}".format(key, value))
            if value:
                listservice.append(key)

        returnDict = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_service = {executor.submit(self.service_check, service): service for service in listservice}
            for future in concurrent.futures.as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    returnDict[service]=future.result()
                except Exception as exc:
                    returnDict[service]={}
                    returnDict[service]['status']=False
                    returnDict[service]['message']='Service: {0} - Error: {1}'.format(service, exc)
        
        self.debug(type(returnDict))
        self.debug(returnDict)
        return True, returnDict

    def service_check(self, service):
        status, message = self.service_return(service)
        rCheck = {}
        rCheck['status']=status
        rCheck['message']=''
        if self.monitor.chcek_status(status, 'service_status', service):
            if status:
                self.send_message('Service: {0} - Status: Ok'.format(service))
            else:
                self.send_message('Service: {0} - **Error: {1}'.format(service, message))
        return rCheck

    def service_return(self, service):
        utils = importlib.import_module('__utils')
        stdout, stderr = utils.execute('systemctl status '+service)
        if stdout == '':
            return False, stderr[:-1]
        return True, ''

    def send_message(self, message):
        if message:
            self.monitor.tg_send_message(message)

if __name__ == '__main__':
    wf = Watchful()
    print(wf.check())
