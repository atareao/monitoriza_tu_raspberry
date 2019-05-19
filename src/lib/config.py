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
from lib.debug import *
from lib.configStore import *

__all__ = ['Config']

class Config(ConfigStore):

    __load=None
    __update=None

    def __init__(self, file):
        super().__init__(file)
        self.data = None

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, val):
        __update = datetime.datetime.now()
        self.__data = val

    @property
    def isChanged(self):
        if __update and not __load:
            #Se han insertado datos manulamente, no se ha leido ningun archivo.
            return True
        if not __update or not __load:
            #No se ha cargado ningun archivo ni se han insertado datos.
            return False
        if __update > __load:
            #la fecha de actualizacione es superior a la de carga por lo que se ha modificado.
            return True
        return False

    @property
    def isLoad(self):
        if __load:
            return True
        return False

    def read(self, returnData=True):
        try:
            self.data = super().read()
            self.__load=datetime.datetime.now()
            self.__update=self.__load
            
        except Exception as e:
            globales.GlobDebug.Exception(e)
            self.__load=None
            self.__update=None

        if returnData:
            return self.data
        
    def save(self):
        try:
            super().save(self.data)
            self.__load=datetime.datetime.now()
            self.__update=self.__load
        except Exception as e:
            globales.GlobDebug.Exception(e)
            return False
        return True

    def read_conf(self, findkey, default_val=None, returnType=None):
        return self.__read_conf_find(self.data, findkey , default_val, returnType)

    def __read_conf_find(self, data, findkey, default_val=None, returnType=None):
        dataReturn = None
        if data:
            if isinstance(findkey, dict):
                #Se anula ya que hace cosas raras en ocasiones da None otras lee bien.
                return None

            elif isinstance(findkey, list) or isinstance(findkey, dict) or isinstance(findkey, tuple):

                #print("findkey:",findkey)
                #print("count:",len(findkey))

                if isinstance(findkey, dict):
                    i = findkey.popitem()[0]
                    [key for key in findkey if key == i]
                else:
                    if isinstance(findkey, tuple):
                        findkey = list(findkey)
                    i = findkey.pop(0)
                    
                print("i:",i)

                if i in data.keys():
                    #print("d:", data[i])
                    #print("t:",type(data[i]))

                    if isinstance(data[i], list) or isinstance(data[i], tuple) or isinstance(data[i], dict):
                        if len(findkey) == 0:
                            dataReturn = data[i]
                        else:
                            dataReturn = self.__read_conf_find(data[i], findkey, default_val, returnType)
                    else:
                        if len(findkey) == 0:
                            dataReturn = data[i]
                else:
                    return None

            else:
                print ("other:", findkey)
                if findkey in data.keys():
                    return data[findkey]
                return None
             

        if dataReturn != None:
            return dataReturn


        if isinstance(returnType, list):
            if default_val:
                return default_val
            return []
        elif isinstance(returnType, dict):
            if default_val:
                return default_val
            return {}
        elif isinstance(returnType, tuple):
            if default_val:
                return default_val
            return ()
        elif isinstance(returnType, int) or isinstance(returnType, bool):
            if default_val:
                return default_val
            return None
        else:
            if default_val:
                return default_val
            return ''