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
import collections

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
                    keys = list(findkey)
                else:
                    keys = findkey.copy()
                i = keys.pop(0)
                if i in data.keys():

                    if isinstance(data[i], list) or isinstance(data[i], tuple) or isinstance(data[i], dict):
                        # comprueba que no hay más niveles de búsqueda
                        if len(keys) == 0:
                            data_return = data[i]
                        else:
                            data_return = self.__get_conf(data[i], keys, def_val, r_type)
                    else:
                        # comprueba que no hay más niveles de búsqueda
                        if len(keys) == 0:
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

    def __convert_findkey_to_list(self, findkey, str_split):
        lreturn = None
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
            raise ValueError('findkey type [{0}] in not valid.'.format(type(findkey)))
        return lreturn

    def is_exist_conf(self, findkey, str_split=None, data_dic=None):
        """ Return True if the given findkey is present within the structure of the source dictionary, False otherwise.
        
        The findkey format is list, taple, or string in which the str_split parameter is used as the deleting character.

        :param findkey: the target keys structure, which should be present. Support type [string | tuple | list].
        :param str_split (obj:`str`, optional): character that will be used to separate findkey if it is string type in the list conversion.
        :param data_dic (obj:`dict`, optional): the dictionary to be searched in.
        :returns Boolean: is the findkey structure present in data.
        :raises ValueError: if findkey is not a string | tuple | list

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
#            { 'levle1': { 'level2': 'OK' } }
#            Query:
#                y1 = x.isExist_conf(['level1', 'level2'])
#                y2 = x.isExist_conf(('level1', 'level2'))
#                y3 = x.isExist_conf(('level1', 'level2','level3'))
#                y4 = x.isExist_conf('level1')
#                y5 = x.isExist_conf('level1:level2', ':')
#                y6 = x.isExist_conf('level2:level1', ':', { 'levle2': { 'level1': 'OK' } })
#            Return:
#                y1 = True
#                y2 = True
#                y3 = False
#                y4 = True
#                y5 = True
#                y6 = True

        if data_dic is None:
            data_dic = self.data

        if findkey and data_dic:
            keys = self.__convert_findkey_to_list(findkey, str_split)
            work_dict = data_dic
            while keys:
                target = keys.pop(0)
                if isinstance(work_dict, dict):
                    if target in work_dict.keys():
                        if not keys:    # this is the last element in the findkey, and it is in the data_dic
                            return True
                        else:   # not the last element of findkey, change the temp var
                            work_dict = work_dict[target]
                    else:
                        return False
                else:
                    return False
        return False



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

    # https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    def __update_value_findkey(self, source, overrides):
        for key, val in overrides.items():
            if isinstance(source, collections.Mapping):
                if isinstance(val, collections.Mapping):
                    source[key] = self.__update_value_findkey(source.get(key, {}), val)
                else:
                    source[key] = val
            else:
                source = {key: overrides[key]}
        return source

    def set_conf(self, findkey, val, str_split=None, data_dic=None):
        """ Return true if the process was successful, False otherwise.

        The findkey format is list, taple, or string in which the str_split parameter is used as the deleting character.

        :param findkey: the target keys structure, which should be present. Support type [string | tuple | list].
        :param val: new value
        :param str_split (obj:`str`, optional): character that will be used to separate findkey if it is string type in the list conversion.
        :param data_dic (obj:`dict`, optional): the dictionary to be searched in. By default the self.data will be used.
        :returns Boolean: if it has been processed correctly.
        :raises ValueError: if findkey is not a string | tuple | list

        Note:
            Parameter 'findkey' is not support type 'dict'.
            https://docs.python.org/3/library/collections.html#collections.OrderedDict

            Ordered dictionaries are just like regular dictionaries but have some
            extra capabilities relating to ordering operations. They have become less
            important now that the built-in dict class gained the ability to remember
            insertion order (this new behavior became guaranteed in Python 3.7).

        """

        if findkey:
            keys = self.__convert_findkey_to_list(findkey, str_split)
            if data_dic is not None:
                work_dict = data_dic
            elif self.data is not None:
                work_dict = self.data
            else:
                work_dict = {}

            keyupdate = self.__convert_list_to_dict(keys, val)
            work_dict = self.__update_value_findkey(work_dict, keyupdate)

            if data_dic is not None:
                return work_dict

            self.data = work_dict
            return True
        return False
