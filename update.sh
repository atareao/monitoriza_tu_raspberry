#!/bin/bash
if [ "$(id -u)" != "0" ]; then
    echo "Sorry, you are not root."
    exit 1
fi
systemctl stop watchful.timer
rm -rf '/opt/watchful'
mkdir -p '/opt/watchful/lib'
mkdir -p '/opt/watchful/watchfuls'
cp src/*.py /opt/watchful/
cp src/lib/*.py /opt/watchful/lib/
cp src/watchfuls/*.py /opt/watchful/watchfuls/
systemctl start watchful.timer