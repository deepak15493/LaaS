destroy_lbs()
{
    echo "Destroying all lbs"
#    virsh destroy S11
 #   virsh destroy S12
  #  virsh destroy T11
   # virsh destroy T12

    echo "Undefining all lbs"
  #  virsh undefine S11  --remove-all-storage
  #  virsh undefine S12  --remove-all-storage
  #  virsh undefine T11  --remove-all-storage
  #  virsh undefine T12  --remove-all-storage
    sudo ip netns del TEN${TENANT_ID}
    sudo ip netns del S11TEN${TENANT_ID}
    sudo ip netns del S12TEN${TENANT_ID}
    sudo ip netns del T11TEN${TENANT_ID}
    sudo ip netns del T12TEN${TENANT_ID}
}

destroy_networks()
{
   virsh net-destroy network11 
   virsh net-destroy network12
   virsh net-destroy network13

   virsh net-undefine network11
   virsh net-undefine network12
   virsh net-undefine network13
   
   sudo ip link set dev ${TENANT_ID}_br11 down
   sudo ip link set dev ${TENANT_ID}_br12 down
   sudo ip link set dev ${TENANT_ID}_br13 down

   sudo brctl delbr ${TENANT_ID}_br11
   sudo brctl delbr ${TENANT_ID}_br12
   sudo brctl delbr ${TENANT_ID}_br13
}

destroy_name_spaces()
{
    sudo ip netns del ${TENANT_ID}_NSLB11
    sudo ip netns del ${TENANT_ID}_EWLB11
}

destroy_veth_pairs()
{
    sudo ip link del ${TENANT_ID}_databr12veth0
    sudo ip link del ${TENANT_ID}_nslb11veth0 
    sudo ip link del ${TENANT_ID}_appbr11veth0
    sudo ip link del ${TENANT_ID}_appbr13veth0 
    sudo ip link del s1br11${TENANT_ID} 
    sudo ip link del s1br13${TENANT_ID}
    sudo ip link del s2br11${TENANT_ID} 
    sudo ip link del s2br13${TENANT_ID} 
    sudo ip link del t1br12${TENANT_ID}
    sudo ip link del t2br12${TENANT_ID}
    sudo ip link del br11s1${TENANT_ID} 
    sudo ip link del br13s1${TENANT_ID}
    sudo ip link del br11s2${TENANT_ID} 
    sudo ip link del br13s2${TENANT_ID} 
    sudo ip link del br12t1${TENANT_ID}
    sudo ip link del br12t2${TENANT_ID}
    sudo ip link del ten${TENANT_ID}veth0 
    sudo ip link del ten${TENANT_ID}greveth0
    sudo ip link del ten${TENANT_ID}greveth1
}


destroy_vxlan(){
	sudo ip link del ${TENANT_ID}_vxlanfrontend 
	sudo ip link del ${TENANT_ID}_vxlanbackend 
	
}

if [ -z "$1" ];then
	echo "Tenant ID parameter is missing"
	exit 1
fi

TENANT_ID=$1
destroy_lbs
destroy_networks
destroy_veth_pairs
destroy_name_spaces
destroy_vxlan

#sudo ip link del gretun1
