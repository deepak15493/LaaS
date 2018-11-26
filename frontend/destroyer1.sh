destroy_lbs()
{
    echo "Destroying all lbs"
    virsh destroy S11
    virsh destroy S12
    virsh destroy T11
    virsh destroy T12

    echo "Undefining all lbs"
    virsh undefine S11  --remove-all-storage
    virsh undefine S12  --remove-all-storage
    virsh undefine T11  --remove-all-storage
    virsh undefine T12  --remove-all-storage
}

destroy_networks()
{
   virsh net-destroy network11 
   virsh net-destroy network12
   virsh net-destroy network13

   virsh net-undefine network11
   virsh net-undefine network12
   virsh net-undefine network13
   
   sudo ip link set dev br11 down
   sudo ip link set dev br12 down
   sudo ip link set dev br13 down

   sudo brctl delbr br11
   sudo brctl delbr br12
   sudo brctl delbr br13
}

destroy_name_spaces()
{
    sudo ip netns del NSLB11
    sudo ip netns del EWLB11
}

destroy_veth_pairs()
{
    sudo ip link del databr12veth0 type veth peer name databr12veth1
    sudo ip link del nslb11veth0 type veth peer name nslb11veth1
    sudo ip link del appbr11veth0 type veth peer name appbr11veth1
    sudo ip link del appbr13veth0 type veth peer name appbr13veth1
}

destroy_lbs
destroy_networks
destroy_veth_pairs
destroy_name_spaces
