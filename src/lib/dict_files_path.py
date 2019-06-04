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


"""
Almacenamos una lista de nombre de archivos con su path correspondiente.

Ejemplo:
    >>> t = DictFilesPath()
    >>> t.set("test.tmp", "/tmp/test.tmp")
    True
    >>> print(t.files)
    {'test.tmp': '/tmp/test.tmp'}
    >>> t.set("test.tmp", "/tmp/test_dir/test.tmp")
    True
    >>> print(t.files)
    {'test.tmp': '/tmp/test_dir/test.tmp'}
    >>> t.set("test2.tmp", "/tmp/test2.tmp")
    True
    >>> print(t.files)
    {'test.tmp': '/tmp/test_dir/test.tmp', 'test2.tmp': '/tmp/test2.tmp'}
    >>> t.remove("test2.tmp")
    True
    >>> print(t.files)
    {'test.tmp': '/tmp/test_dir/test.tmp'}
    >>> print(t.find("test.tmp", "/dev/null"))
    /tmp/test_dir/test.tmp
    >>> print(t.find("test00.tmp", "/dev/null"))
    /dev/null

"""

__author__ = "Javier Pastor"
__copyright__ = "Copyright © 2019, Javier Pastor"
__credits__ = "Javier Pastor"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = 'Javier Pastor'
__email__ = "python@cerebelum.net"
__status__ = "Development"

__all__ = ['DictFilesPath']


class DictFilesPath(object):

    """ Main Class. """

    def __init__(self):
        """ Inicializa el objeto. """
        self.__files = None
        self.clear()

    def clear(self):
        """
        Vacia la lista.

        :return: None

        """
        self.__files = {}

    def is_exist(self, file_find: str) -> bool:
        """
        Comprueba si el archivo que le especificamos esta en la lista o no.

        :param file_find: Nombre del archivo que buscamos.
        :return: True si existe, False no existe.

        """
        if file_find and file_find in self.files.keys():
            return True
        return False

    def find(self, file_find: str, default_value: str = '') -> str:
        """
        Busca el archivo en la lista, y retorna el Path relacionado con el. Si no se encuentra retorna el valor que se especifique como valor por defecto.

        :param file_find: Nombre del archivo que buscamos.
        :param default_value: Valor por defecto que se retornara si no se encuentra el archivo que buscamos.
        :return: String del path del archivo.

        """
        if self.is_exist(file_find):
            return self.files[file_find]
        return default_value

    @property
    def files(self) -> dict:
        """
        Diccionario de la lista de archivos almacenados.

        :return: Diccionario de archivos.

        """
        if self.__files is None:
            return {}
        return self.__files

    def set(self, file_name: str, file_path: str) -> bool:
        """
        Crea un archivo nuevo a la lista y si existe lo modifica.

        :param file_name: Nombre del archivo.
        :param file_path: Path del archivo.
        :return: True si se todo ha ido bien, False si falla.

        """
        if file_name:
            self.__files[file_name] = file_path
            return self.is_exist(file_name)
        return False

    def remove(self, file_find: str) -> bool:
        """
        Elimina el archivo que le especificamos de la lista.

        :param file_find: Nombre del archivo a eliminar.
        :return: True si se ha eliminado correctamente, False si se produce error.

        """
        if self.is_exist(file_find):
            del self.__files[file_find]
            return True
        return False
