#!/bin/bash
if [ "$(id -u)" != "0" ]; then
    echo "Sorry, you are not root."
    exit 1
fi

systemctl disable watchful.timer
systemctl stop watchful.timer
rm '/lib/systemd/system/watchful.service'
rm '/lib/systemd/system/watchful.timer'
systemctl daemon-reload

rm -f '/etc/watchful/status.json'
rm -f '/var/lib/watchful/status.json'
rm -f '/var/lib/watchful/dev/status.json'
rm -rf '/opt/watchful'
mkdir -p '/var/lib/watchful'
mkdir -p '/opt/watchful'
cp src/*.py /opt/watchful/
for f in src/*/
do
  NAMEDIR=${f#"src/"}
  NAMEDIR=${NAMEDIR%"/"}
  PATH_DEST="/opt/watchful/${NAMEDIR}"
  mkdir ${PATH_DEST}
  if [[ "${NAMEDIR:0:2}" != "__" ]]; then
	cp $f*.py ${PATH_DEST}/
  fi  
done
for f in data/*.json
do
  NAMEFILE=${f#"data/"}
  EXTTMP=$(date +%Y%m%d%H%M%S)
  PATH_DEST="/etc/watchful/${NAMEFILE}"
  
  if [[ ! -f "$PATH_DEST" ]]; then
    cp $f ${PATH_DEST}
  else
	if [[ $(diff $f ${PATH_DEST}) ]]; then
		echo "Info: File (${NAMEFILE}) exists, the new configuration will be copied with the name(${NAMEFILE}.${EXTTMP})."
		cp $f ${PATH_DEST}.${EXTTMP}
	fi
  fi
done

cp data/watchful.service /lib/systemd/system/
cp data/watchful.timer /lib/systemd/system/

systemctl daemon-reload
systemctl enable watchful.timer
systemctl start watchful.timer