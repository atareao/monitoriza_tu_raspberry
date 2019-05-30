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

__all__ = ['ReturnModuleCheck']


class ReturnModuleCheck(object):

    __dict_return = None

    def __init__(self):
        self.__dict_return = {}

    @property
    def list(self) -> dict:
        if self.__dict_return:
            return self.__dict_return
        return {}

    @property
    def count(self) -> int:
        return len(self.list)

    def items(self):
        return self.list.items()

    def keys(self):
        return self.list.keys()

    def is_exist(self, key: str) -> bool:
        if key in self.list.keys():
            return True
        return False

    def set(self, key: str, status: bool = True, message='', send_msg: bool = True, other_data: dict = {}) -> bool:
        if key:
            self.__dict_return[key] = {}
            self.__dict_return[key]['status'] = status
            self.__dict_return[key]['message'] = message
            self.__dict_return[key]['send'] = send_msg
            self.__dict_return[key]['other_data'] = other_data
            return self.is_exist(key)
        return False

    def remove(self, key: str) -> bool:
        if self.is_exist(key):
            del self.__dict_return[key]
            return True
        return False

    def get(self, key: str) -> dict:
        if self.is_exist(key):
            return self.list[key]
        return {}

    def get_status(self, key: str) -> bool:
        if self.is_exist(key):
            return self.list[key]['status']
        return False

    def get_message(self, key: str) -> str:
        if self.is_exist(key):
            return self.list[key]['message']
        return ''

    def get_send(self, key: str) -> bool:
        if self.is_exist(key):
            return self.list[key]['send']
        return True

    def get_other_data(self, key: str) -> dict:
        if self.is_exist(key):
            return self.list[key]['other_data']
        return True
