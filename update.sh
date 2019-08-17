#!/bin/bash
if [ "$(id -u)" != "0" ]; then
	echo "Sorry, you are not root."
	exit 1
fi
source check_dependencies.sh
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
	cp -r ${f} /opt/watchful
done
for f in data/*.json
do
	NAMEFILE=${f#"data/"}
	PATH_DEST="/etc/watchful/${NAMEFILE}"
	CHEKC=${PATH_DEST}
	CHEKC_ULTIMA=${PATH_DEST}
	COUNT=0
	while true; do
		if [[ ! -f "${CHEKC}" ]]; then
			break
		fi
		let COUNT+=1
		CHEKC="${PATH_DEST}.${COUNT}"
	done
	if [[ "${PATH_DEST}" != "${CHEKC}" ]]; then
		if [[ ${COUNT} > 1 ]]; then
			let COUNT-=1
			CHEKC_ULTIMA="${PATH_DEST}.${COUNT}"
		fi
		if [[ $(diff "${CHEKC_ULTIMA}" "${f}") ]]; then
			cp ${f} ${CHEKC}
		fi
	fi
done

cp data/watchful.service /lib/systemd/system/
cp data/watchful.timer /lib/systemd/system/

systemctl daemon-reload
systemctl enable watchful.timer
systemctl start watchful.timer
