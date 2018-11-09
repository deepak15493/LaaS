#!/bin/bash

total_customer_ip(){

    customer_vms=$1
    customer_count=0
    for vm in ${customer_vms}
    do
        customer_count=$(expr ${customer_count} + 1) 
    done

    return ${customer_count}
}


apply_iptable(){

    customer_vms=$1
    total_customer_ip "${customer_vms}"
    customer_count=$?
    customer_itr=0

    IPV4_FORWARD_FILE="/proc/sys/net/ipv4/ip_forward"
    # Disable IPTABLES forwarding flag

    echo 0 > ${IPV4_FORWARD_FILE} 
    # IPTABLE rules
    for customer_ip in ${customer_vms} 
    do
        iptables -t nat -I PREROUTING -p tcp -d ${customer_ip} --dport 80 -m state --state NEW -m statistic --mode nth --every ${customer_count} --packet ${customer_itr} -j DNAT --to-destination ${customer_ip} 
        customer_itr=$(expr ${customer_itr} + 1 ) 
    done

    # Enable IPTABLES forwarding flag
    echo 1 > ${IPV4_FORWARD_FILE} 

}


remove_iptable(){

    
    IPV4_FORWARD_FILE="/proc/sys/net/ipv4/ip_forward"
    # Disable IPTABLES forwarding flag

    echo 0 > ${IPV4_FORWARD_FILE} 

    # IPTABLE rules flush all 
    iptables -F PREROUTING -tnat


    # Enable IPTABLES forwarding flag
    echo 1 > ${IPV4_FORWARD_FILE} 
}

validate_ip(){
    return 0
}

ACTION=$1

# MAIN SCRIPT 

if [ -z ${ACTION} ];then
    echo "No ACTION [ APPLY / DELETE ] found"
    exit 1
fi

# Check if the IP ADDRESS is valid 
CUSTOMER_VM_FILE="/tmp/customer_vms.txt"
if [ ! -f ${CUSTOMER_VM_FILE} ];then
    echo " No customer vm file ${CUSTOMER_VM_FILE} present"
    exit 1
fi
customer_vms=""
while IFS='' read -r line || [[ -n "$line" ]]; do
    customer_vms="${customer_vms} "${line}
done < ${CUSTOMER_VM_FILE}
if [ -z "${customer_vms}" ];then
    echo " No customer VMs to apply DNAT rules"
    exit 1
fi


remove_iptable "${customer_vms}"

apply_iptable "${customer_vms}"


echo " HANDLE IPTABLES complete"
exit 0;


