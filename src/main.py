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

"""Module Main."""


import os
import sys
import time
import argparse
import globales
import lib.debug
import lib.monitor
import lib.config


def _dir():
    """Path run program.

    Returns:
    str: Returning value

    """
    return os.path.dirname(os.path.abspath(__file__))


def _modules_dir():
    """Path modules.

    Returns:
    str: Returning value

    """
    return os.path.join(_dir(), 'watchfuls')


def _lib_dir():
    """Path lib's.

    Returns:
    str: Returning value

    """
    return os.path.join(_dir(), 'lib')


def _config_dir():
    """Path config files.

    Returns:
    str: Returning value

    """
    if _dir().find('src') != -1:
        return os.path.normpath(os.path.join(_dir(), '../data/'))
    else:
        return '/etc/watchful/'


def _var_dir():
    """Path /var/lib...

    Returns:
    str: Returning value

    """
    if _dir().find('src') != -1:
        return '/var/lib/watchful/dev/'
    else:
        return '/var/lib/watchful/'


def arg_check_dir_path(path):
    if not path:
        return ''
    elif os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError("{0} is not a valid path".format(path))


def arg_check_timer(timercheck):
    if timercheck.isnumeric() and int(timercheck) > 0:
        return timercheck
    else:
        raise argparse.ArgumentTypeError("{0} is not a valid timer".format(timercheck))


if __name__ == "__main__":

    # allow_abbrev modo estricto en la detección de argumento, de lo contrario --pat lo reconocería como --path
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument('-c', '--clear', default=False, action="store_true", dest="clear_status", help="clear status.json")
    ap.add_argument('-d', '--daemon', default=False, action="store_true", dest="daemon_mode", help="start mode daemon")
    ap.add_argument('-t', '--timer', default=None, type=arg_check_timer, dest="timer_check", help="timer interval of the check in daemon mode")
    ap.add_argument('-v', '--verbose', default=None, action="store_true", dest="verbose", help="verbose mode true")
    ap.add_argument('-p', '--path', default=None, type=arg_check_dir_path, dest="path", help="path config files")
    args = vars(ap.parse_args())

    if args['path'] is None:
        args['path'] = _config_dir()

    sys.path.append(_lib_dir())
    sys.path.append(_modules_dir())

    globales.GlobDebug = lib.debug.Debug(True)

    Config = lib.config.Config(os.path.join(args['path'], 'config.json'))
    Config.read()
    if Config:
        if not Config.is_exist_conf(['daemon', 'timer_check']):
            Config.set_conf(['daemon', 'timer_check'], 300)

        if not Config.is_exist_conf(['global', 'debug']):
            Config.set_conf(['global', 'debug'], False)
    else:
        raise Exception("Error load config gloabl.")

    if args['verbose'] is None:
        globales.GlobDebug.enabled = Config.get_conf(['global', 'debug'], globales.GlobDebug.enabled)

    if args['timer_check'] is None:
        args['timer_check'] = Config.get_conf(['daemon', 'timer_check'], 0)

    globales.GlobMonitor = lib.monitor.Monitor(_dir(), args['path'], _modules_dir(), _var_dir())

    if args['clear_status'] is True:
        globales.GlobMonitor.clearStatus()

    if args['daemon_mode'] is False:
        globales.GlobDebug.print("Run Mode Single Process", lib.debug.DebugLevel.debug)
        globales.GlobMonitor.check()
    else:
        globales.GlobDebug.print("Run Mode Daemon", lib.debug.DebugLevel.debug)
        while True:
            globales.GlobMonitor.check()
            if int(args['timer_check']) == 0:
                break
            globales.GlobDebug.print("Waiting {0} seconds...".format(args['timer_check']), lib.debug.DebugLevel.debug)
            try:
                time.sleep(int(args['timer_check']))
            except KeyboardInterrupt:
                globales.GlobDebug.print("Process cancel  by the user!!", lib.debug.DebugLevel.debug)
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
            except Exception as e:
                globales.GlobDebug.Exception(e)
