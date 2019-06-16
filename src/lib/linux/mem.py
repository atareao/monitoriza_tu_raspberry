#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Monitorize your Raspberry Pi
#
# Copyright © 2019  Javier Pastor (aka vsc55)
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

__all__ = ['Mem']


class Mem(object):

    class MemInfo(object):
        def __init__(self, total: int = 0, free: int = 0):
            self.total = total
            self.free = free

        @property
        def used(self) -> int:
            r_used = int(self.total) - int(self.free)
            return r_used

        @property
        def used_percent(self) -> float:
            r_per = float(self.used) / float(self.total) * 100.0
            return r_per

        @property
        def total(self) -> int:
            return self.__total

        @total.setter
        def total(self, val: int):
            self.__total = val

        @property
        def free(self) -> int:
            return self.__free

        @free.setter
        def free(self, val: int):
            self.__free = val

    def __init__(self):
        pass

    @staticmethod
    def __read_meminfo():
        with open('/proc/meminfo', 'r') as mem:
            ret = {'ram': {}, 'swap': {}}
            for i in mem:
                s_line = i.split()
                if str(s_line[0]) == 'MemTotal:':
                    ret['ram']['total'] = int(s_line[1])
                elif str(s_line[0]) == 'MemFree:':
                    ret['ram']['free'] = int(s_line[1])
                elif str(s_line[0]) == 'Buffers:':
                    ret['ram']['buffers'] = int(s_line[1])
                elif str(s_line[0]) == 'Cached:':
                    ret['ram']['cached'] = int(s_line[1])
                elif str(s_line[0]) == 'SwapTotal:':
                    ret['swap']['total'] = int(s_line[1])
                elif str(s_line[0]) == 'SwapFree:':
                    ret['swap']['free'] = int(s_line[1])
        return ret

    @property
    def ram(self) -> MemInfo:
        mem_info = self.__read_meminfo()
        r_info = self.MemInfo()
        r_info.total = int(mem_info['ram']['total'])
        r_info.free = int(mem_info['ram']['free']) + int(mem_info['ram']['buffers']) + int(mem_info['ram']['cached'])
        return r_info

    @property
    def swap(self) -> MemInfo:
        mem_info = self.__read_meminfo()
        r_info = self.MemInfo()
        r_info.total = int(mem_info['swap']['total'])
        r_info.free = int(mem_info['swap']['free'])
        return r_info


if __name__ == "__main__":
    x = Mem()
    y = x.ram
    print(y.total, y.free, y.used)

    y = x.swap
    print(y.total, y.free, y.used)

    print(Mem().ram.total, Mem().ram.free, Mem().ram.used, Mem().ram.used_percent)
    print(Mem().swap.total, Mem().swap.free, Mem().swap.used, Mem().swap.used_percent)
