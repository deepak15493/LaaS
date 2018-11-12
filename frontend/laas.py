import  os
import paramiko
import csv
import libvirt
import time

 
listOfAWSServers = []
listOfNCServers = []
listOfNCServersIP = []
ipOfHypervisor = ''
userNameOfHypervisor = ''
passwordOfHypervisor = ''
listOfLB = []
#load balancer common credentials

lbUserName = ''
lbPassword = ''

listOfServers = []

dictOfNCServersIps = {}



def initialize():
    print ("Initializing")
    #initialize lb credentials
    global listOfLB, lbUserName, lbPassword
    lbUserName = 'root'
    lbPassword = 'tushar123'

    listOfLB = ['LB101', 'LB102', 'LB103','LB104','LB105','LB106','LB107','LB108', 'LB109', 'LB110']
    
    getInputsFromUser()
    # to create 10 AWS load balancers
    # createAWSLoadBalancers()

    # to create 10 NC load balancers


    #### just for avoiding creation of multiple vms
    #createNCLoadBalancers()
    getIpsFromNCHypervisor() 
    writeLBsAndTheirIPsToFile()
    ####
    writeServerIpsfile();   
    transferFileToLB()

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

def createNCLoadBalancers():
    # create lbs in hypervisor
    # wait for 10 s
    # get Ips from respective VMs
    global ipOfHypervisor, userNameOfHypervisor, passwordOfHypervisor, listOfLB
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipOfHypervisor, port=22, username=userNameOfHypervisor, password=passwordOfHypervisor)


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


def getInputsFromUser():
    global ipOfHypervisor, userNameOfHypervisor, passwordOfHypervisor, listOfServers 

    #inputDetails = input("Enter ip address, username and password  of Hypervisor (space Separated): ")
    #inputDetails = raw_input("Enter ip address, username and password  of Hypervisor (space Separated): ")
    inputDetails = '192.168.122.103 ece792 welcome1'
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

    #  assigning valid ip to hypervisor
    ipOfHypervisor = inputDetailsArray[0].strip()
    userNameOfHypervisor = inputDetailsArray[1].strip()
    passwordOfHypervisor = inputDetailsArray[2].strip()
    
    while(True):
	serverDetails = raw_input("Enter ip address of web server space separated ( or Enter 1 when finished entering server details) ")
	inputServerDetails = serverDetails.strip()
	
	if(inputServerDetails == str(1)):
		break
	listOfServers.append(inputServerDetails)
	
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
        csv_writer.writerow(listOfServers)
	
 	

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

	
