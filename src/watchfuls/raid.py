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

from lib import Switch
from lib.modules import ModuleBase
from lib.linux import RAID_Mdstat


class Watchful(ModuleBase):

    __path_mdstat = "/proc/mdstat"

    def __init__(self, monitor):
        super().__init__(monitor, __name__)

    def check(self):
        list_md = RAID_Mdstat(self.__path_mdstat).read_status()
        if len(list_md) == 0:
            message = "*No RAID's* in the system. {0}".format(u'\U00002705')
            self.dict_return.set("None", True, message)
        else:
            for (key, value) in list_md.items():
                # print("key:", key, " - Val:", value)

                other_data = {}
                is_warning = True
                with Switch(value.get("update", '')) as case:
                    if case(RAID_Mdstat.UpdateStatus.ok):
                        is_warning = False
                        message = "RAID *{0}* in good status. {1}".format(key, u'\U00002705')

                    elif case(RAID_Mdstat.UpdateStatus.error):
                        message = "*RAID {0} is degraded.* {1}".format(key, u'\U000026A0')

                    elif case(RAID_Mdstat.UpdateStatus.recovery):
                        other_data['percent'] = value.get("recovery", {}).get('percent', -1)
                        other_data['finish'] = value.get("recovery", {}).get('finish', -1)
                        other_data['speed'] = value.get("recovery", {}).get('speed', -1)

                        message = "*RAID {0} is degraded, recovery status {1}%, estimate time to finish {2}.* {3}".\
                            format(key, other_data['percent'], other_data['finish'], u'\U000026A0')

                    else:
                        message = "*RAID {0} Unknown Error*. {1}".format(key, u'\U000026A0')

                self.dict_return.set(key, not is_warning, message, other_data=other_data)

        super().check()
        return self.dict_return
