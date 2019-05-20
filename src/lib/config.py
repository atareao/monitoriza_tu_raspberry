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

import globales
import datetime
import lib.configStore

__all__ = ['Config']

"""Configuration module"""


class Config(lib.configStore.ConfigStore):
    """Class to Storage and processing of configuration parameters."""

    def __init__(self, file, init_data=None):
        self.__load = None
        self.__update = None
        super().__init__(file)
        self.data = init_data

    @property
    def data(self):
        """Return Obtenemos los datos almacendados."""
        return self.__data

    @data.setter
    def data(self, val):
        self.__update = datetime.datetime.now()
        self.__data = val

    @property
    def is_changed(self):
        if self.__update and not self.__load:
            # Se han insertado datos manulamente, no se ha leido ningun
            # archivo.
            return True
        if not self.__update or not self.__load:
            # No se ha cargado ningun archivo ni se han insertado datos.
            return False
        if self.__update > self.__load:
            # La fecha de actualizacione es superior a la de carga
            # por lo que se ha modificado.
            return True
        return False

    @property
    def is_load(self):
        if self.__load is not None:
            return True
        return False

    def read(self, return_data=True):
        try:
            self.data = super().read()
            self.__load = datetime.datetime.now()
            self.__update = self.__load

        except Exception as e:
            globales.GlobDebug.Exception(e)
            self.__load = None
            self.__update = None

        if return_data:
            return self.data
        return None

    def save(self):
        try:
            super().save(self.data)
            self.__load = datetime.datetime.now()
            self.__update = self.__load
        except Exception as e:
            globales.GlobDebug.Exception(e)
            return False
        return True

    def get_conf(self, findkey, def_val=None, r_type=None):
        """Get the stored value of the key you specify, search supports different levels.

        Args:
            findkey (:obj:`list`of :obj:`tuple` of :obj:`str`): It is the key that contains
            the setting you want to read.
            This parameter accepts the following types [string | tuple | list].

            def_val(optional): It is the value that returns if the key we are looking for is not found.

            r_type (optional): It is the type of object (empty), which will return if def_val is not
            defined or def_val is None and the key we are looking for was not found.
            For example, if we specify r_type = list, it returns [].

        Returns:
            The return value of the key that we are looking for and if this key does not
            exist, it will return def_val.
            If def_val is None it will return an object (empty) of the type that is defined
            in r_type.

        Note:
            Parameter 'findkey' is not support type 'dict'.
            https://docs.python.org/3/library/collections.html#collections.OrderedDict

            Ordered dictionaries are just like regular dictionaries but have some
            extra capabilities relating to ordering operations. They have become less
            important now that the built-in dict class gained the ability to remember
            insertion order (this new behavior became guaranteed in Python 3.7).

        """
#        Example:
#            Config Load:
#            {
#                'levle1': {
#                    'level2': 'OK'
#                }
#            }
#
#            Function:
#                y1 = x.get_conf(['level1', 'level2'], 'Not Exist!')
#                y2 = x.get_conf(('level1', 'level2'), 'Not Exist!')
#                y3 = x.get_conf(('level1', 'level2', 'level3'), 'Not Exist!')
#                y4 = x.get_conf('level1', 'Not Exist!')
#                y5 = x.get_conf('level2', None, list)
#
#            Return:
#                y1 = OK
#                y2 = OK
#                y3 = Not Exist!
#                y4 = OK
#                y5 = {}

        return self.__get_conf(self.data, findkey, def_val, r_type)

    def __get_conf(self, data, findkey, def_val=None, r_type=None):
        data_return = None
        if data:
            if isinstance(findkey, list) or isinstance(findkey, tuple):
                if isinstance(findkey, tuple):
                    findkey = list(findkey)

                i = findkey.pop(0)
                if i in data.keys():

                    if isinstance(data[i], list) or isinstance(data[i], tuple) or isinstance(data[i], dict):
                        # comprueba que no hay más niveles de búsqueda
                        if len(findkey) == 0:
                            data_return = data[i]
                        else:
                            data_return = self.__get_conf(data[i], findkey, def_val, r_type)
                    else:
                        # comprueba que no hay más niveles de búsqueda
                        if len(findkey) == 0:
                            data_return = data[i]
                else:
                    return None

            elif isinstance(findkey, str):
                if findkey in data.keys():
                    data_return = data[findkey]
                else:
                    data_return = None
            else:
                raise ValueError('findkey type [{0}] in not valid.'.format(type(findkey)))

        if data_return is not None:
            return data_return

        if not def_val:
            if isinstance(r_type, list):
                return []
            elif isinstance(r_type, dict):
                return {}
            elif isinstance(r_type, tuple):
                return ()
            elif isinstance(r_type, int) or isinstance(r_type, bool):
                return None
            else:
                return ''

        return def_val

    def is_exist_conf(self, findkey):
        """
        Check if a key exists in the stored data, supporting search in different levels.

        Parameters:
            findkey: It is the key we want to know if it exists. This parameter accepts
                     the following types [string | tuple | list].

        Return:
            True  = Yes exist.
            False = Not exists.

        Warnings:
            Parameter 'findkey' is not support type 'dict'.
            https://docs.python.org/3/library/collections.html#collections.OrderedDict

            Ordered dictionaries are just like regular dictionaries but have some
            extra capabilities relating to ordering operations. They have become less
            important now that the built-in dict class gained the ability to remember
            insertion order (this new behavior became guaranteed in Python 3.7).

        Example:
            Config Load:
            {
                'levle1': {
                    'level2': 'OK'
                }
            }

            Query:
                y1 = x.isExist_conf(['level1', 'level2'])
                y2 = x.isExist_conf(('level1', 'level2'))
                y3 = x.isExist_conf(('level1', 'level2','level3'))
                y4 = x.isExist_conf('level1')

            Return:
                y1 = True
                y2 = True
                y3 = False
                y4 = True

        """
        return self.__is_exist_conf(self.data, findkey)

    def __is_exist_conf(self, data, findkey):
        """Return Ture is findkey exist or False is not exist."""
        if findkey and data:
            if isinstance(findkey, list) or isinstance(findkey, tuple):
                if isinstance(findkey, tuple):
                    findkey = list(findkey)
                i = findkey.pop(0)
                if i in data.keys():
                    if isinstance(data[i], list) or isinstance(data[i], tuple) or isinstance(data[i], dict):
                        # comprueba que no hay más niveles de búsqueda
                        if len(findkey) == 0:
                            return True
                        else:
                            if self.__isExist_Conf(data[i], findkey):
                                return True
                    else:
                        # comprueba que no hay más niveles de búsqueda
                        if len(findkey) == 0:
                            return True

            elif isinstance(findkey, str):
                if findkey in data.keys():
                    return True

            else:
                raise ValueError('key type [{0}] in not valid.'.format(type(findkey)))

        return False

    def set_conf(self, findkey, val):
        """
        It allows us to modify the value of the key we want. AT THE MOMENT THE OPTION OF
        MULTIPLE LEVELS IS NOT SUPPORTED. :(

        Parameters:
            findkey: It is the key that we want to look for to modify its value. At the moment
                        the option of multiple levels is not supported. It only accepts String type.

        Example:
            Config Load:
            { }

            Function:
                x.set_conf('level0', True)
                x.set_conf('level1', {'opt1': 'OK'}")

            Config after set:
            {
                'level0': True,
                'level1': {
                    'opt1': 'OK'
                }
            }

        """
        if not findkey:
            return False
        if self.data is None:
                self.data = {}
        if isinstance(findkey, list) or isinstance(findkey, tuple):
            raise ValueError('key type [{0}] in not valid.'.format(type(findkey)))
            #isExisteKey = self.isExist_Conf(findkey)
            #if isinstance(findkey, tuple):
            #    findkey = list(findkey)
            #
            #print (len(findkey))
            #if isExisteKey:
            #    pass
            #else:
            #    pass
            #
            ##i = findkey.pop(0)
            ##if i in data.keys():
            ##    if isinstance(data[i], list) or isinstance(data[i], tuple) or isinstance(data[i], dict):
            ##        #comprueba que no hay más niveles de búsqueda
            ##        if len(findkey) == 0:
            ##            return True
            ##        else:
            ##            if self.__isExist_Conf(data[i], findkey):
            ##                return True
            ##    else:
            ##        #comprueba que no hay más niveles de búsqueda
            ##        if len(findkey) == 0:
            ##            return True
        elif isinstance(findkey, str):
            self.data[findkey] = val
            return True
        else:
            raise ValueError('key type [{0}] in not valid.'.format(type(findkey)))
