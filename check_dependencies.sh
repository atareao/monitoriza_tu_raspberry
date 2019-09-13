#!/bin/bash -x
for i in $(cat dependencies.txt)
do
    if [[ $i =~ ";" ]]; then
        arrSplit=(${i//;/ })
        pkg_name=${arrSplit[0]}
        deb_url=${arrSplit[1]}
        deb_file=${deb_url##*/}
        tmp_file="/tmp/$deb_file"
    else
        pkg_name=$(echo $i | tr -d '\r')
        deb_url=""
    fi

    if [[ $(dpkg-query -W -f='${Status}' "$pkg_name" 2>/dev/null | grep -c "ok installed") -ne 1 ]]; then
	    echo -e "${pkg_name} is not installed. I'm going to install"
        if [[ "$deb_url" = "" ]]; then
            echo sudo apt install -y $pkg_name
        else
            echo wget -q --show-progress "$deb_url" -O "$tmp_file"
#            echo curl --progress-bar "$deb_url" > "$tmp_file"
            echo sudo apt install -y "$tmp_file"
            if [[ -f "$tmp_file" ]]; then
                echo rm -f "$tmp_file"
            fi
        fi
	fi
done
