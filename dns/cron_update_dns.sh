#!/bin/bash
mins=2
hrs=12
if [ -z $1 ];then
	echo "Path for script [ update_dns_entry.sh ] not present"
	exit 1
fi
SCRIPT_PATH=$1
echo "SHELL=/bin/sh" > mycron
echo "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin" >> mycron
crontab -l >> mycron 1>/dev/null 2>/dev/null
update_dns_present=`cat mycron | grep update_dns_entry.sh`
echo "*/${mins} */${hrs} * * * /bin/bash ${SCRIPT_PATH}/update_dns_entry.sh" >> mycron

crontab mycron
rm -f mycron
