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

import lib.tools
import time
from multiprocessing.dummy import Pool as ThreadPool
import globales
from lib.debug import *
from lib.monitor import *
from lib.module_base import *

class Watchful(ModuleBase):

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def check(self):
        lHost=[]
        for (key, value) in self.read_conf('list').items():
            globales.GlobDebug.print("Ping: {0} - Enabled: {1}".format(key, value), DebugLevel.info)
            if value:
                lHost.append(key)

        lReturn=[]
        pool = ThreadPool(self.read_conf('threads',5))
        lReturn = pool.map(self.__ping_check, lHost)
        pool.close()
        pool.join()


        msg_debug = '*'*60 + '\n'
        msg_debug = msg_debug + "Debug [{0}] - Data Work:\n".format(self.NameModule)
        msg_debug = msg_debug + "Type: {0}\n".format(type(lReturn))
        msg_debug = msg_debug + str(lReturn) + '\n'
        msg_debug = msg_debug + '*'*60 + '\n'
        globales.GlobDebug.print(msg_debug, DebugLevel.debug)
        

        #Convertir list en dictionary
        dReturn = {}
        for valueL1 in lReturn:
            dReturn = {**dReturn, **valueL1}

        
        msg_debug = '*'*60 + '\n'
        msg_debug = msg_debug + "Debug [{0}] - Data Return:\n".format(self.NameModule)
        msg_debug = msg_debug + "Type: {0}\n".format(type(dReturn))
        msg_debug = msg_debug + str(dReturn) + '\n'
        msg_debug = msg_debug + '*'*60 + '\n'
        globales.GlobDebug.print(msg_debug, DebugLevel.debug)
        return True, dReturn
    
    def __ping_check(self, host):
        status_return=self.__ping_return(host, 5)

        rCheck = {}
        rCheck[host] = {}
        rCheck[host]['status']=status_return
        rCheck[host]['message']=''
        if self.chcek_status(status_return, self.NameModule, host):
            self.send_message('Ping: {0} {1}'.format(host, 'UP ' + u'\U0001F53C' if status_return else 'DOWN ' + u'\U0001F53D'))
        return rCheck

    def __ping_return(self, host, timeout):
        counter = 0
        while counter < 3:
            rCode = lib.tools.execute_call('ping -c 1 -W {0} {1}'.format(timeout, host))
            if rCode == 0:
                return True
            time.sleep(1)
            counter += 1
        return False

if __name__ == '__main__':
    wf = Watchful()
    print(wf.check())
