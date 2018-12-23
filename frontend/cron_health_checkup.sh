#!/bin/bash
mins=1
if [ -z $1 ];then
        echo "Path for script [ cron_health_checkup.sh ] not present"
        exit 1
fi
if [ -z $2 ];then
        echo "Tenant ID is not present"
        exit 1
fi
if [ -z $3 ];then
        echo "Local public IP is not present"
        exit 1
fi
if [ -z $4 ];then
        echo "Remote public IP is not present"
        exit 1
fi
SCRIPT_PATH=$1
TENANT_ID=$2
LOCAL_PUBLIC_IP=$3
REMOTE_PUBLIC_IP=$4
echo "SHELL=/bin/sh" > mycron
echo "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin" >> mycron
crontab -l >> mycron 1>/dev/null 2>/dev/null
health_checkup_present=`cat mycron | grep cron_health_checkup.sh`
echo "*/${mins} * * * * /bin/python ${SCRIPT_PATH}/sahil_health.py ${TENANT_ID} ${LOCAL_PUBLIC_IP} ${REMOTE_PUBLIC_IP}" >> mycron

crontab mycron
rm -f mycron

