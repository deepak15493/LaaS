#!/bin/sh

create_lbs()
{
    # cloning load balancers
    echo "started cloning S21"
    sudo virt-clone --name S21 --original BASELB1 --auto-clone
    
    echo "started cloning S22"
    sudo virt-clone --name S22 --original BASELB1 --auto-clone
    
    echo "started cloning T21"
    sudo virt-clone --name T21 --original BASELB1 --auto-clone
    
    echo "started cloning T22"
    sudo virt-clone --name T22 --original BASELB1 --auto-clone

    # starting all load balancers
    echo "started S21"
    virsh start S21
    echo "started S22"
    virsh start S22
    echo "started T21"
    virsh start T21
    echo "started T22"
    virsh start T22
}



create_namespace()
{
    sudo ip netns add NSLB22
    sudo ip netns add EWLB22
}

create_veth_pair()
{
    echo "Creating 4 veth pairs"
    sudo ip link add databr22veth0 type veth peer name databr22veth1
    sudo ip link add nslb22veth0 type veth peer name nslb22veth1
    sudo ip link add appbr21veth0 type veth peer name appbr21veth1
    sudo ip link add appbr23veth0 type veth peer name appbr23veth1
    echo "done createing veth pairs"

    echo "Turning interfaces up"
    sudo ip link set dev databr22veth0 up
    sudo ip link set dev nslb22veth0 up
    sudo ip link set dev appbr21veth0 up
    sudo ip link set dev appbr23veth0 up
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
    sudo ip link set databr22veth1 netns EWLB22
    sudo brctl addif br12 databr22veth0

    sudo ip link set nslb22veth1 netns NSLB22

    sudo ip link set appbr21veth1 netns NSLB22
    sudo brctl addif br11 appbr21veth0

    sudo ip link set appbr23veth1 netns EWLB22
    sudo brctl addif br13 appbr23veth0
    echo "done adding veth pairs to respective interfaces"
}

turing_on_vethpair_interfaces()
{
    sudo ip netns exec EWLB22 ip link set dev databr22veth1 up
    sudo ip netns exec EWLB22 ip link set dev appbr23veth1 up

    sudo ip netns exec NSLB22 ip link set dev nslb22veth1 up
    sudo ip netns exec NSLB22 ip link set dev appbr21veth1 up
}


assign_static_ips_to_lbs()
{
    echo "Assigning static ips to namespaces"
    sudo ip addr add 192.168.135.1/24 dev nslb22veth0
    sudo ip netns exec NSLB22 ip addr add 192.168.135.2/24 dev nslb22veth1

    sudo ip netns exec NSLB22 ip addr add 192.168.80.3/24 dev appbr21veth1

    sudo ip netns exec EWLB22 ip addr add 192.168.95.2/24 dev appbr23veth1
    sudo ip netns exec EWLB22 ip addr add 192.168.90.3/24 dev databr22veth1
    echo "Done assiging static ips to namespaces"
}

creating_vxlan()
{
    echo "Creating vxlans"
    sudo ip link add name vxlanfrontend type vxlan id 47 dev ens4 remote 192.168.149.6 dstport 4789
    sudo ip link set dev vxlanfrontend up
    sudo brctl addif br11 vxlanfrontend

    sudo ip link add name vxlanbackend type vxlan id 48 dev ens4 remote 192.168.149.6 dstport 4789
    sudo ip link set dev vxlanbackend up
    sudo brctl addif br12 vxlanbackend
    echo "done Creating vxlans"
}


create_gre()
{
    echo "create gre tunnel "
    sudo ip tunnel add grehypervisor mode gre local 192.168.149.3 remote 192.168.149.6
    sudo ip link set dev grehypervisor up
    sudo ip route add 192.168.130.0/24 dev grehypervisor
    echo "Done creating gre tunnel "
}

adding_masquerade_rules_to_lbs22()
{
    sudo ip netns exec NSLB22 ip route add default via 192.168.135.1

    sudo ip netns exec NSLB22 iptables -t nat -I PREROUTING -p icmp -i nslb22veth1 -d 192.168.135.2 -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.80.51
    sudo ip netns exec NSLB22 iptables -t nat -I PREROUTING -p icmp -i nslb22veth1 -d 192.168.135.2 -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.80.52
    sudo ip netns exec NSLB22 iptables -t nat -I PREROUTING -p icmp -i nslb22veth1 -d 192.168.135.2 -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.80.53
    sudo ip netns exec NSLB22 iptables -t nat -I PREROUTING -p icmp -i nslb22veth1 -d 192.168.135.2 -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.80.54

    sudo ip netns exec NSLB22 iptables -t nat -I POSTROUTING  ! -s 192.168.80.0/24 -j MASQUERADE
    sudo ip netns exec NSLB22 iptables -t nat -I POSTROUTING  -s 192.168.80.0/24  -j MASQUERADE
}

adding_masquerade_rules_to_eslb22()
{
    sudo ip netns exec EWLB22 iptables -t nat -I PREROUTING -p icmp -i appbr23veth1 -d 192.168.95.2 -m statistic --mode nth --every 4 --packet 0 -j DNAT --to-destination 192.168.90.51
    sudo ip netns exec EWLB22 iptables -t nat -I PREROUTING -p icmp -i appbr23veth1 -d 192.168.95.2 -m statistic --mode nth --every 4 --packet 1 -j DNAT --to-destination 192.168.90.52
    sudo ip netns exec EWLB22 iptables -t nat -I PREROUTING -p icmp -i appbr23veth1 -d 192.168.95.2 -m statistic --mode nth --every 4 --packet 2 -j DNAT --to-destination 192.168.90.53
    sudo ip netns exec EWLB22 iptables -t nat -I PREROUTING -p icmp -i appbr23veth1 -d 192.168.95.2 -m statistic --mode nth --every 4 --packet 3 -j DNAT --to-destination 192.168.90.54

    sudo ip netns exec EWLB22 iptables -t nat -I POSTROUTING  -s 192.168.95.0/24 -j MASQUERADE
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
adding_masquerade_rules_to_lbs22
adding_masquerade_rules_to_eslb22
