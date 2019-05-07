#!/bin/bash
if [ "$(id -u)" != "0" ]; then
    echo "Sorry, you are not root."
    exit 1
fi
systemctl disable watchful.timer
systemctl stop watchful.timer
rm /lib/systemd/system/watchful.service
rm /lib/systemd/system/watchful.timer
systemctl daemon-reload
rm -rf '/etc/watchful'
rm -rf '/opt/watchful'