#!/bin/sh

create_lbs()
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
    sudo ip netns add NSLB11
    sudo ip netns add EWLB11
}

create_veth_pair()
{
    echo "Creating 4 veth pairs"
    sudo ip link add databr12veth0 type veth peer name databr12veth1
    sudo ip link add nslb11veth0 type veth peer name nslb11veth1
    sudo ip link add appbr11veth0 type veth peer name appbr11veth1
    sudo ip link add appbr13veth0 type veth peer name appbr13veth1
    echo "done createing veth pairs"

    echo "Turning interfaces up"
    sudo ip link set dev databr12veth0 up
    sudo ip link set dev nslb11veth0 up
    sudo ip link set dev appbr11veth0 up
    sudo ip link set dev appbr13veth0 up
    echo  "All interfaces are up"
}

create_networks()
{
    ## create br br11, br12, br13 with their networks
    echo "creating bridges with network"
    sudo brctl addbr br11
    sudo brctl addbr br12
    sudo brctl addbr br13
    echo "bridge creation completed"
    
    echo "defining 3 networks"
    sudo virsh net-define /home/ece792/network11.xml
    sudo virsh net-define /home/ece792/network12.xml
    sudo virsh net-define /home/ece792/network13.xml
    echo "network defining completed"

    echo "starting networks"
    virsh net-start network11
    virsh net-start network12
    virsh net-start network13
    echo "Network creation completed"

    echo "turn on bridges"
    sudo ip link set dev br11 up
    sudo ip link set dev br12 up
    sudo ip link set dev br13 up
    echo "done"
}

adding_veth_pairs_to_respective_interfaces()
{
    echo "adding veth pairs to respective interfaces"
    sudo ip link set databr12veth1 netns EWLB11
    sudo brctl addif br12 databr12veth0

    sudo ip link set nslb11veth1 netns NSLB11

    sudo ip link set appbr11veth1 netns NSLB11
    sudo brctl addif br11 appbr11veth0

    sudo ip link set appbr13veth1 netns EWLB11
    sudo brctl addif br13 appbr13veth0
    echo "done adding veth pairs to respective interfaces"
}

turing_on_vethpair_interfaces()
{
    sudo ip netns exec EWLB11 ip link set dev databr12veth1 up
    sudo ip netns exec EWLB11 ip link set dev appbr13veth1 up

    sudo ip netns exec NSLB11 ip link set dev nslb11veth1 up
    sudo ip netns exec NSLB11 ip link set dev appbr11veth1 up
}


assign_static_ips_to_lbs()
{
    echo "Assigning static ips to namespaces"
    sudo ip addr add 192.168.130.1/24 dev nslb11veth0
    sudo ip netns exec NSLB11 ip addr add 192.168.130.2/24 dev nslb11veth1

    sudo ip netns exec NSLB11 ip addr add 192.168.80.2/24 dev appbr11veth1

    sudo ip netns exec EWLB11 ip addr add 192.168.85.2/24 dev appbr13veth1
    sudo ip netns exec EWLB11 ip addr add 192.168.90.2/24 dev databr12veth1
    echo "Done assiging static ips to namespaces"
}

creating_vxlan()
{
    echo "Creating vxlans"
    sudo ip link add name vxlanfrontend type vxlan id 47 dev ens4 remote 192.168.149.3 dstport 4789
    sudo ip link set dev vxlanfrontend up
    sudo brctl addif br11 vxlanfrontend

    sudo ip link add name vxlanbackend type vxlan id 48 dev ens4 remote 192.168.149.3 dstport 4789
    sudo ip link set dev vxlanbackend up
    sudo brctl addif br12 vxlanbackend
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

adding_masquerade_rules_to_lbs11()
{
    sudo ip netns exec NSLB11 ip route add default via 192.168.130.1

    sudo ip netns exec NSLB11 iptables -t nat -I PREROUTING -p icmp -i nslb11veth1 -d 192.168.130.2 -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.80.51
    sudo ip netns exec NSLB11 iptables -t nat -I PREROUTING -p icmp -i nslb11veth1 -d 192.168.130.2 -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.80.52
    sudo ip netns exec NSLB11 iptables -t nat -I PREROUTING -p icmp -i nslb11veth1 -d 192.168.130.2 -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.80.53
    sudo ip netns exec NSLB11 iptables -t nat -I PREROUTING -p icmp -i nslb11veth1 -d 192.168.130.2 -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.80.54

    sudo ip netns exec NSLB11 iptables -t nat -I POSTROUTING  ! -s 192.168.80.0/24 -j MASQUERADE
    sudo ip netns exec NSLB11 iptables -t nat -I POSTROUTING  -s 192.168.80.0/24  -j MASQUERADE
}

adding_masquerade_rules_to_eslb11()
{
    sudo ip netns exec EWLB11 iptables -t nat -I PREROUTING -p icmp -i appbr13veth1 -d 192.168.85.2 -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.90.51
    sudo ip netns exec EWLB11 iptables -t nat -I PREROUTING -p icmp -i appbr13veth1 -d 192.168.85.2 -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.90.52
    sudo ip netns exec EWLB11 iptables -t nat -I PREROUTING -p icmp -i appbr13veth1 -d 192.168.85.2 -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.90.53
    sudo ip netns exec EWLB11 iptables -t nat -I PREROUTING -p icmp -i appbr13veth1 -d 192.168.85.2 -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.90.54

    sudo ip netns exec EWLB11 iptables -t nat -I POSTROUTING  -s 192.168.85.0/24 -j MASQUERADE
}


create_lbs
create_gre
create_namespace
create_veth_pair
create_networks
adding_veth_pairs_to_respective_interfaces
turing_on_vethpair_interfaces
assign_static_ips_to_lbs
creating_vxlan
adding_masquerade_rules_to_lbs11
adding_masquerade_rules_to_eslb11
