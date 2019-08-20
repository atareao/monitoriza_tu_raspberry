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

from lib.switch import Switch

__all__ = ['ReturnModuleCheck']


class ReturnModuleCheck(object):

    """ Main Class. """

    def __init__(self):
        """ Inicializa Objeto. """
        self.__dict_return = {}

    @property
    def list(self) -> dict:
        if self.__dict_return:
            return self.__dict_return
        return {}

    @property
    def count(self) -> int:
        """
        Obtenemos el numero de returns que contiene el objeto.

        :return: Numero de returns.

        """
        return len(self.list)

    def items(self):
        """
        Lista de items del diccionario return.

        :return: Lista de items.

        """
        return self.list.items()

    def keys(self):
        """
        Lista de keys del diccionario return.

        :return: Lista de keys.

        """
        return self.list.keys()

    def is_exist(self, key: str) -> bool:
        """
        Comprueba si la key que le especificamos existe en la lista de returns.

        :param key: Key que buscamos.
        :return:  True si existe, False si no existe.

        """
        if key in self.list.keys():
            return True
        return False

    def set(self, key: str, status: bool = True, message='', send_msg: bool = True, other_data: dict = None) -> bool:
        """
        Crea un nuevo return y si ya existe lo actualiza.

        :param key: Key del return
        :param status: True si el Status es OK, False si el status es Error/Warning/Etc.. todo lo que no es OK.
        :param message: Mensaje que se enviara pro telegram.
        :param send_msg: True el mensaje hay que enviarlo, False el mensaje no hay que enviarlo.
        :param other_data: Diccionario con otros datos.
        :return: True se ha guardado ok, False algo ha fallado.

        """
        if key:
            if other_data is None:
                other_data = {}
            self.__dict_return[key] = {}
            self.__dict_return[key]['status'] = status
            self.__dict_return[key]['message'] = message
            self.__dict_return[key]['send'] = send_msg
            self.__dict_return[key]['other_data'] = other_data
            return self.is_exist(key)
        return False

    def update(self, key: str, option: str, value) -> bool:
        """
        Actualiza alguna de las propiedades de un return que ya existe.

        :param key: Key del return
        :param option: Nombre de la opción.
        :param value: Nuevo valor.
        :return: True si todo ha ido bien y False si algo ha fallado.

        """

        if key:
            with Switch(option, invariant_culture_ignore_case=True) as case:
                if case("status", "message", "send", "other_data"):
                    if self.is_exist(key):
                        self.__dict_return[key][option] = value
                        return True
                else:
                    # Opción no valida!!
                    pass
        return False

    def remove(self, key: str) -> bool:
        """
        Eliminamos el key que le especificamos de la lista de returns.

        :param key: Key a eliminar.
        :return: True se ha eliminado, False algo ha fallado.

        """
        if self.is_exist(key):
            del self.__dict_return[key]
            return True
        return False

    def get(self, key: str) -> dict:
        """
        Obtenemos el diccionario de la key que buscamos.

        :param key: Key que buscamos.
        :return: Diccionario con los datos de la key que buscamos y si no existe esa key retorna diccionario vacio.

        """
        if self.is_exist(key):
            return self.list[key]
        return {}

    def get_status(self, key: str) -> bool:
        """ Obtenemos el Status del key que especificamos. """
        return self.get(key).get('status', False)

    def get_message(self, key: str) -> str:
        """ Obtenemos el mensaje del key que especificamos. """
        return self.get(key).get('message', '')

    def get_send(self, key: str) -> bool:
        """ Obtenemos el Send del key que especificamos. """
        return self.get(key).get('send', True)

    def get_other_data(self, key: str) -> dict:
        """ Obtenemos other_data del key que especificamos. """
        return self.get(key).get('other_data', {})
