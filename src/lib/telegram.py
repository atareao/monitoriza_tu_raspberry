#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Monitorize your Raspberry Pi
#
# Copyright © 2019  Javier Pastor (aka vsc55)
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

import threading
import requests
import lib.debug
from lib.object_base import ObjectBase
from time import sleep

__all__ = ['Telegram']


class Telegram(ObjectBase):

    class DaemonSendMsg(threading.Thread):

        tg = None
        __run_while = True

        # https://rstopup.com/ejecutar-un-proceso-y-salir-sin-esperar-a-que-se.html
        # def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        #     super().__init__(self, group=group, target=target, name=name, verbose=verbose)
        #     self.args = args
        #     self.kwargs = kwargs
        #     self.setDaemon(True)
        #     self.tg = None
        #     self.__run_while = True
        #     return

        def run(self):
            # TODO: Pendiente agrupar mensajes
            self.__run_while = True
            while True:
                if self.tg and len(self.tg.list_msg) > 0:
                    msg = self.tg.list_msg.pop()
                    self.tg.api_send_message(msg)
                    self.tg.count_msg_send += 1
                else:
                    if not self.__run_while:
                        break
            return

        def stop(self):
            self.__run_while = False

    def __init__(self, token, chat_id):
        self.list_msg = []
        self.count_msg = 0
        self.count_msg_send = 0
        self.token = token
        self.chat_id = chat_id

        self.daemon_send_msg = self.DaemonSendMsg()
        self.daemon_send_msg.tg = self
        self.daemon_send_msg.setDaemon(True)
        self.daemon_send_msg.start()

    def send_message(self, message):
        self.add_list(message)

    def send_message_end(self):
        # Esperamos que la lista se vacíe antes de enviar el mensaje resumen.
        while True:
            if len(self.list_msg) == 0:
                break

        if self.count_msg > 0:
            s_message = "{0} Summary, get *{1}* new Message. {2}{2}{2}".format(u'\U00002139', self.count_msg, u'\U0000261D')
            self.add_list(s_message)
            # Sleep para evitar que el stop se ejecute antes de que se procese el mensaje de resumen.
            sleep(1)
            self.daemon_send_msg.stop()

        # Esperamos a que el damon_send_msg se muera.
        while True:
            if not self.daemon_send_msg.isAlive():
                break

    def add_list(self, message):
        # Efectuamos insert para mantener el orden.
        self.list_msg.insert(0, message)
        self.count_msg += 1

    def api_send_message(self, message):
        if message and self.token and self.chat_id:
            requests.post('https://api.telegram.org/bot{0}/sendMessage'.format(self.token),
                          data={'chat_id': self.chat_id, 'text': message, 'parse_mode': 'Markdown'})
            return True
        if not self.token:
            self.debug.print("Error: Telegram Token is Null", lib.debug.DebugLevel.error)
        if not self.chat_id:
            self.debug.print("Error: Telegram Chat ID is Null", lib.debug.DebugLevel.error)
        return False


# https://apps.timwhitlock.info/emoji/tables/unicode
