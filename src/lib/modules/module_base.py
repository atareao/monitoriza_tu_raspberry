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

import lib.tools
from lib import Switch
from lib import ObjectBase
from lib import DictFilesPath
from lib.debug import DebugLevel
from lib.config import ConfigTypeReturn
from lib.modules import ReturnModuleCheck
from enum import Enum

__all__ = ['ModuleBase']


class ModuleBase(ObjectBase):

    # Nº de hilos que se usaran en los módulos para procesamiento en paralelo como valor por defecto.
    _default_threads = 5

    def __init__(self, obj_monitor, name=None):
        self._monitor = obj_monitor
        if name:
            self.__name_module = name
        else:
            self.__name_module = __name__

        # Set var's
        self.path_file = None
        self.dict_return = None

        # Init Var's
        self.__init_var()

    def __init_var(self):
        self.path_file = DictFilesPath()
        self.dict_return = ReturnModuleCheck()

    def check(self):
        self.debug.debug_obj(self.name_module, self.dict_return.list, "Data Return")

    @property
    def name_module(self) -> str:
        """ Nombre del modulo. """
        return self.__name_module

    @property
    def is_monitor_exist(self) -> bool:
        """
        Nos dice si el objeto Monitor esta creado o no.

        :return: True esta creado, False es None o no es tipo Monitor.

        """
        if self._monitor and isinstance(self._monitor, lib.Monitor):
            return True
        return False

    @property
    def _monitor(self):
        """ Leemos el objeto Monitor. """
        return self.__monitor

    @_monitor.setter
    def _monitor(self, val):
        """ Definimos el objeto Monitor. """
        if isinstance(val, lib.Monitor):
            self.__monitor = val
        else:
            raise ValueError('Type not valid, only Monitor valid type.')

    def send_message(self, message, status=None):
        """
        Funciona puente con la función send_message del objeto Monitor, efectuando comprobación de si se ha definido
        Monitor antes de enviar los datos.
        """
        if self.is_monitor_exist:
            self._monitor.send_message(message, status)
        else:
            self.debug.print(">> {0} > send_message: Error, Monitor is not defined!!".format(self.name_module),
                             DebugLevel.error)

    def get_conf(self, find_key=None, default_val=None, select_module: str = None, str_split: str = None,
                 r_type: ConfigTypeReturn = ConfigTypeReturn.STR):
        """
        Función puente con la función get_conf del objeto Monitor efectuando un comprobación de si el objeto Monitor se
        ha definido antes de solicitar los datos.

        :param find_key: Key de configuración que buscamos.
        :param default_val: Valor por defecto que retornara si la configuración no existe o es incorrecta.
        :param select_module: Nombre del modulo en el que vamos a buscar el parámetro find_key. Si no se define ninguno
                              buscaremos en la configuración del modulo actual.
        :param str_split: Carácter que se usara para separar find_key si se pasa en modo String.
        :param r_type: Tipo de return.
        :return:
        """
        if default_val is None:
            default_val = {}

        if self.is_monitor_exist:
            if not select_module:
                select_module = self.name_module

            if select_module:
                if find_key is None:
                    return self._monitor.config_modules.get_conf(select_module, default_val)
                else:
                    keys_list = self._monitor.config_modules.convert_find_key_to_list(find_key, str_split)
                    keys_list.insert(0, select_module)
                    return self._monitor.config_modules.get_conf(keys_list, default_val, str_split=str_split,
                                                                 r_type=r_type)

        if find_key or default_val:
            return default_val
        return []

    def get_conf_in_list(self, opt_find: str, key_name_module: str, def_val=None):
        """
        Obtenemos los datos que deseamos buscar de la sección 'list' de la configuración del modulo.

        :param opt_find: Opción a buscar.
        :param key_name_module: Nombre del modulo del que deseamos obtener la sección 'list'.
        :param def_val: Valor por defecto si no existe la opción que buscamos.
        :return: Valor obtenido de la configuración.

        """
        with Switch(opt_find, check_isinstance=True) as case:
            if case(Enum):
                find_key = [opt_find.name]
            elif case(str):
                find_key = [opt_find]
            elif case(list):
                find_key = opt_find.copy()
            elif case(int, float):
                find_key = [str(opt_find)]
            elif case(tuple):
                find_key = list(opt_find)
            else:
                raise TypeError("opt_find is not valid type ({0})!".format(type(opt_find)))

        if key_name_module:
            find_key.insert(0, key_name_module)
            find_key.insert(0, "list")
        value = self.get_conf(find_key, def_val)
        return value

    def check_status(self, status, module, module_sub_key):
        """ Comprobamos el status del modulo y sub modulo. """
        if self.is_monitor_exist:
            return self._monitor.check_status(status, module, module_sub_key)

    @staticmethod
    def _run_cmd(cmd, return_str_err: bool = False):
        """
        Ejecutamos el programa que le pasamos y leemos lo que retorna.

        :param cmd: Comando a ejecutar.
        :param return_str_err: True retornamos stdout y stderr, False retornamos solo stdout.
        :return: Retornamos el resultado de la ejecución del comando que hemos pasado.

        """
        stdout, stderr = lib.tools.execute(cmd)
        if return_str_err:
            return stdout, stderr
        return stdout

    @staticmethod
    def _run_cmd_call(cmd):
        """
        Ejecutamos el comando y obtenemos el código de retorno del programa.
        :param cmd: Comando a ejecutar.
        :return: Código que retorna el programa al finalizar.
        """
        return_code = lib.tools.execute_call(cmd)
        return return_code
