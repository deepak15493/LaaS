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

mapOfHypervisorToServer = defaultdict(list)

dictOfNCServersIps = {}


def initialize():
    print ("Initializing")
    #initialize lb credentials
    global listOfLB, lbUserName, lbPassword, mapOfHypervisorToServer
    lbUserName = 'root'
    lbPassword = 'tushar123'

    listOfLB = ['LB101', 'LB102', 'LB201','LB202']
    
    getInputsFromUser()
    ### setting up network
    createCustomerNetwork()
    #createManagementNetwork()
    ## need to crerate 2 tunnels 
    #createTunnelInHypervisor()
    #createTunnelInHypervisor()

    # to create 10 AWS load balancers
    # createAWSLoadBalancers()
    # to create 10 NC load balancers


    #### just for avoiding creation of multiple vms
    #createNCLoadBalancers()
    #getIpsFromNCHypervisor() 
    #writeLBsAndTheirIPsToFile()
    ####
    #writeServerIpsfile();   
    #transferFileToLB()

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



def createTunnelInHypervisor(nameOfHypervisor, userNameOfHypervisor, passwordOfHypervisor):
	command_to_clone_lbs = 'virt-clone --original LB1 --name ' + nameOfLoadBalancer + ' --auto-clone'
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_destroy_prev_lbs)
	if (ssh_stderr.readlines() != {}):
		print(ssh_stderr.readlines())

def createLBInNCHypervisor(nameOfLoadBalancer, ssh):
    command_to_clone_lbs = 'virt-clone --original LB1 --name ' + nameOfLoadBalancer + ' --auto-clone'
    command_to_destroy_prev_lbs = 'virsh destroy ' + nameOfLoadBalancer
    command_to_undefine_prev_lbs = 'virsh undefine ' + nameOfLoadBalancer + ' --remove-all-storage'
    command_to_start_lb = 'virsh start ' + nameOfLoadBalancer

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_destroy_prev_lbs)
    if (ssh_stderr.readlines() != {}):
        print(ssh_stderr.readlines())
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_undefine_prev_lbs)
    if (ssh_stderr.readlines() != {}):
        print(ssh_stderr.readlines())
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_clone_lbs)
    if (ssh_stderr.readlines() != {}):
        print(ssh_stderr.readlines())

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_start_lb)
    if (ssh_stderr.readlines() != {}):
        print(ssh_stderr.readlines())

    print ("load bancer vim "+ nameOfLoadBalancer + "started succesfully.")
    return

def getSshInstanceFromParamiko(ipaddress, username, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=22, username=username, password=password)
    return ssh


def createNCLoadBalancers(ssh):
    # create lbs in hypervisor
    # wait for 10 s
    # get Ips from respective VMs
    global ipOfHypervisor, userNameOfHypervisor, passwordOfHypervisor, listOfLB
    #ssh = paramiko.SSHClient()
    #ssh.load_system_host_keys()
    #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh.connect(ipOfHypervisor, port=22, username=userNameOfHypervisor, password=passwordOfHypervisor)


    for nameOfLoadBalancer in listOfLB:
        createLBInNCHypervisor(nameOfLoadBalancer, ssh)

    print ("Waiting for a minute so that LOAD BALANCERS receive  ips Assigned from dhc client") 
    time.sleep(50)

    print ("Fetching IP addressees of Load Balancers.")
    # fetching list of ips from NC hypervisor
    getIpsFromNCHypervisor() 
    writeLBsAndTheirIPsToFile()
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
   # inputDetails = '192.168.122.103 ece792 welcome1'
    #hypervisor1Details = inputDetails.strip().split(" ")
    hypervisor1Details = getHypervisorDetailsFromUser()
    
    #inputDetails1 = '192.168.122.58 ece792 EcE792net!'
    #hypervisor2Details = inputDetails1.strip().split(" ")
    hypervisor2Details = getHypervisorDetailsFromUser()
   
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
