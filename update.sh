#!/bin/bash
if [ "$(id -u)" != "0" ]; then
    echo "Sorry, you are not root."
    exit 1
fi

systemctl stop watchful.timer

rm -f '/etc/watchful/status.json'
rm -rf '/opt/watchful'
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
  EXTTMP=`date +%Y%m%d%H%M%S`
  PATH_DEST="/etc/watchful/${NAMEFILE}"
  if [[ ! -f "$PATH_DEST" ]]; then
    cp $f ${PATH_DEST}
  else
    echo "Info: File (${NAMEFILE}) exists, the new configuration will be copied with the name(${NAMEFILE}.${EXTTMP})."
    cp $f ${PATH_DEST}.${EXTTMP}
  fi
done

systemctl start watchful.timer
