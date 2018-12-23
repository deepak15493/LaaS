#!/bin/bash


add_new_northsouth_namespace(){
	 #echo "starting load balncer  ${TENANT_ID}_NSLB11"
    sudo docker run --privileged -itd --name ${TENANT_ID}_NSLB13 ubuntu:final 
    DOCKER_CONTAINER_PID=`sudo docker inspect -f '{{.State.Pid}}' ${TENANT_ID}_NSLB13 | xargs `
    sudo ln -s /proc/${DOCKER_CONTAINER_PID}/ns/net /var/run/netns/${TENANT_ID}_NSLB13
}

add_new_veth_pairs(){
    echo "Creating ${TENANT_ID}_NSLB13 - BR11 veth pairs"
    sudo ip link add ${TENANT_ID}_br11_NSLB13 type veth peer name ${TENANT_ID}_NSLB13_br11
    sudo ip link add ten${TENANT_ID}_nslb13 type veth peer name nslb13_ten${TENANT_ID}	
}

set_veth_to_namespaces(){
    sudo ip link set ${TENANT_ID}_NSLB13_br11  netns ${TENANT_ID}_NSLB13
    sudo brctl addif ${TENANT_ID}_br11 ${TENANT_ID}_br11_NSLB13

    sudo ip link set nslb13_ten${TENANT_ID}  netns ${TENANT_ID}_NSLB13
    sudo ip link set ten${TENANT_ID}_nslb13 netns TEN${TENANT_ID}

}
set_veth_interface_up(){
	sudo ip link set ${TENANT_ID}_br11_NSLB13 up
	sudo ip netns exec ${TENANT_ID}_NSLB13 ip link set ${TENANT_ID}_NSLB13_br11 up
	sudo ip netns exec ${TENANT_ID}_NSLB13 ip link set nslb13_ten${TENANT_ID} up
	sudo ip netns exec TEN${TENANT_ID} ip link set ten${TENANT_ID}_nslb13 up
}


add_new_static_ips(){
        sudo ip netns exec TEN${TENANT_ID} ip addr add 192.168.131.1/24 dev ten${TENANT_ID}_nslb13
        sudo ip netns exec ${TENANT_ID}_NSLB13 ip addr add 192.168.131.2/24 dev nslb13_ten${TENANT_ID} 
        sudo ip netns exec ${TENANT_ID}_NSLB13 ip addr add 192.168.80.12/24 dev ${TENANT_ID}_NSLB13_br11 
  	sudo ip netns exec ${TENANT_ID}_NSLB13 iptables -t nat -I POSTROUTING  ! -s 192.168.80.0/24 -j MASQUERADE
        sudo ip netns exec ${TENANT_ID}_NSLB13 iptables -t nat -I POSTROUTING  -s 192.168.80.0/24  -j MASQUERADE
	sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I POSTROUTING -d 192.168.131.2 -j MASQUERADE
}




apply_icmp_iptable_new_northsouth_namespace(){
    sudo ip netns exec ${TENANT_ID}_NSLB13 iptables -t nat -I PREROUTING -p icmp -i nslb13_ten${TENANT_ID} -d 192.168.131.2 -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.80.51
    sudo ip netns exec ${TENANT_ID}_NSLB13 iptables -t nat -I PREROUTING -p icmp -i nslb13_ten${TENANT_ID} -d 192.168.131.2 -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.80.52
    sudo ip netns exec ${TENANT_ID}_NSLB13 iptables -t nat -I PREROUTING -p icmp -i nslb13_ten${TENANT_ID} -d 192.168.131.2 -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.80.53
    sudo ip netns exec ${TENANT_ID}_NSLB13 iptables -t nat -I PREROUTING -p icmp -i nslb13_ten${TENANT_ID} -d 192.168.131.2 -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.80.54 
}

apply_tcp_iptable_new_northsouth_namespace(){
    sudo ip netns exec ${TENANT_ID}_NSLB13 iptables -t nat -I PREROUTING -p tcp -i nslb13_ten${TENANT_ID} -d 192.168.131.2 -m state --state NEW -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.80.51
    sudo ip netns exec ${TENANT_ID}_NSLB13 iptables -t nat -I PREROUTING -p tcp -i nslb13_ten${TENANT_ID} -d 192.168.131.2 -m state --state NEW -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.80.52
    sudo ip netns exec ${TENANT_ID}_NSLB13 iptables -t nat -I PREROUTING -p tcp -i nslb13_ten${TENANT_ID} -d 192.168.131.2 -m state --state NEW -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.80.53
    sudo ip netns exec ${TENANT_ID}_NSLB13 iptables -t nat -I PREROUTING -p tcp -i nslb13_ten${TENANT_ID} -d 192.168.131.2 -m state --state NEW -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.80.54 
}

apply_icmp_iptable_tenant_namespace(){
	sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 0 -j DNAT --to-destination 192.168.131.2

	sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 1 -j DNAT --to-destination ${REMOTE_TENANT_PUBLIC_IP}
    
}

apply_tcp_iptable_tenant_namespace(){
	sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p tcp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m state --state NEW -m statistic --mode nth --every 2 --packet 0 -j DNAT --to-destination 192.168.131.2

	sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p tcp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m state --state NEW -m statistic --mode nth --every 2 --packet 1 -j DNAT --to-destination ${REMOTE_TENANT_PUBLIC_IP}
}


remove_iptable(){
    sudo ip netns exec TEN${TENANT_ID} iptables -F PREROUTING -tnat
}



##MAIN starts here

if [ -z "$1" ];then
	echo " TENANT ID parameter is missing"
        exit 1
fi
if [ -z "$2" ];then
	echo "Tenant public ip  parameter is missing"
        exit 1
fi
if [ -z "$3" ];then
	echo "Tenant remote public ip  parameter is missing"
        exit 1
fi

TENANT_ID=$1
TENANT_PUBLIC_IP=$2
REMOTE_TENANT_PUBLIC_IP=$3

# MAIN SCRIPT 
remove_iptable
add_new_northsouth_namespace
add_new_veth_pairs
set_veth_to_namespaces
set_veth_interface_up
add_new_static_ips
apply_icmp_iptable_new_northsouth_namespace
apply_tcp_iptable_new_northsouth_namespace
apply_icmp_iptable_tenant_namespace
apply_tcp_iptable_tenant_namespace
