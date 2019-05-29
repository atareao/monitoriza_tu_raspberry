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
from lib.object_base import ObjectBase
from lib.debug import DebugLevel
from time import sleep

__all__ = ['Telegram']


class Telegram(ObjectBase):

    class PoolSendMsg(threading.Thread):

        tg = None
        __run_while = True
        __group_messages = True

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
            self.__run_while = True
            msg_group = ''
            while True:
                if self.tg and len(self.tg.list_msg) > 0:
                    msg = self.tg.list_msg.pop()
                    self.tg.debug.print("Telegram > Send > Msg: {0}".format(msg))
                    if self.group_messages:
                        msg_group += msg + "\n"
                    else:
                        self.tg.api_send_message(msg)
                    self.tg.count_msg_send += 1
                else:
                    if self.group_messages:
                        if msg_group:
                            self.tg.api_send_message(msg_group)
                            msg_group = ''

                    if not self.__run_while:
                        break
            return

        def stop(self):
            self.__run_while = False

        @property
        def group_messages(self) -> bool:
            return self.__group_messages

        @group_messages.setter
        def group_messages(self, val: bool):
            self.__group_messages = val

    def __init__(self, token, chat_id):
        self.list_msg = []
        self.count_msg = 0
        self.count_msg_send = 0
        self.token = token
        self.chat_id = chat_id

        self.pool_send_msg = self.PoolSendMsg()
        self.pool_send_msg.tg = self
        self.pool_send_msg.setDaemon(True)
        self.pool_send_msg.start()

        self.group_messages = False

    def send_message(self, message):
        self.add_list(message)

    def send_message_end(self, hostname):
        if self.count_msg > 0:
            s_message = "Summary *{0}*, get *{1}* new Message.".format(hostname, self.count_msg)
            # s_message = "{0} {1} {2} {3}{3}{3}".format(u'\U00002139', u'\U0001F4BB', s_message, u'\U0000261D')
            s_message = "{0} {1} {2}{2}{2}".format(u'\U00002139', s_message, u'\U0000261D')
            self.add_list(s_message)
            # Sleep para asegurarnos de que el mensaje anterior esta en la lista antes de iniciar el siguiente While.
            sleep(1)

        # Esperamos a que la lista de mensajes esta vacía.
        while True:
            if len(self.list_msg) == 0:
                break

        self.count_msg = 0
        self.count_msg_send = 0

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
            self.debug.print("Error: Telegram Token is Null", DebugLevel.error)
        if not self.chat_id:
            self.debug.print("Error: Telegram Chat ID is Null", DebugLevel.error)
        return False

    @property
    def group_messages(self) -> bool:
        return self.pool_send_msg.group_messages

    @group_messages.setter
    def group_messages(self, val: bool):
        self.pool_send_msg.group_messages = val


# https://apps.timwhitlock.info/emoji/tables/unicode
