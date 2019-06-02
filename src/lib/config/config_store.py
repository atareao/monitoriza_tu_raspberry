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

import codecs
import json
import os
from lib import ObjectBase
from lib.debug import DebugLevel


__all__ = ['ConfigStore']


class ConfigStore(ObjectBase):

    def __init__(self, file):
        self.file = file

    @property
    def is_exist_file(self):
        if self.file:
            if os.path.isfile(self.file):
                return True
        return False

    @property
    def file(self):
        return self.__file

    @file.setter
    def file(self, val):
        self.__file = val

    def read(self, def_return=None):
        return_date = def_return
        if self.is_exist_file:
            try:
                f = codecs.open(self.file, 'r', 'utf-8')
                return_date = json.loads(f.read())
                f.close()
            except Exception as e:
                self.debug.exception(e)
        else:
            self.debug.print("Config >> Warning: File ({0}) not exist!!!".format(self.file),  DebugLevel.warning)
        return return_date

    def save(self, data) -> bool:
        try:
            f = codecs.open(self.file, 'w', 'utf-8')
            f.write(json.dumps(data))
            f.close()
        except Exception as e:
            self.debug.exception(e)
            return False
        return True
