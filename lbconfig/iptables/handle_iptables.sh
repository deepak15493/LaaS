#!/bin/bash

delete_new_northsouth_namespace(){
    NEW_NAMESPACE=`sudo ip netns list | grep "${TENANT_ID}-" | cut -f 1 -d ' ' | xargs`
    if [ "${NEW_NAMESPACE}" = "" ];then
	echo "No Namespace ${TENANT_ID}_NEW_NSLB11 found.. Skipping delete"
	return
    fi

    sudo ip netns del ${NEW_NAMESPACE} 
    
}

add_new_northsouth_namespace(){
    
    NEW_NAMESPACE=`sudo ip netns list | grep "${TENANT_ID}-" | cut -f 1 -d ' ' | xargs`
    if [ "${NEW_NAMESPACE}" != "" ];then
	echo "Namespace ${TENANT_ID}-NSLB11 already present.. Skipping create"
	return
    fi

    sudo ip netns add ${TENANT_ID}-NSLB11
}

del_new_veth_pairs(){
    sudo ip link del ${TENANT_ID}-BR11NSLB11
    sudo ip netns exec TEN${TENANT_ID} ip link del ${TENANT_ID}-TEN${TENANT_ID}NSLB11
    sudo ip netns exec ${TENANT_ID}-NSLB11 ip link del ${TENANT_ID}-NSLB11TEN${TENANT_ID}
    sudo ip netns exec ${TENANT_ID}-NSLB11 ip link del ${TENANT_ID}-NSLB11BR11
    
}

set_veth_to_namespaces(){
    sudo ip link set ${TENANT_ID}-TEN${TENANT_ID}NSLB11 netns TEN${TENANT_ID}
    sudo ip link set ${TENANT_ID}-NSLB11TEN${TENANT_ID} netns ${TENANT_ID}-NSLB11
    sudo ip link set ${TENANT_ID}-NSLB11BR11 netns ${TENANT_ID}-NSLB11
    sudo brctl addif ${TENANT_ID}_br11 ${TENANT_ID}-BR11NSLB11
}

set_veth_interface_up(){
    sudo ip netns exec TEN${TENANT_ID} ip link set dev ${TENANT_ID}-TEN${TENANT_ID}NSLB11 up 
    sudo ip netns exec ${TENANT_ID}-NSLB11 ip link set dev ${TENANT_ID}-NSLB11TEN${TENANT_ID} up 

    sudo ip netns exec ${TENANT_ID}-NSLB11 ip link set dev ${TENANT_ID}-NSLB11BR11 up
    sudo ip link set dev ${TENANT_ID}-BR11NSLB11 up
}

add_new_static_ips(){
        sudo ip netns exec TEN${TENANT_ID} ip addr add 192.168.131.1/24 dev ${TENANT_ID}-TEN${TENANT_ID}NSLB11
        sudo ip netns exec ${TENANT_ID}-NSLB11 ip addr add 192.168.131.2/24 dev ${TENANT_ID}-NSLB11TEN${TENANT_ID}
        sudo ip netns exec ${TENANT_ID}-NSLB11 ip addr add 192.168.80.12/24 dev ${TENANT_ID}-NSLB11BR11
}

add_new_veth_pairs(){

    echo "Creating NEW_NSLB11 - TENANT veth pairs"
    sudo ip link add ${TENANT_ID}-NSLB11TEN${TENANT_ID} type veth peer name ${TENANT_ID}-TEN${TENANT_ID}NSLB11
    
    echo "Creating NEW_NSLB11 - BR11 veth pairs"
    sudo ip link add ${TENANT_ID}-NSLB11BR11 type veth peer name ${TENANT_ID}-BR11NSLB11

}

cron_apply_iptable(){
    NEW_NAMESPACE=`sudo ip netns list | grep "${TENANT_ID}-"  | cut -f 1 -d ' ' | xargs`

    if [ "${NEW_NAMESPACE}" = "" ];then
		# Applying rules for increasing to 2 NSLB's
		
		sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 3 --packet 0 -j DNAT --to-destination 192.168.130.2

		sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 3 --packet 1 -j DNAT --to-destination 192.168.131.2
		
		sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 3 --packet 2 -j DNAT --to-destination ${REMOTE_TENANT_PUBLIC_IP}
    else
		# Applying rules for 1 decreasing to 1 NSLB
		sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 0 -j DNAT --to-destination 192.168.130.2

		sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 1 -j DNAT --to-destination ${REMOTE_TENANT_PUBLIC_IP}
    
    fi
}


apply_iptable_new_northsouth_namespace(){
    NEW_NAMESPACE=`sudo ip netns list | grep "${TENANT_ID}-" | cut -f 1 -d ' ' | xargs`

    if [ "${NEW_NAMESPACE}" = "" ];then
        return
    fi

    NSLB_S11="192.168.80.51"
    NSLB_S12="192.168.80.52"
    NSLB_S13="192.168.80.53"
    NSLB_S14="192.168.80.54"

    sudo ip netns exec ${NEW_NAMESPACE} ip route add default via 192.168.131.1
    sudo ip netns exec ${NEW_NAMESPACE} iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.131.2 -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.80.51
    sudo ip netns exec ${NEW_NAMESPACE} iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.131.2 -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.80.52
    sudo ip netns exec ${NEW_NAMESPACE} iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.131.2 -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.80.53
    sudo ip netns exec ${NEW_NAMESPACE} iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.131.2 -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.80.54 
}

apply_iptable_tenant_namespace(){
    NEW_NAMESPACE=`sudo ip netns list | grep "${TENANT_ID}-"`

    if [ "${NEW_NAMESPACE}" != "" ];then
		# Applying rules for increasing to 2 NSLB's
		
		sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 3 --packet 0 -j DNAT --to-destination 192.168.130.2

		sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 3 --packet 1 -j DNAT --to-destination 192.168.131.2
		
		sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 3 --packet 2 -j DNAT --to-destination ${REMOTE_TENANT_PUBLIC_IP}
    else
		# Applying rules for 1 decreasing to 1 NSLB
		sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 0 -j DNAT --to-destination 192.168.130.2

		sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 1 -j DNAT --to-destination ${REMOTE_TENANT_PUBLIC_IP}
    
    fi
}


remove_iptable(){

    # Disable IPTABLES forwarding flag


    # IPTABLE rules flush all 
    sudo ip netns exec TEN${TENANT_ID} iptables -F PREROUTING -tnat


    # Enable IPTABLES forwarding flag
}

validate_ip(){
    return 0
}


##MAIN starts here

if [ -z "$1" ];then
	echo " TENANT ID parameter is missing"
        exit 1
fi

if [ -z "$2" ];then
	echo " ACTION [ 1 / 2 ] parameter is missing"
	exit 1
fi
TENANT_ID=$1
ACTION=$2
TENANT_PUBLIC_IP=$3
REMOTE_TENANT_PUBLIC_IP=$4

TENANT_NAMESPACE=TEN${TENANT_ID}

# MAIN SCRIPT 

if [ "$2" = "1" ];then
    ## Path to increase load balancer
    delete_new_northsouth_namespace
    del_new_veth_pairs
    remove_iptable 
   
    add_new_northsouth_namespace
    add_new_veth_pairs
    set_veth_to_namespaces 
    add_new_static_ips
    set_veth_interface_up

    apply_iptable_tenant_namespace 
    apply_iptable_new_northsouth_namespace
elif [ "$2" = "2" ];then
    ## Path to restore load balancer
    delete_new_northsouth_namespace
    del_new_veth_pairs
    remove_iptable 
    
    apply_iptable_tenant_namespace 
else
    ## Cron is calling to just change the IP tables

    ## Donot create anything but delete the NAT over GRE Tunnel
    cron_apply_iptable 
fi

exit 0;
