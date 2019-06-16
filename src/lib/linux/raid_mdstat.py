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

import os.path
from enum import Enum

__all__ = ['RaidMdstat']


class RaidMdstat(object):

    __default_path_mdstat = "/proc/mdstat"

    class UpdateStatus(Enum):
        unknown = 0
        ok = 1
        error = 2
        recovery = 3

    def __init__(self, mdstat = None):
        if mdstat is None:
            self.__path_mdstat = self.__default_path_mdstat
        else:
            self.__path_mdstat = mdstat

    @property
    def is_exist(self) -> bool:
        return os.path.exists(self.__path_mdstat)

    def read_status(self):

        md_list = {}
        md_actual = None

        if self.is_exist:
            with open(self.__path_mdstat, 'r') as f_buffer:
                for l_buffer in f_buffer:
                    l_buffer = str(l_buffer).strip()

                    if "Personalities :" in l_buffer:
                        # Personalities : [linear] [raid0] [raid1] [raid10] [raid6] [raid5] [raid4] [multipath] [faulty]
                        md_actual = None
                        continue

                    elif "unused devices:" in l_buffer:
                        # unused devices: <none>
                        md_actual = None
                        continue

                    elif l_buffer:
                        if md_actual is None and len(l_buffer) > 2 and l_buffer[:2] == "md":
                            #  md126 : active raid1 sdc1[2] sdb1[1]

                            md_actual = l_buffer.split(":")[0].strip()
                            tmp_split = l_buffer.split(":")[1].strip().split(" ")

                            md_list[md_actual] = {}
                            md_list[md_actual]['status'] = tmp_split.pop(0)
                            md_list[md_actual]['type'] = tmp_split.pop(0)
                            md_list[md_actual]['disk'] = tmp_split
                            continue

                        elif "recovery" in l_buffer:
                            # [===>.........]  recovery = 16.3% (39978944/244139648) finish=22.6min speed=149952K/sec

                            md_list[md_actual]['update'] = self.UpdateStatus.recovery
                            tmp_split = l_buffer.split("]")[1].strip().split(" ")
                            md_list[md_actual]['recovery'] = {}
                            md_list[md_actual]['recovery']['percent'] = float(tmp_split[2][:-1])
                            md_list[md_actual]['recovery']['blocks'] = tmp_split[3][1:-1].split("/")
                            md_list[md_actual]['recovery']['finish'] = tmp_split[4].split("=")[1].strip()
                            md_list[md_actual]['recovery']['speed'] = tmp_split[5].split("=")[1].strip()
                            continue

                        elif "blocks" in l_buffer:
                            # 244139648 blocks [2/1] [_U]

                            tmp_split = l_buffer.split(" ")
                            md_list[md_actual]['blocks'] = tmp_split[0]
                            tmp_disks = tmp_split[2][1:-1].split("/")
                            md_list[md_actual]['update'] = self.UpdateStatus.ok if tmp_disks[0] == tmp_disks[1] \
                                else self.UpdateStatus.error
                            continue

                        else:
                            print("** RAID_Mdstat ** >> WARNING!! >> {0} >> NOT CONTROL TEXT: {1}".format(md_actual,
                                                                                                          l_buffer))
                            continue

                    else:
                        md_actual = None
                        continue

            md_actual = None

        return md_list
