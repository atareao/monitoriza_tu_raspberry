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

import importlib
import concurrent.futures
import pprint

class Watchful():
    def __init__(self, monitor):
        self.monitor = monitor
        pass

    def check(self):
        listurl = []
        for (key, value) in self.monitor.config['web'].items():
            print("Web: {0} - Enabled: {1}".format(key, value))
            if value:
                listurl.append(key)

        returnDict = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self.web_check, url): url for url in listurl}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    returnDict[url]=future.result()
                except Exception as exc:
                    returnDict[url]={}
                    returnDict[url]['status']=False
                    returnDict[url]['message']='Web: {0} - Error: {1}'.format(url, exc)
        
        #pprint.pprint(returnDict)
        return True, returnDict

    def web_check(self, url):
        rCheck = {}
        rCheck['status']=self.web_return(url)
        rCheck['message']=''
        if self.monitor.chcek_status(rCheck['status'], 'web', url):
            self.send_message('Web: {0} - Status: {1}'.format(url, 'UP' if rCheck['status'] else 'DOWN' ))
        return rCheck

    def web_return(self, url):
        utils = importlib.import_module('__utils')
        cmd = 'curl -sL -w "%{http_code}\n" http://'+url+' -o /dev/null'
        stdout, stderr = utils.execute(cmd)
        if stdout.find('200') == -1:
           return False
        return True

    def send_message(self, message):
        if message:
            self.monitor.tg_send_message(message)
        
if __name__ == '__main__':
    wf = Watchful()
    print(wf.check())
