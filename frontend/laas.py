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
dictOfHypervisorDetails = {}
lbUserName = ''
lbPassword = ''
listOfHypervisor1LBs = []
listOfHypervisor2LBs = []
mapOfHypervisorToServer = defaultdict(list)

dictOfNCLBIps= {}
dictOfNCLBDefaultMac= {}


def initialize():
    print ("Initializing")
    #initialize lb credentials
    global listOfHypervisor1LBs, listOfHypervisor2LBs, lbUserName, lbPassword, mapOfHypervisorToServer
    lbUserName = 'root'
    lbPassword = 'tushar123'

    listOfHypervisor1LBs = ['LB101', 'LB102'] 
    listOfHypervisor2LBs = [ 'LB201','LB202']
    
    getInputsFromUser()
    ### setting up network
    createCustomerNetwork()
    createManagementNetwork()
 
    ### creating tunnels for both Mangement and data flow   
    createTunnelsForManagementAndDataFlow()

    ### create 4 load balancers in AWS
    # createAWSLoadBalancers()
    
    ### create 4 NC load balancers
    handleCreationOfNCLoadBalancers( )
    
    ### get default ips of all load balancers
    collectIpsForLBs()
    
    ### attach load balancers to vxlan network
    attachLBsToVxlanNetwork()
    
    ### assign static ips to just created load balancers vxlan interfaces
    assignStaticIPToLB() 
    
    ### write LBs and their ips to file
    writeLBsAndTheirIPsToFile()
    
    ####  writing server ips to file 
    writeServerIpsfile();   
   
    ### push server name file to all lbs 	
    transferFileToLB()


def collectIpsForLBs():
    global dictOfHypervisorDetails, dictOfNCLBDefaultMac
    ipOfHypervisor1 = dictOfHypervisorDetails['ipOfHypervisor1']
    userNameOfHypervisor1 = dictOfHypervisorDetails['userNameOfHypervisor1']
    passwordOfHypervisor1 = dictOfHypervisorDetails['passwordOfHypervisor1']

    ipOfHypervisor2 = dictOfHypervisorDetails['ipOfHypervisor2']
    userNameOfHypervisor2 = dictOfHypervisorDetails['userNameOfHypervisor2']
    passwordOfHypervisor2 = dictOfHypervisorDetails['passwordOfHypervisor2'] 

    uri1 = 'qemu+ssh://'+userNameOfHypervisor1+'@'+ ipOfHypervisor1 + ':22/system'
    uri2 = 'qemu+ssh://'+userNameOfHypervisor2+'@'+ ipOfHypervisor2 + ':22/system'
    tries1 = 5
    tries2 = 5
    while( tries > 0): 
    	getIpsFromNCHypervisor(uri1)
    	if('LB101' in dictOfNCLBIps and 'LB102' in dictOfNCLBIps and 'LB101' in dictOfNCLBDefaultMac and 'LB102' in dictOfNCLBDefaultMac ):
		break
	tries1--
    
    while( tries > 0): 
   	getIpsFromNCHypervisor(uri2)
    	if('LB201' in dictOfNCLBIps and 'LB202' in dictOfNCLBIps and 'LB201' in dictOfNCLBDefaultMac and 'LB202' in dictOfNCLBDefaultMac ):
                break
        tries2--	
    return

def attachLBsToVxlanNetwork():
    global dictOfHypervisorDetails, listOfHypervisor1LBs, listOfHypervisor2LBs
    # get configuration details from global dict
    ipOfHypervisor1 = dictOfHypervisorDetails['ipOfHypervisor1']
    userNameOfHypervisor1 = dictOfHypervisorDetails['userNameOfHypervisor1']
    passwordOfHypervisor1 = dictOfHypervisorDetails['passwordOfHypervisor1']

    ipOfHypervisor2 = dictOfHypervisorDetails['ipOfHypervisor2']
    userNameOfHypervisor2 = dictOfHypervisorDetails['userNameOfHypervisor2']
    passwordOfHypervisor2 = dictOfHypervisorDetails['passwordOfHypervisor2']
  

    ### Detach default network
    detachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1LBs, 'default')
    detachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2LBs, 'default')
 
    ### attach data network of vxlan 
    attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1LBs, 'vxlan1')
    attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2LBs, 'vxlan1')
    
    ### attach management network of vxlan
    attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1LBs, 'vxlan2')
    attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2LBs, 'vxlan2')

    ## attach default network 
    attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1LBs, 'default')
    attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2LBs, 'default')
	
    return


def detachHypervisorLBs(ipaddr, username, password, listOfHyperviserLBs, networkName):
    global dictOfNCLBDefaultMac
    # get Instance of ssh from paramiko
    ssh  = getSshInstanceFromParamiko(ipaddr, username, password)
 
    for LBName in listOfHyperviserLBs:
    	command_to_attach_iface = 'virsh detach-interface --domain '+ LBName + ' --type network --source '+ networkName + " --mac " + dictOfNCLBDefaultMac[LBName] 
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
    global dictOfHypervisorDetails
    # get configuration details from global dict
    ipOfHypervisor1 = dictOfHypervisorDetails['ipOfHypervisor1']
    userNameOfHypervisor1 = dictOfHypervisorDetails['userNameOfHypervisor1']
    passwordOfHypervisor1 = dictOfHypervisorDetails['passwordOfHypervisor1']

    ipOfHypervisor2 = dictOfHypervisorDetails['ipOfHypervisor2']
    userNameOfHypervisor2 = dictOfHypervisorDetails['userNameOfHypervisor2']
    passwordOfHypervisor2 = dictOfHypervisorDetails['passwordOfHypervisor2']
    
    listOfLBInHypervisor1 = ['LB101', 'LB102']
    listOfLBInHypervisor2 = ['LB201', 'LB202']
    ## create lbs in hypervisor 1
    createNCLoadBalancers(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfLBInHypervisor1)
    ## create lbs in hypervisor 2 
    createNCLoadBalancers(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfLBInHypervisor2)

def createTunnelsForManagementAndDataFlow():
    global dictOfHypervisorDetails
    # get configuration details from global dict
    ipOfHypervisor1 = dictOfHypervisorDetails['ipOfHypervisor1']
    userNameOfHypervisor1 = dictOfHypervisorDetails['userNameOfHypervisor1']
    passwordOfHypervisor1 = dictOfHypervisorDetails['passwordOfHypervisor1']

    ipOfHypervisor2 = dictOfHypervisorDetails['ipOfHypervisor2']
    userNameOfHypervisor2 = dictOfHypervisorDetails['userNameOfHypervisor2']
    passwordOfHypervisor2 = dictOfHypervisorDetails['passwordOfHypervisor2']
    
    ## creating tunnel for data flow
    createTunnelInHypervisor( ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1,'vxlanbr1', 'vxlan101', '41', ipOfHypervisor2 )
    createTunnelInHypervisor( ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, 'vxlanbr1', 'vxlan101', '41', ipOfHypervisor1)

    ## creating tunnel for management of lbs
    createTunnelInHypervisor( ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1,'vxlanbr2', 'vxlan102', '42',ipOfHypervisor2)
    createTunnelInHypervisor( ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, 'vxlanbr2', 'vxlan102', '42', ipOfHypervisor1)


def getIpsFromNCHypervisor(connectionURI):
	global dictOfNCLBIps, dictOfNCLBDefaultMac 
	conn = libvirt.open(connectionURI)
	domains = conn.listAllDomains()
        for domain in domains:
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
    print("creating bridge in hypervisor: " + ipOfHypervisor, usernameOfHypervisor, passwordOfHypervisor)
    ssh = getSshInstanceFromParamiko(ipOfHypervisor, usernameOfHypervisor, passwordOfHypervisor)
    #write vxlan.xml in /home/ece792

    # details for copying file 
    currentWorkingDirectory = os.getcwd()
    destDirectory = '/home/ece792' 
    fileName = fileName
    cpFileToVM(ipOfHypervisor, usernameOfHypervisor, passwordOfHypervisor, currentWorkingDirectory, destDirectory, fileName )
    # wait for scp to finish
    time.sleep(5)

    # add bridge to hypervisor 
    command_to_create_bridge = 'sudo -S brctl addbr ' + bridgeName           #vxlanbr1
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_create_bridge)
    ssh_stdin.write( passwordOfHypervisor +'\n')
    ssh_stdin.flush()
    print(ssh_stdout.read(), ssh_stderr.read())

    # turn bridge iface up
    command_to_turn_vxlanbr1_iface_up = 'sudo -S ip link set dev '+ bridgeName+' up'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_turn_vxlanbr1_iface_up)
    ssh_stdin.write( passwordOfHypervisor +'\n')
    ssh_stdin.flush()
    print(ssh_stdout.read(), ssh_stderr.read())

    #create network  
    command_to_define_network = 'virsh net-define /home/ece792/' + fileName
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_define_network)
    print(ssh_stdout.read(), ssh_stderr.read())

    #start network 
    command_to_start_network = 'virsh net-start '+ networkName
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_start_network)
    print(ssh_stdout.read())

    #close connection hypervisor	
    ssh.close()

def createCustomerNetwork():
    global dictOfHypervisorDetails
    print("printing hyp details : ", dictOfHypervisorDetails)
    ipOfHypervisor1 = dictOfHypervisorDetails['ipOfHypervisor1']
    userNameOfHypervisor1 = dictOfHypervisorDetails['userNameOfHypervisor1']
    passwordOfHypervisor1 =  dictOfHypervisorDetails['passwordOfHypervisor1']

    ipOfHypervisor2 = dictOfHypervisorDetails['ipOfHypervisor2']
    userNameOfHypervisor2 = dictOfHypervisorDetails['userNameOfHypervisor2']
    passwordOfHypervisor2 =  dictOfHypervisorDetails['passwordOfHypervisor2']
 
    bridgeNameForNetwork1 = 'vxlanbr1'
    fileNameForNetwork1 = 'vxlan1.xml'
    networkName1 = 'vxlan1'
    
    #create network in hypervisor1
    createBridgeNetworkInHypervisor(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, bridgeNameForNetwork1, fileNameForNetwork1, networkName1)
    #create network in hypervisor2
    createBridgeNetworkInHypervisor(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, bridgeNameForNetwork1, fileNameForNetwork1, networkName1)

def createManagementNetwork():
    global dictOfHypervisorDetails
    print("printing hyp details : ", dictOfHypervisorDetails)
    ipOfHypervisor1 = dictOfHypervisorDetails['ipOfHypervisor1']
    userNameOfHypervisor1 = dictOfHypervisorDetails['userNameOfHypervisor1']
    passwordOfHypervisor1 =  dictOfHypervisorDetails['passwordOfHypervisor1']

    ipOfHypervisor2 = dictOfHypervisorDetails['ipOfHypervisor2']
    userNameOfHypervisor2 = dictOfHypervisorDetails['userNameOfHypervisor2']
    passwordOfHypervisor2 =  dictOfHypervisorDetails['passwordOfHypervisor2']

    bridgeNameForNetwork2 = 'vxlanbr2'
    fileNameForNetwork2 = 'vxlan2.xml'
    networkName2 = 'vxlan2'
     #create network in hypervisor1
    createBridgeNetworkInHypervisor(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, bridgeNameForNetwork2, fileNameForNetwork2, networkName2)
    #create network in hypervisor2
    createBridgeNetworkInHypervisor(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, bridgeNameForNetwork2, fileNameForNetwork2, networkName2)



def createTunnelInHypervisor(ipaddr, username, password, vxlanBridge,vxlanName,tunnelID, remoteIPAddr):
        # get ssh instace from paramiko
        ssh = getSshInstanceFromParamiko(ipaddr, username, password)

	# commands to create tunnel 
        command_to_create_tunnel = 'sudo -S ip link add name '+ vxlanName +' type vxlan id '+ tunnelID + ' dev ens4 remote '+ remoteIPAddr +' dstport 4098'
	command_to_turn_vxlan_iface_up = 'sudo -S ip link set dev '+ vxlanName +' up'
	command_to_add_vxlan_iface_to_vxlan_br = 'sudo -S  brctl addif '+ vxlanBridge +' ' + vxlanName

	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_create_tunnel)
        ssh_stdin.write( password+'\n')
        ssh_stdin.flush()
        print(ssh_stdout.read(), ssh_stderr.read())

 
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_turn_vxlan_iface_up)
        ssh_stdin.write( password +'\n')
        ssh_stdin.flush()
        print(ssh_stdout.read(), ssh_stderr.read())

	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_add_vxlan_iface_to_vxlan_br)
        ssh_stdin.write( password +'\n')
        ssh_stdin.flush()
        print(ssh_stdout.read(), ssh_stderr.read())
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
    global dictOfHypervisorDetails
    dictOfHypervisorDetails['ipOfHypervisor1'] = hypervisor1Details[0].strip()
    dictOfHypervisorDetails['userNameOfHypervisor1'] = hypervisor1Details[1].strip()
    dictOfHypervisorDetails['passwordOfHypervisor1'] = hypervisor1Details[2].strip()
    
    dictOfHypervisorDetails['ipOfHypervisor2'] = hypervisor2Details[0].strip()
    dictOfHypervisorDetails['userNameOfHypervisor2'] = hypervisor2Details[1].strip()
    dictOfHypervisorDetails['passwordOfHypervisor2'] = hypervisor2Details[2].strip()

def setServerDetailsFromUser():
    global mapOfHypervisorToServer	
    while(True):
	serverDetails = raw_input("Enter  Enter the hypervisor name (hypervisor1/hypervisor2) and ip address of web server space separated ( or Enter 1 when finished entering server details) ")
	inputServerDetails = serverDetails.strip()
	if(inputServerDetails == str(1)):
		break
	inputServerDetailsArray = inputServerDetails.split(' ')
        hypervisorName = inputServerDetailsArray[0]
        ipOfServer = inputServerDetailsArray[1] 
        print("hypervisor : " , hypervisorName, "ip: ", ipOfServer) 
	mapOfHypervisorToServer[hypervisorName].append(ipOfServer)


def getInputsFromUser():
    # need to remove following 2 lines 
    inputDetails = '192.168.149.3 ece792 welcome1'
    hypervisor1Details = inputDetails.strip().split(" ")
    #hypervisor1Details = getHypervisorDetailsFromUser()
    
    inputDetails1 = '192.168.149.6 ece792 EcE792net!'
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
    with open('customer_vms.txt', mode='w') as csv_write_file:
        pass
        csv_writer = csv.writer(csv_write_file)
        csv_writer.writerow(mapOfHypervisorToServer.iteritems())              # need to change this function to accept dictionary instead of list ... prev it was listOfServers
 	
def cpFileToVM(ipaddr, username, password, srcPath, destPath, filename):
	command = 'sshpass -p '+ password +' scp -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' ' + username  +'@'+   ipaddr +':'+ destPath
        print (command)
        os.system(command)

def assignStaticIPToLB():
	global dictOfNCLBIps, lbPassword, lbUserName, listOfHypervisor1LBs, listOfHypervisor2LBs
	global dictOfHypervisorDetails
	print("printing hyp details : ", dictOfHypervisorDetails)
	ipOfHypervisor1 = dictOfHypervisorDetails['ipOfHypervisor1']
	userNameOfHypervisor1 = dictOfHypervisorDetails['userNameOfHypervisor1']
	passwordOfHypervisor1 =  dictOfHypervisorDetails['passwordOfHypervisor1']

	ipOfHypervisor2 = dictOfHypervisorDetails['ipOfHypervisor2']
	userNameOfHypervisor2 = dictOfHypervisorDetails['userNameOfHypervisor2']
	passwordOfHypervisor2 =  dictOfHypervisorDetails['passwordOfHypervisor2']
	
	currentWorkingDirectory = os.getcwd()
	destDirectory = '/tmp'
	staticIPScript = "assignStaticIp.py"
	### Copy script on hypervisor 
	cpFileToVM(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, currentWorkingDirectory, destDirectory, staticIPScript ) 
		
	cpFileToVM(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, currentWorkingDirectory, destDirectory, staticIPScript ) 

	### Run script on Hypervisor [ Assigns static IP on Load Balancer VM's customer and management network ]
    	ssh = getSshInstanceFromParamiko(ipOfHypervisor1, usernameOfHypervisor1, passwordOfHypervisor1)
	command_to_run_static_ip_script = 'python ' + staticIPScript + ' ' 
	input_static_ip_script = ipOfHypervisor1 + " " + usernameOfHypervisor1 + " " + passwordOfHypervisor1 + " LB101,LB102" + " " + dictOfNCLBIps["LB101"] + "," + dictOfNCLBIps["LB102"] + " 1" 

	command_to_run_static_ip_script += input_static_ip_script
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_static_ip_script)
	print(ssh_stdout.readlines())
	ssh.close()


	### Run script on Hypervisor [ Assigns static IP on Load Balancer VM's customer and management network ]
    	ssh = getSshInstanceFromParamiko(ipOfHypervisor2, usernameOfHypervisor2, passwordOfHypervisor2)
	command_to_run_static_ip_script = 'python ' + staticIPScript + ' ' 
	input_static_ip_script = ipOfHypervisor2 + " " + usernameOfHypervisor2 + " " + passwordOfHypervisor2 + " LB201,LB202" + " " + dictOfNCLBIps["LB201"] + "," + dictOfNCLBIps["LB202"] + " 2" 
	command_to_run_static_ip_script += input_static_ip_script
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_static_ip_script)
	print(ssh_stdout.readlines())
	ssh.close()

def transferFileToLB():
	global dictOfNCLBIps, lbPassword, lbUserName, listOfHypervisor1LBs, listOfHypervisor2LBs
        listOfAllLBs = listOfHypervisor1LBs + listOfHypervisor2LBs
	for lbName in listOfAllLB:
		if(lbName in dictOfNCLBIps):	# dictOfNCLBIps is dictionary of type loadbalncerName: ipOfLoadBalancer
			ip = dictOfNCLBIps[lbName]
			currentWorkingDirectory = os.getcwd()
    			destDirectory = '/tmp'
    			fileName = 'customer_vms.txt'
			cpFileToVM(ip, lbUserName, lbPassword, currentWorkingDirectory, destDirectory, fileName ) 

if __name__ == "__main__":
	initialize()
