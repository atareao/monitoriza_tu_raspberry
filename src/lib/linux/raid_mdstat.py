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
from lib.exe import Exec
from lib import DictFilesPath

__all__ = ['RaidMdstat']


class RaidMdstat(object):

    class UpdateStatus(Enum):
        unknown = 0
        ok = 1
        error = 2
        recovery = 3

    def __init__(self, mdstat=None, host=None, port=22, user=None, password=None, timeout=None):
        self.paths = DictFilesPath()
        self.paths.set('mdstat', '/proc/mdstat')
        if mdstat is not None:
            self.paths.set('mdstat', mdstat)
        self.__host = host
        self.__port = port
        self.__user = user
        self.__pass = password
        self.__timeout = timeout

    @property
    def is_remote(self) -> bool:
        if self.__host:
            return True
        return False

    @property
    def validate_remote(self) -> bool:
        if self.is_remote:
            if str(self.__host).strip() and int(self.__port) > 0 and str(self.__user).strip():
                return True
        return False

    @property
    def is_exist(self) -> bool:
        path_md_stat = self.paths.find('mdstat')
        if self.is_remote:
            if self.validate_remote:
                str_check = "exists"
                remote_cmd = "test -e {0} && echo {1}".format(path_md_stat, str_check)
                stdout, stderr, _, stdexcept = Exec.execute(remote_cmd,
                                                            self.__host,
                                                            self.__port,
                                                            self.__user,
                                                            self.__pass,
                                                            self.__timeout)

                str_err = "** RAID_Mdstat ** >> {0}!! >> REMOTE >> Failed to check existence of {1}: {2}!"
                if stderr:
                    print(str_err.format("ERROR", path_md_stat, stderr))
                    return False

                if stdexcept:
                    print(str_err.format("EXCEPTION", path_md_stat, stdexcept))
                    raise Exception(stdexcept)

                return True if stdout.strip() == str_check else False

            else:
                print(
                    "** RAID_Mdstat ** >> WARNING!! >> REMOTE >> CONFIG NOT VALID ({0}:{1}@{1}) NOT VALID!".format(
                        self.__host, self.__pass, self.__user))
                return False

        else:
            if os.path.isdir(path_md_stat):
                return False
            else:
                return os.path.exists(path_md_stat)

    def read_status(self):
        md_list = {}
        md_actual = None

        try:
            is_exist = self.is_exist
        except Exception as ex:
            raise Exception(ex)

        if is_exist:
            f_buffer = None
            if self.is_remote:
                remote_cmd = "cat {0}".format(self.paths.find('mdstat'))
                stdout, stderr, _, stdexcept = Exec.execute(remote_cmd,
                                                            self.__host,
                                                            self.__port,
                                                            self.__user,
                                                            self.__pass,
                                                            self.__timeout)

                str_err = "** RAID_Mdstat ** >> {0}!! >> REMOTE >> ({1}): {2}!"
                if stderr:
                    raise Exception(str_err.format("ERROR", remote_cmd, stderr))

                if stdexcept:
                    raise Exception(str_err.format("EXCEPTION", remote_cmd, stdexcept))

                f_buffer = stdout.splitlines()
            else:
                f_buffer = open(self.paths.find('mdstat'), 'r')

            if f_buffer:
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

        return md_list
