# Monitorize your Raspberry Pi

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/22be071ac81842888561769423f492e8)](https://app.codacy.com/app/vsc55/monitoriza_tu_raspberry?utm_source=github.com&utm_medium=referral&utm_content=vsc55/monitoriza_tu_raspberry&utm_campaign=Badge_Grade_Dashboard)


## Requirements
* `python3-requests`
* `python3-pymysql`
* `python3-paramiko >= 2.5 (version 2.4 da errores CryptographyDeprecationWarning)`

## Install:
```
$ cd /usr/src
$ git clone https://github.com/atareao/monitoriza_tu_raspberry.git
$ cd monitoriza_tu_raspberry
$ chmod +x *.sh
$ sudo ./install.sh
```

## Update:
```
$ cd /usr/src/monitoriza_tu_raspberry
$ git pull
$ chmod +x *.sh
$ sudo ./update.sh
```

## Uninstall:
```
$ cd /usr/src/monitoriza_tu_raspberry
$ sudo ./uninstall.sh
```

* Note: If no parameter is specified "/etc/watchful" is not erased. If you want a full uninstall must add the "-a" parameter.
* Note: on uninstall, dependencies aren't removed. **You must remove by hand**.
