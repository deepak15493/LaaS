#!/bin/bash

#### dependent on INPUT parameters 
#### Hypervisor_flag , GRE_LOCAL_IP , GRE_REMOTE_IP
create_gre(){ 
   if [ "${HYPERVISOR_FLAG}" = "1" ];then
	sudo ip tunnel add gretun1 mode gre local ${GRE_LOCAL_IP} remote ${GRE_REMOTE_IP}
	sudo ip link set dev gretun1 up
   else
	sudo ip tunnel add gretun1 mode gre local ${GRE_REMOTE_IP} remote ${GRE_LOCAL_IP}
	sudo ip link set dev gretun1 up
   fi
}


### MAIN starts here
HYPERVISOR_FLAG=$1
GRE_LOCAL_IP=$2
GRE_REMOTE_IP=$3
create_gre
