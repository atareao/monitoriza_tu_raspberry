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


import shlex
import subprocess
import paramiko

from enum import Enum
from lib.switch import Switch

__author__ = "Javier Pastor"
__copyright__ = "Copyright © 2019, Javier Pastor"
__credits__ = "Javier Pastor"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = 'Javier Pastor'
__email__ = "python@cerebelum.net"
__status__ = "Development"

__all__ = ['EnumLocationExec', 'Exec']


class EnumLocationExec(Enum):
    local = 1
    remote = 2


class Exec(object):

    """ Main Class. """

    def __init__(self, command: str = ""):
        """ Inicializa el objeto y lo configura con los valores por defecto.

        :param command: Comando a ejecutar.

        """

        self.__location = EnumLocationExec.local
        self.__command = command
        self.__host = ""
        self.__port = 0
        self.__user = ""
        self.__password = ""
        self.__timeout = 30
        self.set_remote()

    @property
    def location(self) -> EnumLocationExec:
        return self.__location

    @location.setter
    def location(self, val: EnumLocationExec):
        self.__location = val

    @property
    def command(self) -> str:
        return self.__command

    @command.setter
    def command(self, val: str):
        self.__command = val

    @property
    def host(self) -> str:
        return self.__host

    @host.setter
    def host(self, val: str):
        self.__host = val

    @property
    def port(self) -> int:
        return self.__port

    @port.setter
    def port(self, val: int):
        self.__port = val

    @property
    def user(self) -> str:
        return self.__user

    @user.setter
    def user(self, val: str):
        self.__user = val

    @property
    def password(self) -> str:
        return self.__password

    @password.setter
    def password(self, val: str):
        self.__password = val

    @property
    def timeout(self) -> float:
        return self.__timeout

    @timeout.setter
    def timeout(self, val: float):
        self.__timeout = val

    def __is_command_exist(self) -> bool:
        if self.command and len(self.command.strip()) > 0:
            return True
        else:
            return False

    def __execute_local(self):
        """ Ejecuta el comando en el equipo local.

        :return: Retorna stdout, stderr y exit_code

        """
        data_return = {'out': None, 'err': None, 'code': None}

        if self.__is_command_exist():
            command_with_args = shlex.split(self.command)
            execution = subprocess.Popen(command_with_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = execution.communicate()

            data_return['out'] = stdout.decode()
            data_return['err'] = stderr.decode()
            data_return['code'] = execution.returncode
            data_return['exception'] = None

        return data_return

    def __execute_remote(self):
        """ Ejecuta el comando en el host remoto que se ha configurado.

        :return: Retorna stdout, stderr y exit_code

        """
        # http://docs.paramiko.org/en/2.6/api/client.html
        # https://stackoverflow.com/questions/7002878/basic-paramiko-exec-command-help
        # https://www.programcreek.com/python/example/4561/paramiko.SSHClient

        data_return = {'out': None, 'err': None, 'code': None, 'exception': None}

        if self.__is_command_exist():
            shell = None
            client = None
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=self.host,
                               port=self.port,
                               username=self.user,
                               password=self.password,
                               timeout=self.timeout)
                shell = client.invoke_shell()

                # TODO: Pendiente añadir soporte para multiples commands.
                _, stdout, stderr = client.exec_command(self.command)

                # Espera a que termine de ejecutarse el comando y obtenemos el exit code.
                exit_code = stdout.channel.recv_exit_status()

                # read_out = stdout if stdout else ""
                # read_err = stderr if stdout else ""

                read_out = stdout.read().decode() if stdout else ""
                read_err = stderr.read().decode() if stdout else ""

                data_return = {'out': read_out, 'err': read_err, 'code': exit_code, 'exception': None}

            except Exception as ex:
                # http://docs.paramiko.org/en/2.6/api/ssh_exception.html
                # print("Exception:", ex)
                # Authentication failed.
                data_return = {'out': None, 'err': None, 'code': None, 'exception': ex}

            finally:
                if shell:
                    shell.close()
                if client:
                    client.close()

        return data_return

    def start(self):
        """ Ejecuta el comando y mira si tiene que ejecutarlo localmente o se tiene que ejecutar en otro host. """

        tmp_exec = {'out': None, 'err': None}
        if self.__is_command_exist():
            with Switch(self.location) as case:
                if case(EnumLocationExec.local):
                    tmp_exec = self.__execute_local()

                elif case(EnumLocationExec.remote):
                    tmp_exec = self.__execute_remote()

        return tmp_exec['out'], tmp_exec['err'], tmp_exec['code'], tmp_exec['exception']

    def set_remote(self, host: str = "", port: int = 22, user: str = "root", password: str = None,
                   timeout: float = None):
        """ Configuramos los datos de conexión al host remoto.

        :param host: Nombre del host o IP
        :param port: Puerto que usa SSH
        :param user: Nombre de usuario con el que nos logeamos en el sistema.
        :param password: Password del usuario.
        :param timeout: Timeout al intentar conectar.
        :return:

        """

        # TODO: Pendiente añadir soporte key public/private

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        if timeout is not None:
            self.timeout = timeout

    @staticmethod
    def execute(command: str = "", host: str = "", port: int = 22, user: str = "", password: str = "",
                timeout: float = None):
        """ Ejecuta el comando que le pasamos sin tener que crear el objeto Exec.

        :param command: Comando ha ejecutar.
        :param host: Host o IP
        :param port: Puerto SSH
        :param user: Usuario login
        :param password: Password Login
        :param timeout: Tiempo en segundos hasta que falla el intento de conexión.
        :return: Retorna stdout y stderr

        """

        tmp_exec = Exec(command=command)
        if len(host.strip()) > 0:
            tmp_exec.location = EnumLocationExec.remote
            tmp_exec.set_remote(host=host, port=port, user=user, password=password, timeout=timeout)
        return tmp_exec.start()
