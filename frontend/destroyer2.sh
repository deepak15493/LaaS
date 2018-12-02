destroy_lbs()
{
    echo "Destroying all lbs"
    virsh destroy S21
    virsh destroy S22
    virsh destroy T21
    virsh destroy T22

    echo "Undefining all lbs"
    virsh undefine S21  --remove-all-storage
    virsh undefine S22  --remove-all-storage
    virsh undefine T21  --remove-all-storage
    virsh undefine T22  --remove-all-storage
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
    sudo ip netns del NSLB22
    sudo ip netns del EWLB22
}

destroy_veth_pairs()
{
    sudo ip link del databr22veth0 type veth peer name databr22veth1
    sudo ip link del nslb22veth0 type veth peer name nslb22veth1
    sudo ip link del appbr21veth0 type veth peer name appbr21veth1
    sudo ip link del appbr23veth0 type veth peer name appbr23veth1
}

destroy_lbs
destroy_networks
destroy_veth_pairs
destroy_name_spaces
