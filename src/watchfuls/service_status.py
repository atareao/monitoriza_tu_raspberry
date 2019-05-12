#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
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

class Watchful():
    def __init__(self, monitor):
        self.monitor = monitor
        pass

    def check(self):
        service = importlib.import_module('__service')
        returnDict = {}
        
        for (key, value) in self.monitor.config['services'].items():
            print("Service: {0} - Enabled: {1}".format(key, value))
            if value:
                status, message = service.status(key)
                returnDict[key] = {}
                returnDict[key]['status']=status
                returnDict[key]['message']=message
        
        return True, returnDict

if __name__ == '__main__':
    wf = Watchful()
    print(wf.check())
