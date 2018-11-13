import  os
import paramiko
import csv
import libvirt
import time
from collections import defaultdict
 
listOfAWSServers = []
listOfNCServers = []
listOfNCServersIP = []
listOfLB = []
#load balancer common credentials
dictOfHypervisorDetails = {}
lbUserName = ''
lbPassword = ''
listOfHypervisor1LBs = []
listOfHypervisor2LBs = []
mapOfHypervisorToServer = defaultdict(list)

dictOfNCServersIps = {}


def initialize():
    print ("Initializing")
    #initialize lb credentials
    global listOfHyperviser1LBs, listOfHyperviser2LBs, lbUserName, lbPassword, mapOfHypervisorToServer
    lbUserName = 'root'
    lbPassword = 'tushar123'

    listOfHyperviser2LBs = ['LB101', 'LB102'] [
    listOfHyperviser2LBs = [ 'LB201','LB202']
    
    getInputsFromUser()
    ### setting up network
    createCustomerNetwork()
    #createManagementNetwork()
 
    ### creating tunnels for both Mangement and data flow   
    createTunnelsForManagementAndDataFlow()

    ### create 4 load balancers in AWS
    # createAWSLoadBalancers()
    
    ### create 4 NC load balancers
    handleCreationOfNCLoadBalancers( )
    
    ### attach load balancers to vxlan network
    attachLBsToVxlanNetwork()
    
    ### get default ips of all load balancers
   # getIpsFromNCHypervisor()
     collectIpsForLBs()
    #writeLBsAndTheirIPsToFile()
    ####
    #writeServerIpsfile();   
    #transferFileToLB()


def collectIpsForLBs():
    

def attachLBsToVxlanNetwork():
    global dictOfHypervisorDetails, listOfHyperviser1LBs, listOfHyperviser2LBs
    # get configuration details from global dict
    ipOfHypervisor1 = dictOfHypervisorDetails['ipOfHypervisor1']
    userNameOfHypervisor1 = dictOfHypervisorDetails['userNameOfHypervisor1']
    passwordOfHypervisor1 = dictOfHypervisorDetails['passwordOfHypervisor1']

    ipOfHypervisor2 = dictOfHypervisorDetails['ipOfHypervisor2']
    userNameOfHypervisor2 = dictOfHypervisorDetails['userNameOfHypervisor2']
    passwordOfHypervisor2 = dictOfHypervisorDetails['passwordOfHypervisor2']
   
    ### attach data network of vxlan 
    attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHyperviser1LBs, 'vxlan1')
    attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHyperviser2LBs, 'vxlan1')
    
    ### attach management network of vxlan
    #attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHyperviser1LBs, 'vxlan2')
    #attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHyperviser2LBs, 'vxlan2')

    ## attach default network 
    attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHyperviser1LBs, 'vxlan2')
    attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHyperviser2LBs, 'vxlan2')
	
    return


def attachHypervisorLBs(ipaddr, username, password, listOfHyperviserLBs, networkName):
    # get Instance of ssh from paramiko
    ssh  = getSshInstanceFromParamiko(ipaddr, username, password)
 
    for LBName in listOfHyperviserLBs:
    	command_to_attach_iface = 'virsh attach-interface --domain '+ LBName + ' --type network --source '+ networkName +' --model virtio --config --live'
    	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_attach_iface)
    	print(ssh_stdout.read(), ssh_stderr.read())

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
    createTunnelInHypervisor( ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1,'vxlanbr1', 'vxlan101', 41)
    createTunnelInHypervisor( ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, 'vxlanbr1', 'vxlan101', 41)

    ## creating tunnel for management of lbs
    #createTunnelInHypervisor( ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1,'vxlanbr2', 'vxlan102', 42)
    #createTunnelInHypervisor( ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, 'vxlanbr2', 'vxlan102', 42)

def getIpsFromNCHypervisor():
	global dictOfNCServersIps 
	conn = libvirt.open('qemu:///system')
	domains = conn.listAllDomains()
        for domain in domains:
                if(domain.name().startswith( 'LB' )):
                     ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
                     if(bool(ifaces)):
                             key, value = ifaces.popitem()
                             if 'addrs' in value:
                                     dictOfNCServersIps[domain.name()] = value['addrs'][0]['addr']


        for k, v in dictOfNCServersIps.iteritems():
                print k , v
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

def createBridgeNetworkInHypervisor(ipOfHypervisor, usernameOfHypervisor, passwordOfHypervisor):
    print("creating bridge in hypervisor: " + ipOfHypervisor, usernameOfHypervisor, passwordOfHypervisor)
    ssh = getSshInstanceFromParamiko(ipOfHypervisor, usernameOfHypervisor, passwordOfHypervisor)
    #write vxlan.xml in /home/ece792

    # details for copying file 
    currentWorkingDirectory = os.getcwd()
    destDirectory = '/home/ece792' 
    fileName = 'vxlan1.xml'
    cpFileToVM(ipOfHypervisor, usernameOfHypervisor, passwordOfHypervisor, currentWorkingDirectory, destDirectory, fileName )
    # wait for scp to finish
    time.sleep(5)

    # add bridge to hypervisor 
    command_to_create_bridge = 'sudo -S brctl addbr vxlanbr1'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_create_bridge)
    ssh_stdin.write( passwordOfHypervisor +'\n')
    ssh_stdin.flush()
    print(ssh_stdout.read(), ssh_stderr.read())

    # turn bridge iface up
    command_to_turn_vxlanbr1_iface_up = 'sudo -S ip link set dev vxlanbr1 up'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_turn_vxlanbr1_iface_up)
    ssh_stdin.write( passwordOfHypervisor +'\n')
    ssh_stdin.flush()
    print(ssh_stdout.read(), ssh_stderr.read())

    #create network  
    command_to_define_network = 'virsh net-define /home/ece792/vxlan1.xml'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_define_network)
    print(ssh_stdout.read(), ssh_stderr.read())

    #start network 
    command_to_start_network = 'virsh net-start vxlan1'
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

    #create network in hypervisor1
    createBridgeNetworkInHypervisor(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)
    #create network in hypervisor2
    createBridgeNetworkInHypervisor(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)

def createManagementNetwork():
	print('Yet to be implemented')



def createTunnelInHypervisor(ipaddr, username, password, vxlanBridge,vxlanName,tunnelID):
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
    command_to_clone_lbs = 'virt-clone --original LB1 --name ' + nameOfLoadBalancer + ' --auto-clone'
    command_to_start_lb = 'virsh start ' + nameOfLoadBalancer
    #destroyLBsIfExistsInHypervisor(ssh)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_clone_lbs)
    print(ssh_stdout.readlines())
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_start_lb)
    print(ssh_stdout.readlines())

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
    #print ("Waiting for a minute so that LOAD BALANCERS receive  ips Assigned from dhc client") 
    #time.sleep(50)

    #print ("Fetching IP addressees of Load Balancers.")
    # fetching list of ips from NC hypervisor
    #getIpsFromNCHypervisor() 
    #writeLBsAndTheirIPsToFile()
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
	    writer.writerows(dictOfNCServersIps.iteritems() )
	
def writeServerIpsfile():
    print('writing')
    with open('customer_vms.txt', mode='w') as csv_write_file:
        pass
        csv_writer = csv.writer(csv_write_file, delimiter='\n')
        csv_writer.writerow(mapOfHypervisorToServer)              # need to change this function to accept dictionary instead of list ... prev it was listOfServers
 	
def cpFileToVM(ipaddr, username, password, srcPath, destPath, filename):
	command = 'sshpass -p '+ password +' scp -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' ' + username  +'@'+   ipaddr +':'+ destPath
        print (command)
        os.system(command)


def transferFileToLB():
	global dictOfNCServersIps, lbPassword, lbUserName
	for lbName in listOfLB:
		if(lbName in dictOfNCServersIps):			# dictOfNCServersIps is dictionary of type loadbalncerName: ipOfLoadBalancer
			ip = dictOfNCServersIps[lbName] 
			command = 'sshpass -p '+ lbPassword +' scp -o StrictHostKeyChecking=no /home/ece792/LaaS/customer_vms.txt '+ lbUserName  +'@'+ ip +':/tmp'
			#print (command)
			os.system(command)

if __name__ == "__main__":
	initialize()
