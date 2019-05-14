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
from lib.module_base import ModuleBase

class Watchful(ModuleBase):
    
    def __init__(self, monitor, debug = False):
        ModuleBase.__init__(self,__name__, monitor, debug)
        
    def check(self):
        listurl = []
        for (key, value) in self.monitor.config[self.NameModule].items():
            self.debug("Web: {0} - Enabled: {1}".format(key, value))
            if value:
                listurl.append(key)

        returnDict = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self.__web_check, url): url for url in listurl}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    returnDict[url]=future.result()
                except Exception as exc:
                    returnDict[url]={}
                    returnDict[url]['status']=False
                    returnDict[url]['message']='Web: {0} - Error: {1}'.format(url, exc)
        
        
        self.debug(type(returnDict))
        self.debug(returnDict)
        return True, returnDict

    def __web_check(self, url):
        rCheck = {}
        rCheck['status']=self.__web_return(url)
        rCheck['message']=''
        if self.monitor.chcek_status(rCheck['status'], self.NameModule, url):
            self.send_message('Web: {0} - Status: {1}'.format(url, 'UP ' + u'\U0001F53C' if rCheck['status'] else 'DOWN ' + u'\U0001F53D' ))
        return rCheck

    def __web_return(self, url):
        cmd = 'curl -sL -w "%{http_code}\n" http://'+url+' -o /dev/null'
        
        stdout, stderr =  lib.tools.execute(cmd)
        if stdout.find('200') == -1:
           return False
        return True
        
if __name__ == '__main__':
    wf = Watchful()
    print(wf.check())
