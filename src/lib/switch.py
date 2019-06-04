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

""" The switch statement is similar to a series of IF statements on the same expression. In many occasions, you may
want to compare the same variable (or expression) with many different values, and execute a different piece of code
depending on which value it equals to. This is exactly what the switch statement is for.

Example 1:
    with Switch(5) as case:
        if case(0):
            print("Is 0.")
        elif case(1, 2):
            print("Is 1 or 2.")
        elif case(3, 4):
            print("Is 3 or 4.")
        else:
            print("Is other number.")

    Return >> "Is other number."


Example 2:
    with Switch("Test", invariant_culture_ignore_case=True) as case:
        if case("Test0"):
            print("Is Test0.")
        elif case("Test1", "Test2"):
            print("Is Test1 or Test2.")
        elif case("TEST"):
            print("Is TEST.")
        else:
            print("Is other Value.")

    Return: >> Is TEST.


Example 3:
    value_test = ["Test1", "Test2"]
    with Switch(value_test, check_isinstance=True) as case:
        if case(str):
            print("Is String.")
        elif case(int, float):
            print("Is Int or Float.")
        elif case(list):
            print("Is List.")
        else:
            print("Is other type.")

    Return: >> Is List..

"""

__author__ = "Javier Pastor, Ian Bell"
__copyright__ = "Copyright © 2019, Javier Pastor"
__credits__ = "Javier Pastor"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = 'Javier Pastor'
__email__ = "python@cerebelum.net"
__status__ = "Development"

__all__ = ['Switch']


class Switch:

    """ Main Class. """

    def __init__(self, value, invariant_culture_ignore_case=False, check_isinstance=False):
        """ The switch is initialized and configured as it will act.

        :param value: Value against which comparisons will be made.
        :param invariant_culture_ignore_case: If it is set to True and the type of value to be compared is a String,
        the difference between uppercase and lowercase will be ignored when doing the verification.
        :param check_isinstance: If set to True, the check will not be content value but the type of object it is.

        """
        self.value = value
        self.invariant_culture_ignore_case = invariant_culture_ignore_case
        self.check_isinstance = check_isinstance

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        # Allows a traceback to occur
        return False

    def __call__(self, *values):
        """ Check if any of the values passed to you match the value that was defined when the object was created.

        :param values: List of values that are compared to the value specified when creating the switch.
        :return: True if any of the values that have been passed match, False if none matches.

        """
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
