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

import os
import shlex
import subprocess

def execute(command, parser=None):
    command_with_args = shlex.split(command)
    execution = subprocess.Popen(command_with_args, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    stdout, stderr = execution.communicate()
    return stdout.decode(), stderr.decode()

def execute_call(command, parser=None):
    command_with_args = shlex.split(command)
    return_code = subprocess.call(command_with_args, stdout=open(os.devnull, 'w'),
                                 stderr=open(os.devnull, 'w'))
    return return_code
