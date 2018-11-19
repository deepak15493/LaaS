import  os
import paramiko
import csv
import libvirt
import time
from collections import defaultdict
 
#listOfAWSServers = []
listOfNCServersIP = []
#listOfLB = []
#load balancer common credentials
lbUserName = ''
lbPassword = ''
listOfHypervisor1LBs = []
listOfHypervisor2LBs = []
mapOfHypervisorToServer = {} 

dictOfNCLBIps= {}
dictOfNCLBDefaultMac= {}


dictOfNCServerIps = {}
dictOfNCServerDefaultMac = {}

ipOfHypervisor1 = ''
userNameOfHypervisor1 = ''
passwordOfHypervisor1 = ''


ipOfHypervisor2 = ''
userNameOfHypervisor2 = ''
passwordOfHypervisor2 = ''

def initialize():
    print ("Initializing")
    #initialize lb credentials
    global listOfHypervisor1LBs, listOfHypervisor2LBs, lbUserName, lbPassword, mapOfHypervisorToServer
    lbUserName = 'root'
    lbPassword = 'tushar123'

    listOfHypervisor1LBs = ['LB401', 'LB402'] 
    listOfHypervisor2LBs = [ 'LB501','LB502']
    
    getInputsFromUser()
    ### setting up network
    createCustomerNetwork()
    createManagementNetwork()
 
    ### creating tunnels for both Mangement and data flow   
    createTunnelsForManagementAndDataFlow()

    ### assigning static ip to Front end vm
    assignStaticIpToManagementVM()
    ### create 4 load balancers in AWS
    # createAWSLoadBalancers()
    
    ### create 4 NC load balancers
    #handleCreationOfNCLoadBalancers( )
    
    ### get default ips of all load balancers
    #collectIpsForLBs()
    
    ### attach load balancers to vxlan network
    #attachLBsToVxlanNetwork()
    
    #collectIpsForLBs() 
    ### assign static ips to just created load balancers vxlan interfaces
    #assignStaticIPToLB() 

    ### create Servers according to requirement
    #createServersInrespectiveHypervisor()

    ### get default ips of all servers
    #collectIpsForServers()

    ## attach server to data network
    #attachServersToNetwork()

    ### assign static ips to just created servers vxlan interfaces
    #assignStaticIPToServer()

    ### write LBs and their ips to file
    #writeLBsAndTheirIPsToFile()
    
    ####  writing server ips to file 
    #writeServerIpsfile();   
   
    ### push server name file to all lbs 	
    #transferFileToLB()

    #doLoadBalncingONLBVMs()



def doLoadBalncingONLBVMs():
	global dictOfNCLBIps, lbPassword, lbUserName, listOfHypervisor1LBs, listOfHypervisor2LBs
        listOfAllLBs = listOfHypervisor1LBs + listOfHypervisor2LBs

        staticDictForLBIps = {}
        staticDictForLBIps['LB101'] = '192.168.98.27'
        staticDictForLBIps['LB102'] = '192.168.98.26'
        staticDictForLBIps['LB201'] = '192.168.98.25'
        staticDictForLBIps['LB202'] = '192.168.98.24'
        for lbName in listOfAllLBs:
                if(lbName in staticDictForLBIps):
			ssh = getSshInstanceFromParamiko(staticDictForLBIps[lbName], 'root', 'tushar123')
			command_to_execute_handle_iptable = 'bash /tmp/handle_iptable.sh'
			ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_execute_handle_iptable)
			print(ssh_stdout.readlines())			
			command_to_execute_iptables_wrapper = 'bash /tmp/iptable_wrapper.sh'
			ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_execute_iptables_wrapper)
                        print(ssh_stdout.readlines())

def assignStaticIPToServer():
	global dictOfNCServerIps, lbPassword, lbUserName 
        global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
        global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
	
	currentWorkingDirectory = os.getcwd()
	destDirectory = '/tmp'
	staticIPScript = "assignStaticIpToServer.py"
	### Copy script on hypervisor 
	cpFileToVM(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, currentWorkingDirectory, destDirectory, staticIPScript ) 
		
	cpFileToVM(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, currentWorkingDirectory, destDirectory, staticIPScript ) 


    	ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)

	### give file executing permission
	command_to_change_permission = 'chmod 777 /tmp/'+ staticIPScript
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
	print(ssh_stdout.readlines())

	### Run script on Hypervisor [ Assigns static IP on Load Balancer VM's customer and management network ]
	command_to_run_static_ip_script = 'python /tmp/' + staticIPScript + ' ' 
	input_static_ip_script = "SERVER110,SERVER111" + " " + dictOfNCServerIps["SERVER110"] + "," + dictOfNCServerIps["SERVER111"] + " 1" 

	command_to_run_static_ip_script += input_static_ip_script
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_static_ip_script)
	print(ssh_stdout.readlines())
	ssh.close()


	### Run script on Hypervisor [ Assigns static IP on Load Balancer VM's customer and management network ]
    	ssh = getSshInstanceFromParamiko(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)

 	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
        print(ssh_stdout.readlines())

	command_to_run_static_ip_script = 'python /tmp/' + staticIPScript + ' ' 
	input_static_ip_script = "SERVER220,SERVER221" + " " + dictOfNCServerIps["SERVER220"] + "," + dictOfNCServerIps["SERVER221"] + " 2" 
	command_to_run_static_ip_script += input_static_ip_script
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_static_ip_script)
	print(ssh_stdout.readlines())
	ssh.close()



def collectIpsForServers():
    global  dictOfNCLBDefaultMac, ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2


    uri1 = 'qemu+ssh://'+userNameOfHypervisor1+'@'+ ipOfHypervisor1 + ':22/system'
    uri2 = 'qemu+ssh://'+userNameOfHypervisor2+'@'+ ipOfHypervisor2 + ':22/system'
    tries1 = 5
    tries2 = 5
    while( tries1 > 0):
        getIpsFromNCServers(uri1)
        if('SERVER110' in dictOfNCServerIps and 'SERVER111' in dictOfNCServerIps and 'SERVER110' in dictOfNCServerDefaultMac and 'SERVER111' in dictOfNCServerDefaultMac ):
                break
        tries1 -= 1

    while( tries2 > 0):
        getIpsFromNCServers(uri2)
	if('SERVER220' in dictOfNCServerIps and 'SERVER221' in dictOfNCServerIps and 'SERVER220' in dictOfNCServerDefaultMac and 'SERVER221' in dictOfNCServerDefaultMac ):                
		break
        tries2 -= 1
    return




def attachServersToNetwork():
    global mapOfHypervisorToServer
    listOfServersInHypervisor1 = []
    listOfServersInHypervisor2 = [] 

    if('hypervisor1' in mapOfHypervisorToServer):
	for count in range(0, mapOfHypervisorToServer['hypervisor1']):
		nameOfServer = 'SERVER11'+ str(count)
		listOfServersInHypervisor1.append(nameOfServer)
    	attachHypervisorServers(ipOfHypervisor1,userNameOfHypervisor1, passwordOfHypervisor1, listOfServersInHypervisor1,'vxlan201' )
    	  

    if('hypervisor2' in mapOfHypervisorToServer):
	for count in range(0, mapOfHypervisorToServer['hypervisor2']):
		nameOfServer = 'SERVER22' + str(count)
		listOfServersInHypervisor2.append(nameOfServer)
 	attachHypervisorServers(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfServersInHypervisor2,'vxlan201')
    


def attachHypervisorServers(ipaddr, username, password, listOfServers, networkName):
    for nameOfServer in listOfServers:
	detachHypervisorServer(ipaddr, username, password, listOfServers, 'default')

    # get Instance of ssh from paramiko
    ssh  = getSshInstanceFromParamiko(ipaddr, username, password)

    for nameOfServer in listOfServers:
        command_to_attach_iface = 'virsh attach-interface --domain '+ nameOfServer + ' --type network --source '+ networkName +' --model virtio --config --live'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_attach_iface)
        print(ssh_stdout.read(), ssh_stderr.read())

    time.sleep(1)

    for nameOfServer in listOfServers:
        command_to_attach_iface = 'virsh attach-interface --domain '+ nameOfServer + ' --type network --source default --model virtio --config --live'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_attach_iface)
        print(ssh_stdout.read(), ssh_stderr.read())

    ssh.close()
    return

def getIpsFromNCServers(connectionURI):
        global dictOfNCServerIps, dictOfNCServerDefaultMac
        conn = libvirt.open(connectionURI)
        domains = conn.listAllDomains()
        for domain in domains:
                if(domain.name().startswith( 'SERVER' )):
                     ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
                     if(bool(ifaces)):
                             key, value = ifaces.popitem()
                             if 'addrs' in value:
                                     dictOfNCServerIps[domain.name()] = value['addrs'][0]['addr']
                             if 'hwaddr' in value:
                                     dictOfNCServerDefaultMac[domain.name()] = value['hwaddr']

        print("printing the dict of load balancer name to ips")
        for k, v in dictOfNCServerIps.iteritems():
                print k , v
        print("printing the dict of load balancer name to macs")
        for k, v in dictOfNCServerDefaultMac.iteritems():
                print k , v
        time.sleep(15)
        conn.close()	

def createServersInrespectiveHypervisor():
    global mapOfHypervisorToServer, ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2

    # get instance of ssh from paramiko
    ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)
    if('hypervisor1' in mapOfHypervisorToServer):
    	for count in range(0, mapOfHypervisorToServer['hypervisor1']):
       		nameOfServer = 'SERVER11'+ str(count)
		createServerInHypervisor(nameOfServer, ssh)
    ssh.close()

    # get instance of ssh from paramiko
    ssh = getSshInstanceFromParamiko(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)
    if('hypervisor2' in mapOfHypervisorToServer):
    	for count in range(0, mapOfHypervisorToServer['hypervisor2']):
       		nameOfServer = 'SERVER22'+ str(count)
		createServerInHypervisor(nameOfServer, ssh)
    ssh.close()
    return    

def createServerInHypervisor(nameOfServer, ssh): 
    command_to_clone_server = 'virt-clone --original BASELB1 --name ' + nameOfServer + ' --auto-clone'
    command_to_start_server = 'virsh start ' + nameOfServer 
    #destroyLBsIfExistsInHypervisor(ssh)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_clone_server)
    print(ssh_stdout.readlines())
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_start_server)
    print(ssh_stdout.readlines())
    time.sleep(10)
    print ( nameOfServer + " started succesfully.")
    return


def collectIpsForLBs():
    global  dictOfNCLBDefaultMac, ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2    


    uri1 = 'qemu+ssh://'+userNameOfHypervisor1+'@'+ ipOfHypervisor1 + ':22/system'
    uri2 = 'qemu+ssh://'+userNameOfHypervisor2+'@'+ ipOfHypervisor2 + ':22/system'
    tries1 = 5
    tries2 = 5
    while( tries1 > 0): 
    	getIpsFromNCHypervisor(uri1)
    	if('LB401' in dictOfNCLBIps and 'LB402' in dictOfNCLBIps and 'LB401' in dictOfNCLBDefaultMac and 'LB402' in dictOfNCLBDefaultMac ):
		break
	tries1 -= 1
    
    while( tries2 > 0): 
   	getIpsFromNCHypervisor(uri2)
    	if('LB501' in dictOfNCLBIps and 'LB502' in dictOfNCLBIps and 'LB501' in dictOfNCLBDefaultMac and 'LB502' in dictOfNCLBDefaultMac ):
                break
        tries2 -= 1	
    return



def attachLBsToVxlanNetwork():
    global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2 
    global listOfHypervisor1LBs, listOfHypervisor2LBs
 
    ### Detach default network
    detachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1LBs, 'default')
    detachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2LBs, 'default')
 
    ### attach data network of vxlan 
    attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1LBs, 'vxlan200')
    attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2LBs, 'vxlan200')
    
    ### attach management network of vxlan
    attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1LBs, 'vxlan201')
    attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2LBs, 'vxlan201')

    ## attach default network 
    attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1LBs, 'default')
    attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2LBs, 'default')
	
    return

def detachHypervisorServer(ipaddr, username, password, listOfHyperviserServers, networkName):
    global dictOfNCServerDefaultMac
    # get Instance of ssh from paramiko
    ssh  = getSshInstanceFromParamiko(ipaddr, username, password)
 
    for nameOfServer in listOfHyperviserServers:
    	command_to_attach_iface = 'virsh detach-interface --domain '+ nameOfServer + ' --type network --mac ' + dictOfNCServerDefaultMac[nameOfServer]	
    	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_attach_iface)
    	print(ssh_stdout.read())
    time.sleep(1)
    ssh.close()
    return

def detachHypervisorLBs(ipaddr, username, password, listOfHyperviserLBs, networkName):
    global dictOfNCLBDefaultMac
    # get Instance of ssh from paramiko
    ssh  = getSshInstanceFromParamiko(ipaddr, username, password)
 
    for LBName in listOfHyperviserLBs:
    	command_to_attach_iface = 'virsh detach-interface --domain '+ LBName + ' --type network --mac ' + dictOfNCLBDefaultMac[LBName]	
    	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_attach_iface)
    	print(ssh_stdout.read(), ssh_stderr.read())
    time.sleep(1)
    ssh.close()
    return

def attachHypervisorLBs(ipaddr, username, password, listOfHyperviserLBs, networkName):
    # get Instance of ssh from paramiko
    ssh  = getSshInstanceFromParamiko(ipaddr, username, password)
 
    for LBName in listOfHyperviserLBs:
    	command_to_attach_iface = 'virsh attach-interface --domain '+ LBName + ' --type network --source '+ networkName +' --model virtio --config --live'
    	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_attach_iface)
    	print(ssh_stdout.read(), ssh_stderr.read())
    time.sleep(1) 
    ssh.close()
    return

def handleCreationOfNCLoadBalancers():
    global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
 
    listOfLBInHypervisor1 = ['LB401', 'LB402']
    listOfLBInHypervisor2 = ['LB501', 'LB502']
    ## create lbs in hypervisor 1
    createNCLoadBalancers(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfLBInHypervisor1)
    ## create lbs in hypervisor 2 
    createNCLoadBalancers(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfLBInHypervisor2)

def attachStaticInterfaceToManagementVM(ipaddr, username, password, networkName):
    ssh  = getSshInstanceFromParamiko(ipaddr, username, password)
    LBName = "testing"
    print("Attaching management network to front end vm")
    command_to_attach_iface = 'virsh attach-interface --domain '+ LBName + ' --type network --source '+ networkName +' --model virtio --config --live'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_attach_iface)
    ssh_stdout.readlines()
    ssh.close()
    return

def assignStaticIpToManagementVM():
    print "waiting to get interface up for current front end vm"
    time.sleep(10)
    os.system('ip addr add 192.168.111.70/24 dev eth1')


def createTunnelsForManagementAndDataFlow():
    global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
 
    ## creating tunnel for data flow
    createTunnelInHypervisor( ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1,'vxlanbr200', 'vxlan200', '52', ipOfHypervisor2 )
    createTunnelInHypervisor( ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, 'vxlanbr200', 'vxlan200', '52', ipOfHypervisor1)

    ## creating tunnel for management of lbs
    createTunnelInHypervisor( ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1,'vxlanbr201', 'vxlan201', '53',ipOfHypervisor2)
    createTunnelInHypervisor( ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, 'vxlanbr201', 'vxlan201', '53', ipOfHypervisor1)

    attachStaticInterfaceToManagementVM(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, 'vxlan201')

def getIpsFromNCHypervisor(connectionURI):
	global dictOfNCLBIps, dictOfNCLBDefaultMac 
	conn = libvirt.open(connectionURI)
	domainIDs = conn.listDomainsID()
	#domains = conn.listDomains()
        for domainID in domainIDs:
		domain = conn.lookupByID(domainID)
                if(domain.name().startswith( 'LB' )):
                     ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
                     if(bool(ifaces)):
                             key, value = ifaces.popitem()
                             if 'addrs' in value:
                                     dictOfNCLBIps[domain.name()] = value['addrs'][0]['addr']
		             if 'hwaddr' in value:	
                                     dictOfNCLBDefaultMac[domain.name()] = value['hwaddr']
				
	print("printing the dict of load balancer name to ips")
        for k, v in dictOfNCLBIps.iteritems():
                print k , v
	print("printing the dict of load balancer name to macs")
        for k, v in dictOfNCLBDefaultMac.iteritems():
                print k , v
	time.sleep(15)
	conn.close()

def setAWSServerList():
    print("YET TO BE IMPLEMENTED")
    return


def getServerList():
    print("YET TO BE IMPLEMENTED")
    return


def createAWSLoadBalancers():
    print("YET TO BE IMPLEMENTED")
    return

def createBridgeNetworkInHypervisor(ipOfHypervisor, usernameOfHypervisor, passwordOfHypervisor, bridgeName, fileName, networkName):
    ssh = getSshInstanceFromParamiko(ipOfHypervisor, usernameOfHypervisor, passwordOfHypervisor)
    #write vxlan.xml in /home/ece792

    # details for copying file 
    currentWorkingDirectory = os.getcwd()
    destDirectory = '/home/ece792' 
    fileName = fileName
    cpFileToVM(ipOfHypervisor, usernameOfHypervisor, passwordOfHypervisor, currentWorkingDirectory, destDirectory, fileName )

    print "Waiting 1 secs after copying network.xml file to hypervisor"
    # wait for scp to finish
    time.sleep(1)

    # add bridge to hypervisor 
    command_to_create_bridge = 'sudo -S brctl addbr ' + bridgeName           #vxlanbr1
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_create_bridge)
    ssh_stdin.write( passwordOfHypervisor +'\n')
    ssh_stdin.flush()
    ssh_stdout.readlines()

    # turn bridge iface up
    command_to_turn_vxlanbr1_iface_up = 'sudo -S ip link set dev '+ bridgeName+' up'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_turn_vxlanbr1_iface_up)
    ssh_stdin.write( passwordOfHypervisor +'\n')
    ssh_stdin.flush()
    ssh_stdout.readlines()

    #create network  
    command_to_define_network = 'virsh net-define /home/ece792/' + fileName
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_define_network)
    ssh_stdout.readlines()

    #start network 
    command_to_start_network = 'virsh net-start '+ networkName
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_start_network)
    ssh_stdout.readlines()

    #close connection hypervisor	
    ssh.close()

def createCustomerNetwork():
    global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
 
    bridgeNameForNetwork1 = 'vxlanbr200'
    fileNameForNetwork1 = 'vxlan200.xml'
    networkName1 = 'vxlan200'
    
    print("Creating bridge in hypervisor1 for data tunnel ")
    #create network in hypervisor1
    createBridgeNetworkInHypervisor(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, bridgeNameForNetwork1, fileNameForNetwork1, networkName1)
    #create network in hypervisor2
    print("Creating bridge in hypervisor2 for data tunnel ")
    createBridgeNetworkInHypervisor(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, bridgeNameForNetwork1, fileNameForNetwork1, networkName1)

def createManagementNetwork():
    global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2

    bridgeNameForNetwork2 = 'vxlanbr201'
    fileNameForNetwork2 = 'vxlan201.xml'
    networkName2 = 'vxlan201'
    print("Creating bridge in hypervisor1 for management tunnel ")
     #create network in hypervisor1
    createBridgeNetworkInHypervisor(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, bridgeNameForNetwork2, fileNameForNetwork2, networkName2)
    print("Creating bridge in hypervisor2 for management tunnel ")
    #create network in hypervisor2
    createBridgeNetworkInHypervisor(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, bridgeNameForNetwork2, fileNameForNetwork2, networkName2)



def createTunnelInHypervisor(ipaddr, username, password, vxlanBridge,vxlanName,tunnelID, remoteIPAddr):
        # get ssh instace from paramiko
        ssh = getSshInstanceFromParamiko(ipaddr, username, password)

	print("Crating tunnel "+ vxlanName + "with id " + tunnelID )
	# commands to create tunnel 
        command_to_create_tunnel = 'sudo -S ip link add name '+ vxlanName +' type vxlan id '+ tunnelID + ' dev ens4 remote '+ remoteIPAddr +' dstport 4098'
	command_to_turn_vxlan_iface_up = 'sudo -S ip link set dev '+ vxlanName +' up'
	command_to_add_vxlan_iface_to_vxlan_br = 'sudo -S  brctl addif '+ vxlanBridge +' ' + vxlanName

	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_create_tunnel)
        ssh_stdin.write( password+'\n')
        ssh_stdin.flush()
        ssh_stdout.readlines()

 
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_turn_vxlan_iface_up)
        ssh_stdin.write( password +'\n')
        ssh_stdin.flush()
        ssh_stdout.readlines() 

	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_add_vxlan_iface_to_vxlan_br)
        ssh_stdin.write( password +'\n')
        ssh_stdin.flush()
        ssh_stdout.readlines()
	return

def destroyLBsIfExistsInHypervisor(ssh):
    # commands to destroy vms	
    command_to_destroy_prev_lbs = 'virsh destroy ' + nameOfLoadBalancer
    command_to_undefine_prev_lbs = 'virsh undefine ' + nameOfLoadBalancer + ' --remove-all-storage'

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_destroy_prev_lbs)
    print(ssh_stdout.readlines())
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_undefine_prev_lbs)
    print(ssh_stdout.readlines())
    return

def createLBInNCHypervisor(nameOfLoadBalancer, ssh):
    command_to_clone_lbs = 'virt-clone --original BASELB1 --name ' + nameOfLoadBalancer + ' --auto-clone'
    command_to_start_lb = 'virsh start ' + nameOfLoadBalancer
    #destroyLBsIfExistsInHypervisor(ssh)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_clone_lbs)
    print(ssh_stdout.readlines())
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_start_lb)
    print(ssh_stdout.readlines())
    time.sleep(25)
    print ("load bancer vim "+ nameOfLoadBalancer + "started succesfully.")
    return

def getSshInstanceFromParamiko(ipaddress, username, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=22, username=username, password=password)
    return ssh


def createNCLoadBalancers(ipaddr, username, password, listOfLBs):
     # get instance of ssh from paramiko
     ssh = getSshInstanceFromParamiko(ipaddr, username, password)

     for nameOfLoadBalancer in listOfLBs:
        createLBInNCHypervisor(nameOfLoadBalancer, ssh)

     ssh.close()
     return


def validateIpProvided(inputDetailsOfHypervisor):
    # ip username pasword format
    # can add ping test to test ip is valid.
    return 0;


def getHypervisorDetailsFromUser():
    inputDetails = raw_input("Enter ip address, username and password  of Hypervisor (space Separated): ")
    #inputDetails = '192.168.122.103 ece792 welcome1'
    inputDetailsArray = inputDetails.strip().split(" ")
    if(len(inputDetailsArray) != 3):
        print("Invalid Number of Arguments.")
        exit(1)

    if len(inputDetailsArray[0].strip().split(".")) != 4 :
        print("Please Enter the valid hypervisor ip")
        exit(1)

    if(validateIpProvided(inputDetailsArray) != 0):
        print("Invalid ip provided")
        exit(1)
    return inputDetailsArray
	
def setGlobalHypervisorDetails(hypervisor1Details, hypervisor2Details):
    global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1 
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
 
    ipOfHypervisor1 = hypervisor1Details[0].strip()
    userNameOfHypervisor1 = hypervisor1Details[1].strip()
    passwordOfHypervisor1 = hypervisor1Details[2].strip()
    
    ipOfHypervisor2 = hypervisor2Details[0].strip()
    userNameOfHypervisor2 = hypervisor2Details[1].strip()
    passwordOfHypervisor2 = hypervisor2Details[2].strip()

def setServerDetailsFromUser():
    global mapOfHypervisorToServer	
    while(True):
	serverDetails = raw_input("Enter the hypervisor name (hypervisor1/hypervisor2) and number of servers on this hypervisor (2 or 4)  (or Enter 1 when finished entering server details) ")
	inputServerDetails = serverDetails.strip()
	if(inputServerDetails == str(1)):
		break
	inputServerDetailsArray = inputServerDetails.split(' ')
        hypervisorName = inputServerDetailsArray[0]
	mapOfHypervisorToServer[hypervisorName] = int(inputServerDetailsArray[1]) 


def getInputsFromUser():
    # need to remove following 2 lines 
    inputDetails = '192.168.149.6 ece792 EcE792net!'
    hypervisor1Details = inputDetails.strip().split(" ")
    #hypervisor1Details = getHypervisorDetailsFromUser()
    
    inputDetails1 = '192.168.149.3 ece792 welcome1'
    hypervisor2Details = inputDetails1.strip().split(" ")
    #hypervisor2Details = getHypervisorDetailsFromUser()
   
    setGlobalHypervisorDetails(hypervisor1Details, hypervisor2Details)
    setServerDetailsFromUser()
	
def writeLBsAndTheirIPsToFile() :
    # writing server ip in file 
    with open('load_balancers.txt', 'wb') as f:
	    writer = csv.writer(f)
	    writer.writerows(dictOfNCLBIps.iteritems() )
	
def writeServerIpsfile():
    print('writing')
    ### converting dict to ips of servers
    listOfServerIP = ['192.168.10.50', '192.168.10.51', '192.168.10.60', '192.168.10.61']
    with open('customer_vms.txt', mode='w') as csv_write_file:
        for ip in listOfServerIP:
		csv_write_file.write(ip)
                csv_write_file.write('\n')
 	
def cpFileToVM(ipaddr, username, password, srcPath, destPath, filename):
	command = 'sshpass -p '+ password +' scp -c aes128-ctr -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' ' + username  +'@'+   ipaddr +':'+ destPath
        os.system(command)



def assignStaticIPToLB():
	global dictOfNCLBIps, lbPassword, lbUserName, listOfHypervisor1LBs, listOfHypervisor2LBs
        global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
        global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
	
	currentWorkingDirectory = os.getcwd()
	destDirectory = '/tmp'
	staticIPScript = "assignStaticIp.py"
	staticAssignLastToLBIPScript = "cronAssignStaticIPs.py"
	### Copy script on hypervisor 
	cpFileToVM(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, currentWorkingDirectory, destDirectory, staticIPScript ) 
		
	cpFileToVM(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, currentWorkingDirectory, destDirectory, staticIPScript ) 

	### Copy assign last 2 vms IP on hypervisor 
        cpFileToVM(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, currentWorkingDirectory, destDirectory, staticAssignLastToLBIPScript )

        cpFileToVM(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, currentWorkingDirectory, destDirectory, staticAssignLastToLBIPScript )

    	ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)

	### give file executing permission
	command_to_change_permission = 'chmod 777 /tmp/'+ staticIPScript
	command_to_change_permission_for_last_2_lb = 'chmod 777 /tmp/'+ staticAssignLastToLBIPScript
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
	print(ssh_stdout.readlines())
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission_for_last_2_lb)
	print(ssh_stdout.readlines())


	### Run script on Hypervisor [ Assigns static IP on Load Balancer VM's customer and management network ]
	command_to_run_static_ip_script = 'python /tmp/' + staticIPScript + ' ' 
	input_static_ip_script = "LB401,LB402" + " " + dictOfNCLBIps["LB401"] + "," + dictOfNCLBIps["LB402"] + " 1" 

	command_to_run_static_ip_script += input_static_ip_script
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_static_ip_script)
	print(ssh_stdout.readlines())
	ssh.close()


	### Run script on Hypervisor [ Assigns static IP on Load Balancer VM's customer and management network ]
    	ssh = getSshInstanceFromParamiko(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)

 	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
        print(ssh_stdout.readlines())
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission_for_last_2_lb)
        print(ssh_stdout.readlines())  

	command_to_run_static_ip_script = 'python /tmp/' + staticIPScript + ' ' 
	input_static_ip_script = "LB501,LB502" + " " + dictOfNCLBIps["LB501"] + "," + dictOfNCLBIps["LB502"] + " 2" 
	command_to_run_static_ip_script += input_static_ip_script
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_static_ip_script)
	print(ssh_stdout.readlines())
	ssh.close()




def assignStaticIPToLB():
	global dictOfNCLBIps, lbPassword, lbUserName, listOfHypervisor1LBs, listOfHypervisor2LBs
        global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
        global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
	
	currentWorkingDirectory = os.getcwd()
	destDirectory = '/tmp'
	staticIPScript = "assignStaticIp.py"
	### Copy script on hypervisor 
	cpFileToVM(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, currentWorkingDirectory, destDirectory, staticIPScript ) 
		
	cpFileToVM(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, currentWorkingDirectory, destDirectory, staticIPScript ) 


    	ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)

	### give file executing permission
	command_to_change_permission = 'chmod 777 /tmp/'+ staticIPScript
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
	print(ssh_stdout.readlines())

	### Run script on Hypervisor [ Assigns static IP on Load Balancer VM's customer and management network ]
	command_to_run_static_ip_script = 'python /tmp/' + staticIPScript + ' ' 
	input_static_ip_script = "LB401,LB402" + " " + dictOfNCLBIps["LB401"] + "," + dictOfNCLBIps["LB402"] + " 1" 

	command_to_run_static_ip_script += input_static_ip_script
	print(command_to_run_static_ip_script)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_static_ip_script)
	print(ssh_stdout.readlines())
	ssh.close()


	### Run script on Hypervisor [ Assigns static IP on Load Balancer VM's customer and management network ]
    	ssh = getSshInstanceFromParamiko(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)

 	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
        print(ssh_stdout.readlines())

	command_to_run_static_ip_script = 'python /tmp/' + staticIPScript + ' ' 
	input_static_ip_script = "LB501,LB502" + " " + dictOfNCLBIps["LB501"] + "," + dictOfNCLBIps["LB502"] + " 2" 
	command_to_run_static_ip_script += input_static_ip_script
	print(command_to_run_static_ip_script)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_static_ip_script)
	print(ssh_stdout.readlines())
	ssh.close()

def transferFileToLB():
	global dictOfNCLBIps, lbPassword, lbUserName, listOfHypervisor1LBs, listOfHypervisor2LBs
        listOfAllLBs = listOfHypervisor1LBs + listOfHypervisor2LBs

        staticDictForLBIps = {}
        staticDictForLBIps['LB101'] = '192.168.98.27'
        staticDictForLBIps['LB102'] = '192.168.98.26'
        staticDictForLBIps['LB201'] = '192.168.98.25'
        staticDictForLBIps['LB202'] = '192.168.98.24'
	for lbName in listOfAllLBs:
		if(lbName in staticDictForLBIps):	# dictOfNCLBIps is dictionary of type loadbalncerName: ipOfLoadBalancer
			ip = staticDictForLBIps[lbName]
			currentWorkingDirectory = os.getcwd()
    			destDirectory = '/tmp'
    			fileName = 'customer_vms.txt'
			currentWorkingDirectoryForShell = '/root/LaaS/lbconfig/iptables/'
			ipTablesFileName = 'handle_iptables.sh'
			ipTableWrapperFileName = 'iptable_wrapper.sh'
			cpFileToVM(ip, lbUserName, lbPassword, currentWorkingDirectory, destDirectory, fileName ) 
			cpFileToVM(ip, lbUserName, lbPassword, currentWorkingDirectoryForShell, destDirectory, ipTablesFileName ) 
			cpFileToVM(ip, lbUserName, lbPassword, currentWorkingDirectoryForShell, destDirectory, ipTableWrapperFileName ) 


if __name__ == "__main__":
	initialize()
