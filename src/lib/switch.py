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

# Fuente:
# https://stackoverflow.com/questions/60208/replacements-for-switch-statement-in-python

__all__ = ['Switch']


class Switch:
    def __init__(self, value, invariant_culture_ignore_case=False, check_isinstance=False):
        self.value = value
        self.invariant_culture_ignore_case = invariant_culture_ignore_case
        self.check_isinstance = check_isinstance

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        # Allows a traceback to occur
        return False

    def __call__(self, *values):
        if self.check_isinstance:
            # Efectúa check isinstance
            for item in values:
                if isinstance(self.value, item):
                    return True
            return False

        elif self.invariant_culture_ignore_case and isinstance(self.value, str):
            # Comparativa ignorando Mayúsculas y Minúsculas.
            for item in values:
                if isinstance(item, str) and (self.value.lower() == item.lower()):
                    return True

        return self.value in values
