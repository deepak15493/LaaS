#!/bin/sh

create_client_servers_as_namespace()
{
    # cloning load balancers
    echo "starting server S11TEN${TENANT_ID}"
    sudo ip netns add S11TEN${TENANT_ID}
    
    echo "started cloning S12"
    sudo ip netns add S12TEN${TENANT_ID}
    
    echo "started cloning T11"
    sudo ip netns add T11TEN${TENANT_ID}
    
    echo "started cloning T12"
    sudo ip netns add T12TEN${TENANT_ID}
}
create_client_servers()
{
    # cloning load balancers
    echo "started cloning S11"
    sudo virt-clone --name S11 --original BASELB1 --auto-clone
    
    echo "started cloning S12"
    sudo virt-clone --name S12 --original BASELB1 --auto-clone
    
    echo "started cloning T11"
    sudo virt-clone --name T11 --original BASELB1 --auto-clone
    
    echo "started cloning T12"
    sudo virt-clone --name T12 --original BASELB1 --auto-clone

    # starting all load balancers
    echo "started S11"
    virsh start S11
    echo "started S12"
    virsh start S12
    echo "started T11"
    virsh start T11
    echo "started T12"
    virsh start T12
}



create_namespace()
{
    sudo ip netns add TEN${TENANT_ID}
    sudo ip netns add ${TENANT_ID}_NSLB11
    sudo ip netns add ${TENANT_ID}_EWLB11
}

create_veth_pair()
{
    echo "Creating 4 veth pairs"
    sudo ip link add ${TENANT_ID}_databr12veth0 type veth peer name ${TENANT_ID}_databr12veth1
    sudo ip link add ${TENANT_ID}_nslb11veth0 type veth peer name ${TENANT_ID}_nslb11veth1
    sudo ip link add ${TENANT_ID}_appbr11veth0 type veth peer name ${TENANT_ID}_appbr11veth1
    sudo ip link add ${TENANT_ID}_appbr13veth0 type veth peer name ${TENANT_ID}_appbr13veth1
    echo "done createing veth pairs"


    echo "Creating Veth pairs for servers"
    sudo ip link add s1br11${TENANT_ID} type veth peer name br11s1${TENANT_ID}
    sudo ip link add s1br13${TENANT_ID} type veth peer name br13s1${TENANT_ID}
    sudo ip link add s2br11${TENANT_ID} type veth peer name br11s2${TENANT_ID}
    sudo ip link add s2br13${TENANT_ID} type veth peer name br13s2${TENANT_ID}
    sudo ip link add t1br12${TENANT_ID} type veth peer name br12t1${TENANT_ID}
    sudo ip link add t2br12${TENANT_ID} type veth peer name br12t2${TENANT_ID}
    echo "done creating veth pairs for servers"

    echo "Creating Veth for TENANT - Hypervisor"
    sudo ip link add ten${TENANT_ID}veth0 type veth peer name ten${TENANT_ID}veth1
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
        echo " Creating veth for remote gre DNAT"
        sudo ip link add ten${TENANT_ID}greveth0 type veth peer name ten${TENANT_ID}greveth1
	
    fi

    echo "Done creating TENANT - Hypervisor veth"    
    echo "Turning interfaces up"
    sudo ip link set dev ${TENANT_ID}_databr12veth0 up
    sudo ip link set dev ${TENANT_ID}_nslb11veth0 up
    sudo ip link set dev ${TENANT_ID}_appbr11veth0 up
    sudo ip link set dev ${TENANT_ID}_appbr13veth0 up
    sudo ip link set dev ten${TENANT_ID}veth0 up
    sudo ip link set dev ten${TENANT_ID}veth1 up
    sudo ip link set dev s1br11${TENANT_ID} up
    sudo ip link set dev br11s1${TENANT_ID} up
    sudo ip link set dev s1br13${TENANT_ID} up
    sudo ip link set dev br13s1${TENANT_ID} up
    sudo ip link set dev s2br11${TENANT_ID} up
    sudo ip link set dev br11s2${TENANT_ID} up
    sudo ip link set dev s2br13${TENANT_ID} up
    sudo ip link set dev br13s2${TENANT_ID} up
    sudo ip link set dev t1br12${TENANT_ID} up
    sudo ip link set dev br12t1${TENANT_ID} up
    sudo ip link set dev t2br12${TENANT_ID} up
    sudo ip link set dev br12t2${TENANT_ID} up
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
        sudo ip link set dev ten${TENANT_ID}greveth1 up
    fi
    echo  "All interfaces are up"
}

create_networks()
{
    ## create br br11, br12, br13 with their networks
    echo "creating bridges with network"
    sudo brctl addbr ${TENANT_ID}_br11
    sudo brctl addbr ${TENANT_ID}_br12
    sudo brctl addbr ${TENANT_ID}_br13
    echo "bridge creation completed"
 
   
#    echo "defining 3 networks"
#    sudo virsh net-define /home/ece792/network11.xml
 #   sudo virsh net-define /home/ece792/network12.xml
 #   sudo virsh net-define /home/ece792/network13.xml
 #   echo "network defining completed"

 #   echo "starting networks"
 #   virsh net-start network11
 #   virsh net-start network12
 #   virsh net-start network13
 #   echo "Network creation completed"

    echo "turn on bridges"
    sudo ip link set dev ${TENANT_ID}_br11 up
    sudo ip link set dev ${TENANT_ID}_br12 up
    sudo ip link set dev ${TENANT_ID}_br13 up
    echo "done"
}

adding_veth_pairs_to_respective_interfaces()
{
    echo "adding veth pairs to respective interfaces"
    sudo ip link set ${TENANT_ID}_databr12veth1 netns ${TENANT_ID}_EWLB11
    sudo brctl addif ${TENANT_ID}_br12 ${TENANT_ID}_databr12veth0

    sudo ip link set ${TENANT_ID}_nslb11veth1 netns ${TENANT_ID}_NSLB11

    sudo ip link set ${TENANT_ID}_appbr11veth1 netns ${TENANT_ID}_NSLB11
    sudo brctl addif ${TENANT_ID}_br11 ${TENANT_ID}_appbr11veth0

    sudo ip link set ${TENANT_ID}_appbr13veth1 netns ${TENANT_ID}_EWLB11
    sudo brctl addif ${TENANT_ID}_br13 ${TENANT_ID}_appbr13veth0


    
    sudo ip link set ten${TENANT_ID}veth1 netns TEN${TENANT_ID}
    echo "Joining NSLB11 - TEN${TENANT_ID}"    
    sudo ip link set ${TENANT_ID}_nslb11veth0 netns TEN${TENANT_ID}
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
        sudo ip link set ten${TENANT_ID}greveth0 netns TEN${TENANT_ID}
    fi

    sudo ip link set s1br11${TENANT_ID} netns S11TEN${TENANT_ID}
    sudo brctl addif ${TENANT_ID}_br11 br11s1${TENANT_ID}
    sudo ip link set s1br13${TENANT_ID} netns S11TEN${TENANT_ID}
    sudo brctl addif ${TENANT_ID}_br13 br13s1${TENANT_ID}
    sudo ip link set s2br11${TENANT_ID} netns S12TEN${TENANT_ID}
    sudo brctl addif ${TENANT_ID}_br11 br11s2${TENANT_ID}
    sudo ip link set s2br13${TENANT_ID} netns S12TEN${TENANT_ID}
    sudo brctl addif ${TENANT_ID}_br13 br13s2${TENANT_ID}
    sudo ip link set t1br12${TENANT_ID} netns T11TEN${TENANT_ID}
    sudo brctl addif ${TENANT_ID}_br12 br12t1${TENANT_ID}
    sudo ip link set t2br12${TENANT_ID} netns T12TEN${TENANT_ID}
    sudo brctl addif ${TENANT_ID}_br12 br12t2${TENANT_ID}


    echo "done adding veth pairs to respective interfaces"
}

turing_on_vethpair_interfaces()
{
    sudo ip netns exec ${TENANT_ID}_EWLB11 ip link set dev ${TENANT_ID}_databr12veth1 up
    sudo ip netns exec ${TENANT_ID}_EWLB11 ip link set dev ${TENANT_ID}_appbr13veth1 up

    sudo ip netns exec ${TENANT_ID}_NSLB11 ip link set dev ${TENANT_ID}_nslb11veth1 up
    sudo ip netns exec ${TENANT_ID}_NSLB11 ip link set dev ${TENANT_ID}_appbr11veth1 up

    
    sudo ip netns exec S11TEN${TENANT_ID} ip link set dev s1br11${TENANT_ID} up
    sudo ip netns exec S11TEN${TENANT_ID} ip link set dev s1br13${TENANT_ID} up

    sudo ip netns exec S12TEN${TENANT_ID} ip link set dev s2br11${TENANT_ID} up
    sudo ip netns exec S12TEN${TENANT_ID} ip link set dev s2br13${TENANT_ID} up
    
    sudo ip netns exec T11TEN${TENANT_ID} ip link set dev t1br12${TENANT_ID} up
    sudo ip netns exec T12TEN${TENANT_ID} ip link set dev t2br12${TENANT_ID} up
    
    sudo ip netns exec TEN${TENANT_ID} ip link set dev ${TENANT_ID}_nslb11veth0 up
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
        sudo ip netns exec TEN${TENANT_ID} ip link set dev ten${TENANT_ID}greveth0 up
    fi
    sudo ip netns exec TEN${TENANT_ID} ip link set dev ten${TENANT_ID}veth1 up
}

assign_static_public_ips_and_iptables(){
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
	sudo ip netns exec TEN${TENANT_ID} ifconfig lo up
        sudo ip netns exec TEN${TENANT_ID} ip addr add 192.168.130.1/24 dev ${TENANT_ID}_nslb11veth0
        sudo ip netns exec ${TENANT_ID}_NSLB11 ip addr add 192.168.130.2/24 dev ${TENANT_ID}_nslb11veth1
        sudo ip netns exec TEN${TENANT_ID} ip addr add ${TENANT_PUBLIC_IP}/24 dev ten${TENANT_ID}veth1
        sudo ip addr add ${OTHER_END_TENANT_PUBLIC_IP}/24 dev ten${TENANT_ID}veth0
        sudo ip netns exec TEN${TENANT_ID} ip addr add ${TENANT_DNAT_PUBLIC_IP}/24 dev ten${TENANT_ID}greveth0
        sudo ip addr add ${OTHER_END_TENANT_DNAT_PUBLIC_IP}/24 dev ten${TENANT_ID}greveth1
        # GRE Remote route
	NETWORK_ID=`echo ${REMOTE_TENANT_PUBLIC_IP} | cut -f 1-3 -d '.' | xargs`
	NETWORK_ID=${NETWORK_ID}".0"
	sudo ip netns exec TEN${TENANT_ID} ip route add ${NETWORK_ID} via ${OTHER_END_TENANT_DNAT_PUBLIC_IP} dev ten${TENANT_ID}greveth0
        # route add 192.168.62.0/24 via 192.168.61.3 dev ten2greveth0
	#+ TENANT_PUBLIC_IP=192.168.60.2
	# OTHER_END_TENANT_PUBLIC_IP=192.168.60.3
	# VXLAN_ID=60
	# TENANT_DNAT_PUBLIC_IP=192.168.61.2
	# OTHER_END_TENANT_DNAT_PUBLIC_IP=192.168.61.3
	# REMOTE_TENANT_PUBLIC_IP=192.168.62.2
	# OTHER_END_REMOTE_TENANT_PUBLIC_IP=192.168.62.3
	#
	#sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -j DNAT --to-destination 192.168.130.2
    	sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I POSTROUTING  -d ${REMOTE_TENANT_PUBLIC_IP} -j SNAT --to ${TENANT_DNAT_PUBLIC_IP}
        sudo ip route add ${NETWORK_ID}/24 via ${TENANT_DNAT_PUBLIC_IP} dev gretun1 
    else
	sudo ip netns exec TEN${TENANT_ID} ifconfig lo up
        sudo ip netns exec TEN${TENANT_ID} ip addr add 192.168.135.1/24 dev ${TENANT_ID}_nslb11veth0
        sudo ip netns exec ${TENANT_ID}_NSLB11 ip addr add 192.168.135.2/24 dev ${TENANT_ID}_nslb11veth1
        sudo ip addr add ${OTHER_END_REMOTE_TENANT_PUBLIC_IP}/24 dev ten${TENANT_ID}veth0
        sudo ip netns exec TEN${TENANT_ID} ip addr add ${REMOTE_TENANT_PUBLIC_IP}/24 dev ten${TENANT_ID}veth1
	NETWORK_ID=`echo ${TENANT_DNAT_PUBLIC_IP} | cut -f 1-3 -d '.' | xargs`
	NETWORK_ID=${NETWORK_ID}".0"
	sudo ip netns exec TEN${TENANT_ID} ip route add ${NETWORK_ID} via ${OTHER_END_REMOTE_TENANT_PUBLIC_IP} dev ten${TENANT_ID}veth1
        sudo ip route add ${NETWORK_ID}/24 dev gretun1 
    fi
}

assign_static_ips_to_servers()
{
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
	sudo ip netns exec S11TEN${TENANT_ID} ip addr add 192.168.80.51/24 dev s1br11${TENANT_ID}
	sudo ip netns exec S12TEN${TENANT_ID} ip addr add 192.168.80.52/24 dev s2br11${TENANT_ID}

	sudo ip netns exec S11TEN${TENANT_ID} ip addr add 192.168.85.51/24 dev s1br13${TENANT_ID}
	sudo ip netns exec S12TEN${TENANT_ID} ip addr add 192.168.85.52/24 dev s2br13${TENANT_ID}

	sudo ip netns exec T11TEN${TENANT_ID} ip addr add 192.168.90.51/24 dev t1br12${TENANT_ID}
	sudo ip netns exec T12TEN${TENANT_ID} ip addr add 192.168.90.52/24 dev t2br12${TENANT_ID}
    else
	sudo ip netns exec S11TEN${TENANT_ID} ip addr add 192.168.80.53/24 dev s1br11${TENANT_ID}
	sudo ip netns exec S12TEN${TENANT_ID} ip addr add 192.168.80.54/24 dev s2br11${TENANT_ID}

	sudo ip netns exec S11TEN${TENANT_ID} ip addr add 192.168.85.53/24 dev s1br13${TENANT_ID}
	sudo ip netns exec S12TEN${TENANT_ID} ip addr add 192.168.85.54/24 dev s2br13${TENANT_ID}

	sudo ip netns exec T11TEN${TENANT_ID} ip addr add 192.168.90.53/24 dev t1br12${TENANT_ID}
	sudo ip netns exec T12TEN${TENANT_ID} ip addr add 192.168.90.54/24 dev t2br12${TENANT_ID}
    fi
}

assign_static_ips_to_lbs()
{
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
	echo "Assigning static ips to namespaces"
	#sudo ip addr add 192.168.130.1/24 dev ${TENANT_ID}_nslb11veth0
	sudo ip netns exec ${TENANT_ID}_NSLB11 ip addr add 192.168.130.2/24 dev ${TENANT_ID}_nslb11veth1

	sudo ip netns exec ${TENANT_ID}_NSLB11 ip addr add 192.168.80.2/24 dev ${TENANT_ID}_appbr11veth1

	sudo ip netns exec ${TENANT_ID}_EWLB11 ip addr add 192.168.85.2/24 dev ${TENANT_ID}_appbr13veth1
	sudo ip netns exec ${TENANT_ID}_EWLB11 ip addr add 192.168.90.2/24 dev ${TENANT_ID}_databr12veth1
	echo "Done assiging static ips to namespaces"
    else
	echo "Assigning static ips to namespaces"
	#sudo ip addr add 192.168.130.1/24 dev ${TENANT_ID}_nslb11veth0
	sudo ip netns exec ${TENANT_ID}_NSLB11 ip addr add 192.168.135.2/24 dev ${TENANT_ID}_nslb11veth1

	sudo ip netns exec ${TENANT_ID}_NSLB11 ip addr add 192.168.80.3/24 dev ${TENANT_ID}_appbr11veth1

	sudo ip netns exec ${TENANT_ID}_EWLB11 ip addr add 192.168.85.3/24 dev ${TENANT_ID}_appbr13veth1
	sudo ip netns exec ${TENANT_ID}_EWLB11 ip addr add 192.168.90.3/24 dev ${TENANT_ID}_databr12veth1
	echo "Done assiging static ips to namespaces"
	
    fi
}
# VXLAN ID is input ... ensure that this number is unique per hypervisor
# Each iteration uses 2 ID's. e.g 50 -> 50 and 51 is under use
creating_vxlan()
{
    echo "Creating vxlans"
    VXLAN_FRONTEND_ID=${VXLAN_ID}
    VXLAN_BACKEND_ID=$(expr ${VXLAN_ID} + 1)

    if [ "${HYPERVISOR_FLAG}" = "1" ];then
	sudo ip link add name ${TENANT_ID}_vxlanfrontend type vxlan id ${VXLAN_FRONTEND_ID} dev ens4 remote 192.168.149.3 dstport 4789

	sudo ip link add name ${TENANT_ID}_vxlanbackend type vxlan id ${VXLAN_BACKEND_ID} dev ens4 remote 192.168.149.3 dstport 4789
    else
	sudo ip link add name ${TENANT_ID}_vxlanfrontend type vxlan id ${VXLAN_FRONTEND_ID} dev ens4 remote 192.168.149.6 dstport 4789

	sudo ip link add name ${TENANT_ID}_vxlanbackend type vxlan id ${VXLAN_BACKEND_ID} dev ens4 remote 192.168.149.6 dstport 4789
    fi
    sudo ip link set dev ${TENANT_ID}_vxlanfrontend up
    sudo brctl addif ${TENANT_ID}_br11 ${TENANT_ID}_vxlanfrontend
    sudo ip link set dev ${TENANT_ID}_vxlanbackend up
    sudo brctl addif ${TENANT_ID}_br12 ${TENANT_ID}_vxlanbackend
    echo "done Creating vxlans"
}



create_gre()
{
    echo "create gre tunnel "
    sudo ip tunnel add grehypervisor mode gre local 192.168.149.6 remote 192.168.149.3
    sudo ip link set dev grehypervisor up
    sudo ip route add 192.168.135.0/24 dev grehypervisor
    echo "Done creating gre tunnel "
}

adding_icmp_masquerade_rules_to_lbs11(){
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
        sudo ip netns exec ${TENANT_ID}_NSLB11 ip route add default via 192.168.130.1
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.130.2 -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.80.51
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.130.2 -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.80.52
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.130.2 -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.80.53
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.130.2 -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.80.54
    else
        sudo ip netns exec ${TENANT_ID}_NSLB11 ip route add default via 192.168.135.1
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.135.2 -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.80.51
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.135.2 -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.80.52
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.135.2 -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.80.53
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_nslb11veth1 -d 192.168.135.2 -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.80.54
    fi
}

adding_tcp_masquerade_rules_to_lbs11(){
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
        sudo ip netns exec ${TENANT_ID}_NSLB11 ip route add default via 192.168.130.1
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_nslb11veth1 -d 192.168.130.2 -m state --state NEW -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.80.51
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_nslb11veth1 -d 192.168.130.2 -m state --state NEW -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.80.52
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_nslb11veth1 -d 192.168.130.2 -m state --state NEW -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.80.53
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_nslb11veth1 -d 192.168.130.2 -m state --state NEW -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.80.54
    else
        sudo ip netns exec ${TENANT_ID}_NSLB11 ip route add default via 192.168.135.1
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_nslb11veth1 -d 192.168.135.2 -m state --state NEW  -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.80.51
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_nslb11veth1 -d 192.168.135.2 -m state --state NEW -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.80.52
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_nslb11veth1 -d 192.168.135.2 -m state --state NEW -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.80.53
        sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_nslb11veth1 -d 192.168.135.2 -m state --state NEW -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.80.54
    fi
}

adding_masquerade_rules_to_lbs11()
{
    adding_icmp_masquerade_rules_to_lbs11
    adding_tcp_masquerade_rules_to_lbs11
    sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I POSTROUTING  ! -s 192.168.80.0/24 -j MASQUERADE
    sudo ip netns exec ${TENANT_ID}_NSLB11 iptables -t nat -I POSTROUTING  -s 192.168.80.0/24  -j MASQUERADE
}

adding_filter_rules_to_tenant_namespace(){
#    iptables -I INPUT -s 198.51.100.0 -j DROP
    echo "Filter rules to be added in future" 

}

adding_icmp_masquerade_rules_to_tenant_namespace(){
     if [ "${HYPERVISOR_FLAG}" = "1" ];then
        sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 0 -j DNAT --to-destination 192.168.130.2

        sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m statistic --mode nth --every 2 --packet 1 -j DNAT --to-destination ${REMOTE_TENANT_PUBLIC_IP}
    else
        sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p icmp -i ten${TENANT_ID}veth1 -d ${REMOTE_TENANT_PUBLIC_IP} -j DNAT --to-destination 192.168.135.2
   
    fi
}

adding_tcp_masquerade_rules_to_tenant_namespace(){
     if [ "${HYPERVISOR_FLAG}" = "1" ];then
        sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p tcp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m state --state NEW -m statistic --mode nth --every 2 --packet 0 -j DNAT --to-destination 192.168.130.2

        sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p tcp -i ten${TENANT_ID}veth1 -d ${TENANT_PUBLIC_IP} -m state --state NEW -m statistic --mode nth --every 2 --packet 1 -j DNAT --to-destination ${REMOTE_TENANT_PUBLIC_IP}
    else
        sudo ip netns exec TEN${TENANT_ID} iptables -t nat -I PREROUTING -p tcp -i ten${TENANT_ID}veth1 -d ${REMOTE_TENANT_PUBLIC_IP} -m state --state NEW -j DNAT --to-destination 192.168.135.2
   
    fi
}

adding_masquerade_rules_to_tenant_namespace(){
    adding_icmp_masquerade_rules_to_tenant_namespace
    adding_tcp_masquerade_rules_to_tenant_namespace
}

adding_icmp_masquerade_rules_to_eslb11(){
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.2 -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.90.51
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.2 -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.90.52
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.2 -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.90.53
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.2 -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.90.54
    else
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.3 -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.90.51
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.3 -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.90.52
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.3 -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.90.53
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p icmp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.3 -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.90.54
    fi
}

adding_tcp_masquerade_rules_to_eslb11(){
    if [ "${HYPERVISOR_FLAG}" = "1" ];then
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.2  -m state --state NEW -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.90.51
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.2  -m state --state NEW -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.90.52
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.2  -m state --state NEW -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.90.53
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.2  -m state --state NEW -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.90.54
    else
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.3  -m state --state NEW -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.90.51
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.3  -m state --state NEW -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.90.52
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.3  -m state --state NEW -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.90.53
        sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I PREROUTING -p tcp -i ${TENANT_ID}_appbr13veth1 -d 192.168.85.3  -m state --state NEW -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.90.54
    fi
}

adding_masquerade_rules_to_eslb11()
{
    adding_icmp_masquerade_rules_to_eslb11
    adding_tcp_masquerade_rules_to_eslb11
    sudo ip netns exec ${TENANT_ID}_EWLB11 iptables -t nat -I POSTROUTING  -s 192.168.85.0/24 -j MASQUERADE
}

# TODO 
# 1. Create Servers as namespace
# 2. Create veth for servers and attach them
# 3. Create wrapper namespace
# 4. Create veth pairs for wrapper - hypervisor , wrapper - NSLB1
# 5. Edit old veth names with tenant id in name
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
	echo "VXLAN_ID parameter is missing"
	exit 1
fi
if [ -z "$6" ];then
	echo "TENANT_DNAT_PUBLIC_IP parameter is missing"
	exit 1
fi
if [ -z "$7" ];then
	echo "OTHER_END_TENANT_DNAT_PUBLIC_IP parameter is missing"
	exit 1
fi
HYPERVISOR_FLAG=$1
TENANT_ID=$2
TENANT_PUBLIC_IP=$3
OTHER_END_TENANT_PUBLIC_IP=$4
VXLAN_ID=$5
TENANT_DNAT_PUBLIC_IP=$6
OTHER_END_TENANT_DNAT_PUBLIC_IP=$7
REMOTE_TENANT_PUBLIC_IP=$8
OTHER_END_REMOTE_TENANT_PUBLIC_IP=$9
create_client_servers_as_namespace
#create_client_servers
create_namespace
create_veth_pair
create_networks
adding_veth_pairs_to_respective_interfaces
turing_on_vethpair_interfaces
assign_static_ips_to_lbs
assign_static_ips_to_servers
assign_static_public_ips_and_iptables
creating_vxlan
adding_masquerade_rules_to_lbs11
adding_masquerade_rules_to_eslb11
adding_masquerade_rules_to_tenant_namespace
adding_filter_rules_to_tenant_namespace
