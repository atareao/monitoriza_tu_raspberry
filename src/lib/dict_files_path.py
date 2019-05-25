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

__all__ = ['DictFilesPath']


class DictFilesPath(object):

    __files = None

    def __init__(self):
        self.__files = {}

    def is_exist(self, file_find):
        if file_find and file_find in self.files.keys():
            return True
        return False

    def find(self, file_find, return_is_not_exist=''):
        if self.is_exist(file_find):
            return self.files[file_find]
        return return_is_not_exist

    @property
    def files(self):
        if self.__files is None:
            return {}
        return self.__files

    def set(self, file_name, file_path):
        if file_name:
            self.__files[file_name] = file_path
            return self.is_exist(file_name)
        return False

    def remove(self, file_find):
        if self.is_exist(file_find):
            del self.__files[file_find]
            return True
        return False


if __name__ == "__main__":

    t = DictFilesPath()
    t.set("File1", "Path1")
    print("1:", t.files)
    print("")

    t.set("File1", "Path1.1")
    print("2:", t.files)
    print("")

    t.set("File2", "Path2")
    print("3:", t.files)
    print("")

    t.remove("File2")
    print("4:", t.files)
    print("")
    print("")

    x = t.find("File1", "Path1Default")
    print("Find1:", x)
    x = t.find("File11", "Path11Default")
    print("Find2:", x)
