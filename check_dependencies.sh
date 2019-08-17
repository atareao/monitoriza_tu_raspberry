#!/bin/bash -x
for i in $(cat dependencies.txt)
do
    if [ $(dpkg-query -W -f='${Status}' "$i" 2>/dev/null | grep -c "ok installed") -ne 1 ];
	then
		echo "$i is not installed. I'm going to install"
		sudo apt install -y $i
	fi
done
