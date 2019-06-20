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

import sys
import os
from multiprocessing.dummy import Pool as ThreadPool

sys.path.append("..")
sys.path.append(os.path.join('..', 'lib'))

from lib.config import ConfigControl
from lib.config import ConfigTypeReturn


aa = ConfigControl("modules.json")
aa.read()


print("TEST GET CONFIG")
print('-'*60)
print('-'*60)

bb = aa.get_conf(["ping", "list"], "No Encontrado en Lista")
print("List Resultado:", bb)
print('-'*60)

# bb = aa.get_conf({"ram":1, "alert":1}, "No Encontrado en Dict")
# print("Dict Resultado:", bb)
# print('-'*60)

bb = aa.get_conf(("filesystemusage", "list"), "No Encontrado en Tuple")
print("Tuple Resultado:", bb)
print('-'*60)

bb = aa.get_conf(("filesystemusage", "list", "123"), "No Encontrado en Tuple")
print("Tuple Resultado:", bb)
print('-'*60)

bb = aa.get_conf("service_status", "No Encontrado en String")
print("String Resultado:", bb)
print('-'*60)

bb = aa.get_conf('PruebaEstoNoExisteEnLosDatos', r_type=ConfigTypeReturn.LIST)
print("Resultado No Existe y se r_type list:", bb)
print('-'*60)

print('-'*60)
print('-'*60)
print("")
print("")


print("TEST IS EXIST CONFIG")
print('-'*60)
print('-'*60)

bb = aa.is_exist_conf(["ping", "list"])
print("Exist List Resultado:", bb)
print('-'*60)

bb = aa.is_exist_conf(("filesystemusage", "list"))
print("Exist Tuple Resultado:", bb)
print('-'*60)

bb = aa.is_exist_conf(("filesystemusage", "list", "123"))
print("NoExist Tuple Resultado:", bb)
print('-'*60)

bb = aa.is_exist_conf("service_status")
print("Exist String Resultado:", bb)
print('-'*60)

bb = aa.is_exist_conf("123:456", ":",  {'123': {'456': '1.1'}, '456': 2})
print("Exist String stplit Resultado:", bb)
print('-'*60)


# bb = aa.isExist_Conf({"ram":1, "alert":1})
# print("Exist Dict Resultado:", bb)
# print('-'*60)

print('-'*60)
print('-'*60)
print('-'*60)
print("")
print("")


print("TEST SET CONFIG")
print('-'*60)
print('-'*60)

print("MODO MONO HILO")
print('-'*60)
print("")
aa = ConfigControl(None)
print("Datos Init:", aa.data)

aa.set_conf("123", "ok")
aa.set_conf("456", {"1": "OK"})

print("Datos 1:", aa.data)
print('-'*60)

aa.set_conf(["456", "1", "2"], "ok")
aa.data.update({"123": "OK1"})
print("Datos 2:", aa.data)
print('-'*60)
print("")

print("MODO MULTI HILO")
print('-'*60)
print("")
aa = ConfigControl(None)
print("Datos Init:", aa.data)


ltmp_num_loop = 4
ltmp_num_range = 200

print("Loop:", ltmp_num_loop)
print("Nº Reg en cada Loop:", ltmp_num_range)
print('*'*20)
print("")

ltmp = []
for y in range(ltmp_num_loop):
    if y == 0 or y%2 == 0:
        for x in range(ltmp_num_range):
            ltmp.append(x)
    else:
        for x in reversed(range(ltmp_num_range)):
            ltmp.append(x)

    for x in range(ltmp_num_range):
        ltmp.append(999)


def set_cfg(num):
    # print(num)
    findkey = [str(num)]
    ltmp_c = 0

    msg = ''
    if aa.is_exist_conf(findkey):
        msg = '{0} SIExisteA: {1}\n'.format(msg, num)

        ltmp_c = aa.get_conf(findkey, 0)
        msg = '{0} Read({1}): {2}\n'.format(msg, num, ltmp_c)
        if ltmp_c:
            msg = '{0} SIExisteB: {1}\n'.format(msg, num)
        else:
            msg = '{0} NOExisteB: {1}\n'.format(msg, num)
    else:
        msg = '{0} NOExisteA: {1}\n'.format(msg, num)
    
    ltmp_b = ltmp_c + 1
    aa.set_conf(findkey, ltmp_b)

    ltmp_c = aa.get_conf(findkey, 0)
    msg = '{0} Read Despues ({1}): {2}\n'.format(msg, num, ltmp_c)

    msg += '-'*20
    # print(msg)


pool = ThreadPool(200)
lReturn = pool.map(set_cfg, ltmp)
pool.close()
pool.join()


print("Len:", len(aa.data), " - datos:", aa.data)
print('*'*90)
print('LIST (NO TIENE QUE APARECER NADA EN ESTA LISTA):')
for key, val in aa.data.items():
    if val != ltmp_num_loop and (key == 999 and val != ltmp_num_loop*ltmp_num_range):
        print("key:", key, " - Val:", val)
print('-'*60)
