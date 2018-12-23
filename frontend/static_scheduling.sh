#!/bin/bash

stop_second_lb() {
    sudo ip netns exec TEN${TENANT_ID} iptables -L PREROUTING -w -tnat  > /tmp/tmpfile.txt
    DYNAMIC_PRESENT=`cat /tmp/tmpfile.txt | grep "192.168.131.2"`
    rm -f /tmp/tmpfile.txt
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
	sudo ip netns exec TEN${TENANT_ID} iptables -F PREROUTING -w -tnat
	if [ "${DYNAMIC_PRESENT}" = "" ];then
	    sudo ip netns exec TEN${TENANT_ID} iptables -w -t nat -I PREROUTING -p tcp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m state --state NEW  -j DNAT --to-destination 192.168.130.2
	    sudo ip netns exec TEN${TENANT_ID} iptables -w -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP}  -j DNAT --to-destination 192.168.130.2
     	else
	    sudo ip netns exec TEN${TENANT_ID} iptables -w -t nat -I PREROUTING -p tcp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m state --state NEW  -j DNAT --to-destination 192.168.131.2
	    sudo ip netns exec TEN${TENANT_ID} iptables -w -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP}  -j DNAT --to-destination 192.168.131.2
	fi
    fi
}

start_second_lb() {
    sudo ip netns exec TEN${TENANT_ID} iptables -L PREROUTING -w -tnat  > /tmp/tmpfile.txt
    DYNAMIC_PRESENT=`cat /tmp/tmpfile.txt | grep "192.168.131.2"`
    rm -f /tmp/tmpfile.txt
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
        sudo ip netns exec TEN${TENANT_ID} iptables -F PREROUTING -w -tnat
	if [ "${DYNAMIC_PRESENT}" = "" ];then
            sudo ip netns exec TEN${TENANT_ID} iptables -w -t nat -I PREROUTING -p tcp -m state --state NEW  -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 0 -j DNAT --to-destination 192.168.130.2
	    sudo ip netns exec TEN${TENANT_ID} iptables -w -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 0  -j DNAT --to-destination 192.168.130.2
	else
            sudo ip netns exec TEN${TENANT_ID} iptables -w -t nat -I PREROUTING -p tcp -m state --state NEW  -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 0 -j DNAT --to-destination 192.168.131.2
	    sudo ip netns exec TEN${TENANT_ID} iptables -w -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 0  -j DNAT --to-destination 192.168.131.2
	fi
        sudo ip netns exec TEN${TENANT_ID} iptables -w -t nat -I PREROUTING -p tcp -m state --state NEW -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 1 -j DNAT --to-destination ${REMOTE_TENANT_PUBLIC_IP}
        sudo ip netns exec TEN${TENANT_ID} iptables -w -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 1 -j DNAT --to-destination ${REMOTE_TENANT_PUBLIC_IP}
    fi

}

if [ -z "$1" ];then
        echo "Hypervisor flag [ 1 / 2 ] parameter is missing"
        exit 1
fi
if [ -z "$2" ];then
        echo "Tenant ID parameter is missing"
        exit 1
fi

if [ -z "$3" ];then
        echo "Tenant Public IP parameter is missing"
        exit 1
fi

if [ -z "$4" ];then
        echo "Tenant Other end Public IP is missing"
        exit 1
fi
if [ -z "$5" ];then
        echo "Action flag [ APPLY / REMOVE ] parameter is missing"
        exit 1
fi


HYPERVISOR_FLAG=$1
TENANT_ID=$2
TENANT_PUBLIC_IP=$3
REMOTE_TENANT_PUBLIC_IP=$4
ACTION=$5
if [ "${ACTION}" = "APPLY" ];then
    start_second_lb
else
    stop_second_lb
fi
