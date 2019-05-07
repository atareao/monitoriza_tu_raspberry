#!/bin/bash
if [ "$(id -u)" != "0" ]; then
    echo "Sorry, you are not root."
    exit 1
fi
mkdir -p '/etc/watchful'
cp data/config.json /etc/watchful/
cp data/status.json /etc/watchful/
cp data/watchful.service /lib/systemd/system/
cp data/watchful.timer /lib/systemd/system/
mkdir -p '/opt/watchful/watchfuls'
cp src/*.py /opt/watchful/
cp src/watchfuls/*.py /opt/watchful/watchfuls/
systemctl daemon-reload
systemctl enable watchful.timer
systemctl start watchful.timer