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

import datetime
import lib.configStore
import collections
from enum import Enum

__all__ = ['Config', 'ConfigTypeReturn']

"""Configuration module"""


class ConfigTypeReturn(Enum):
    STR = 1
    INT = 2
    BOOL = 3
    LIST = 4
    DICT = 5
    TUPLE = 6


class Config(lib.configStore.ConfigStore):
    """Class to Storage and processing of configuration parameters."""

    def __init__(self, file, init_data: dict = None, obj_debug=None):
        self.__load = None
        self.__update = None
        super().__init__(file, obj_debug)
        self.data = init_data

    @property
    def data(self) -> dict:
        """Return Obtenemos los datos almacendados."""
        if self.__data:
            return self.__data
        return {}

    @data.setter
    def data(self, val):
        self.__update = datetime.datetime.now()
        self.__data = val

    @property
    def is_changed(self) -> bool:
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
    def is_load(self) -> bool:
        if self.__load is not None:
            return True
        return False

    def read(self, return_data=True):
        try:
            self.data = super().read()
            self.__load = datetime.datetime.now()
            self.__update = self.__load

        except Exception as e:
            self.debug.Exception(e)
            self.__load = None
            self.__update = None

        if return_data:
            return self.data
        return None

    def save(self) -> bool:
        try:
            super().save(self.data)
            self.__load = datetime.datetime.now()
            self.__update = self.__load
        except Exception as e:
            self.debug.Exception(e)
            return False
        return True

    def __convert_findkey_to_list(self, findkey, str_split: str = None) -> list:
        lreturn = []
        if isinstance(findkey, str):
            if str_split is None:
                lreturn = findkey.split()
            else:
                lreturn = findkey.split(str_split)
        elif isinstance(findkey, list):
            lreturn = findkey.copy()
        elif isinstance(findkey, tuple):
            lreturn = list(findkey)
        else:
            raise TypeError('Invalid type: findkey must be a string, list or tuple, not {0}.'.format(type(findkey)))
        return lreturn

    def __convert_list_to_dict(self, list_items, val):
        dreturn = {}
        if isinstance(list_items, list):
            target = list_items.pop(0)
            if list_items:
                dreturn[target] = self.__convert_list_to_dict(list_items, val)
            else:
                dreturn[target] = val
        else:
            dreturn[list_items] = val
        return dreturn

    def __update_value_findkey(self, source, overrides):
        # https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
        for key, val in overrides.items():
            if isinstance(source, collections.Mapping):
                if isinstance(val, collections.Mapping):
                    source[key] = self.__update_value_findkey(source.get(key, {}), val)
                else:
                    source[key] = val
            else:
                source = {key: overrides[key]}
        return source

    def get_conf(self, findkey, def_val=None, str_split: str = None, data_dict: dict = None, r_type: ConfigTypeReturn = ConfigTypeReturn.STR):
        """ Return value of the key that we are looking for and if this key does not exist, it
        will return def_val. If def_val is None it will return an object (empty) of the type
        that is defined in r_type.

        :param findkey (:obj:`list`of :obj:`tuple` of :obj:`str`): the target keys structure, which
        should be present. Support type [string | tuple | list].
        :param def_val (optional): It is the value that returns if the key we are looking for is not found.
        :param str_split (obj:`str`, optional): character that will be used to separate findkey if it is
        string type in the list conversion.
        :param data_dict (obj:`dict`, optional): the dictionary to be searched in. By default the self.data
        will be used.
        :param r_type (:obj:`list`of :obj:`tuple` of :obj:`str` of :obj:`int` of :obj:`bool`, optional): It is
        the type of object (empty), which will return if def_val is not defined or def_val is None and the key
        we are looking for was not found. For example, if we specify r_type = list, it returns [].
        :raises TypeError: if findkey is not a string, tuple or list or if r_type is not a string, list, dict,
        tuple, int or bool.

        Note:
            Parameter 'findkey' is not support type 'dict'.
            https://docs.python.org/3/library/collections.html#collections.OrderedDict

            Ordered dictionaries are just like regular dictionaries but have some
            extra capabilities relating to ordering operations. They have become less
            important now that the built-in dict class gained the ability to remember
            insertion order (this new behavior became guaranteed in Python 3.7).

        Example:
            >>> x = Config(None)
            >>> x.data = { 'level1': { 'level2': 'OK' } }
            >>> x.get_conf(['level1', 'level2'], 'Not Exist!')
            'OK'
            >>> x.get_conf(('level1', 'level2'), 'Not Exist!')
            'OK'
            >>> x.get_conf(('level1', 'level2', 'level3'), 'Not Exist!')
            'Not Exist!'
            >>> x.get_conf('level1', 'Not Exist!')
            {'level2': 'OK'}
            >>> x.get_conf('level2', r_type=lib.config.ConfigTypeReturn.LIST)
            []

        """

        if data_dict is None:
            data_dict = self.data

        data_return = None
        if data_dict:
            keys = self.__convert_findkey_to_list(findkey, str_split)

            work_dict = data_dict
            while keys:
                target = keys.pop(0)
                if isinstance(work_dict, dict):
                    if target in work_dict.keys():
                        if not keys:    # this is the last element in the findkey, and it is in the data_dict
                            data_return = work_dict[target]
                            break
                        else:   # not the last element of findkey, change the temp var
                            work_dict = work_dict[target]
                    else:
                        continue
                else:
                    continue

        if data_return is not None:
            return data_return

        if def_val is None:
            if r_type == ConfigTypeReturn.LIST:
                return []
            elif r_type == ConfigTypeReturn.DICT:
                return {}
            elif r_type == ConfigTypeReturn.TUPLE:
                return ()
            elif r_type == ConfigTypeReturn.INT:
                return 0
            elif r_type == ConfigTypeReturn.BOOL:
                return False
            elif r_type == ConfigTypeReturn.STR:
                return ''
            else:
                raise TypeError('Invalid type: r_type must be a string, list, dict, tuple, int or bool, not {0}.'.format(type(r_type)))
        return def_val

    def is_exist_conf(self, findkey, str_split: str = None, data_dict: dict = None):
        """ Return True if the given findkey is present within the structure of the source dictionary, False otherwise.

        The findkey format is list, taple, or string in which the str_split parameter is used as the deleting character.

        :param findkey: the target keys structure, which should be present. Support type [string | tuple | list].
        :param str_split (obj:`str`, optional): character that will be used to separate findkey if it is string type in the list conversion.
        :param data_dict (obj:`dict`, optional): the dictionary to be searched in.
        :returns Boolean: is the findkey structure present in data.
        :raises TypeError: if findkey is not a string, tuple or list

        Note:
            Parameter 'findkey' is not support type 'dict'.
            https://docs.python.org/3/library/collections.html#collections.OrderedDict

            Ordered dictionaries are just like regular dictionaries but have some
            extra capabilities relating to ordering operations. They have become less
            important now that the built-in dict class gained the ability to remember
            insertion order (this new behavior became guaranteed in Python 3.7).

        Example:
            >>> x = Config(None)
            >>> x.data = { 'level1': { 'level2': 'OK' } }
            >>> x.is_exist_conf(['level1', 'level2'])
            True
            >>> x.is_exist_conf(('level1', 'level2'))
            True
            >>> x.is_exist_conf(('level1', 'level2','level3'))
            False
            >>> x.is_exist_conf('level1')
            True
            >>> x.is_exist_conf('level1:level2', ':')
            True
            >>> x.is_exist_conf('level2:level1', ':', { 'level2': { 'level1': 'OK' } })
            True
            >>> x.is_exist_conf('level2:level1', ':', { 'level3': { 'level1': 'OK' } })
            False

        """

        if data_dict is None:
            data_dict = self.data

        if findkey and data_dict:
            keys = self.__convert_findkey_to_list(findkey, str_split)
            work_dict = data_dict
            while keys:
                target = keys.pop(0)
                if isinstance(work_dict, dict):
                    if target in work_dict.keys():
                        if not keys:    # this is the last element in the findkey, and it is in the data_dict
                            return True
                        else:   # not the last element of findkey, change the temp var
                            work_dict = work_dict[target]
                    else:
                        return False
                else:
                    return False
        return False

    def set_conf(self, findkey, val, str_split: str = None, data_dict: dict = None):
        """ Return true if the process was successful, False otherwise.

        The findkey format is list, taple, or string in which the str_split parameter is used as the deleting character.

        :param findkey: the target keys structure, which should be present. Support type [string | tuple | list].
        :param val: new value
        :param str_split (obj:`str`, optional): character that will be used to separate findkey if it is string type in the list conversion.
        :param data_dict (obj:`dict`, optional): the dictionary to be searched in. By default the self.data will be used.
        :returns Boolean: if it has been processed correctly.
        :returns Dict: if it has been processed correctly and data_dict is a dict.
        :raises TypeError: if findkey is not a string, tuple or list

        Note:
            Parameter 'findkey' is not support type 'dict'.
            https://docs.python.org/3/library/collections.html#collections.OrderedDict

            Ordered dictionaries are just like regular dictionaries but have some
            extra capabilities relating to ordering operations. They have become less
            important now that the built-in dict class gained the ability to remember
            insertion order (this new behavior became guaranteed in Python 3.7).

        Example:
            >>> x = Config(None)
            >>> x.set_conf('level1', 'OK')
            True
            >>> x.data
            {'level1': 'OK'}
            >>> x.set_conf(['level1','level2'], 'OK')
            True
            >>> x.data
            {'level1': {'level2': 'OK'}}
            >>> x.set_conf('level1:level2:level3', 'OK',':')
            True
            >>> x.data
            {'level1': {'level2': {'level3': 'OK'}}}
            >>> x.set_conf('level0', 'OK', data_dict = {'level1': 'OK'})
            {'level1': 'OK', 'level0': 'OK'}

        """

        if findkey:
            keys = self.__convert_findkey_to_list(findkey, str_split)
            if data_dict is not None:
                work_dict = data_dict
            elif self.data is not None:
                work_dict = self.data
            else:
                work_dict = {}

            keyupdate = self.__convert_list_to_dict(keys, val)
            work_dict = self.__update_value_findkey(work_dict, keyupdate)

            if data_dict is not None:
                return work_dict

            self.data = work_dict
            return True
        return False
