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

    def __init__(self, monitor):
        self.monitor = monitor
        pass

    def check(self):
        listhost = []
        for (key, value) in self.monitor.config['ping'].items():
            print("Ping: {0} - Enabled: {1}".format(key, value))
            if value:
                listhost.append(key)

        returnDict = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_ping = {executor.submit(self.ping_check, host): host for host in listhost}
            for future in concurrent.futures.as_completed(future_to_ping):
                host = future_to_ping[future]
                try:
                    returnDict[host]=future.result()
                except Exception as exc:
                    returnDict[host]={}
                    returnDict[host]['status']=False
                    returnDict[host]['message']='Ping: {0} - Error: {1}'.format(host, exc)

        #pprint.pprint(returnDict)
        return True, returnDict

    
    def ping_check(self, host):
        rCheck = {}
        rCheck['status']=self.ping_return(host, 5)
        rCheck['message']=''
        if self.monitor.chcek_status(rCheck['status'], 'ping', host):
            self.send_message('Ping: {0} {1}'.format(host, 'UP' if rCheck['status'] else 'DOWN' ))
        return rCheck

    def ping_return(self, host, timeout):
        utils = importlib.import_module('__utils')
        rCode = utils.execute_call('ping -c 1 -W {0} {1}'.format(timeout, host))
        if rCode == 0:
           return True
        return False
   
    def send_message(self, message):
        if message:
            self.monitor.tg_send_message(message)
        

if __name__ == '__main__':
    wf = Watchful()
    print(wf.check())
