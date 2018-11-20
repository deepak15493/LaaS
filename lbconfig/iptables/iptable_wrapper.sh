#!/bin/bash

CUSTOMER_VM_FILE="/tmp/customer_vms.txt"
#while [ 1 ]
#do
#	sleep 1
if [ ! -f ${CUSTOMER_VM_FILE} ];then
	continue
fi
#	echo " Sleep done"
bash /tmp/handle_iptables.sh APPLY	

#done
