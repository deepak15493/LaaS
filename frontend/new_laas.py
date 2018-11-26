import  os
import paramiko
import csv
import libvirt
import time
from collections import defaultdict
 

#load balancer common credentials
lbUserName = ''
lbPassword = ''

mapOfHypervisorToServer = {} 

dictOfNCLBIps= {}
dictOfNCLBDefaultMac= {}

dictOfFrontEndDefaultMac = {}
dictOfBackEndDefaultMac = {}

dictOfFrontEndDefaultIp = {}
dictOfBackEndDefaultIp = {}

listOfHypervisor1Servers = []
listOfHypervisor2Servers = []

ipOfHypervisor1 = ''
userNameOfHypervisor1 = ''
passwordOfHypervisor1 = ''


ipOfHypervisor2 = ''
userNameOfHypervisor2 = ''
passwordOfHypervisor2 = ''

def initialize():
	#initialize lb credentials
	global  lbUserName, lbPassword, mapOfHypervisorToServer
	global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
	global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
	global listOfHypervisor1Servers, listOfHypervisor2Servers
	lbUserName = 'root'
	lbPassword = 'tushar123'
	listOfHypervisor1Servers = ["S11", "S12", "T11", "T12"]
	listOfHypervisor2Servers = ["S21", "S22", "T21", "T22"]

	getInputsFromUser()

	# SCP hypervisor1.sh script to hypervisor 1 & hypervisor2.sh to hypervisor2
	#cpShellScriptToHypervisors()

	# Run hypervisor1.sh script in hypervisor 1 & hypervisor2.sh in hypervisor2
	#runShellScriptsInHypervisors()

	# Collect IP's for servers
	#collectIpsForServers()
	print(dictOfFrontEndDefaultIp)
	print(dictOfBackEndDefaultIp)
	print(dictOfFrontEndDefaultMac)
	print(dictOfBackEndDefaultMac)
	# Detach and Attach interfaces for front-end servers
	#attachServersToRespectiveNetworks()

	collectIpsForServers()
	# assign static ip s
	assignStaticIpsToServers()
	return

def assignStaticIpsToServers():
    global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
    global dictOfFrontEndDefaultIp, dictOfBackEndDefaultIp
    dictOfServers = dictOfBackEndDefaultIp.copy()
    dictOfServers.update(dictOfFrontEndDefaultIp)

    print("in assign Static Ips to Servers ")
    print(dictOfServers)

    listOfServersHypervisor1 = ["S11","S12","T11","T12"] 
    listOfServersHypervisor2 = ["S21","S22","T21","T22"]

    #scp assign.py assignHypervisor.py to both hyperviosrs
    srcPath = os.getcwd()
    destPath = '/home/ece792'
    cpFileToVM(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, srcPath, destPath, "assign.py")
    cpFileToVM(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, srcPath, destPath, "assignHypervisor.py")

    cpFileToVM(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, srcPath, destPath, "assign.py")
    cpFileToVM(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, srcPath, destPath, "assignHypervisor.py")
    
    #execute assignHypervisor.py with changed permission on both files
    ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)
    command_to_change_permission1 = 'chmod 777 /home/ece792/assignHypervisor.py'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission1)
    print(ssh_stdout.readlines())
    for name in listOfServersHypervisor1:
        ip = dictOfServers[name]
        command_to_execute = 'python /home/ece792/assignHypervisor.py ' + name + ' ' + ip
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_execute)
        print(ssh_stdout.readlines())
    ssh.close()

   # ssh = getSshInstanceFromParamiko(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)
   # command_to_change_permission2 = 'chmod 777 /home/ece792/assignHypervisor.py'
   # ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission2)
   # print(ssh_stdout.readlines())
   # for name in listOfServersHypervisor2:
   #     ip = dictOfServers[name]
   #     command_to_execute = 'python /home/ece792/assignHypervisor.py ' + name + ' ' + ip
   #     ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_execute)
   #     print(ssh_stdout.readlines())
   # ssh.close()


def attachServersToRespectiveNetworks():
    global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
    global listOfHypervisor1Servers, listOfHypervisor2Servers
    listOfNetworks = ["network11", "network13", "network12"]
    ### Detach default network
    print("Detaching \"default\" interface for LBs")  
    print(listOfHypervisor1Servers)
    detachHypervisorServers(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1Servers, 'default')
    #detachHypervisorServers(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2Servers, 'default')

    ### attach data network of vxlan 
    for i in range (0,2):
	print(i)
        attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1Servers[0], listOfNetworks[i])
        attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1Servers[1], listOfNetworks[i])
        #attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2Servers[0], listOfNetworks[i])
        #attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2Servers[1], listOfNetworks[i])

    for i in range (2,4):
        attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1Servers[i], listOfNetworks[2])
        #attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2Servers[i], listOfNetworks[2])

    ## attach default network 
    for i in range (0,4):
        attachHypervisorLBs(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, listOfHypervisor1Servers[i], 'default')
        #attachHypervisorLBs(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, listOfHypervisor2Servers[i], 'default')

    return

def detachHypervisorServers(ipaddr, username, password, listOfHyperviserServers, networkName):
    global dictOfBackEndDefaultmac,  dictOfFrontEndDefaultMac
    dictOfServerToMac = dictOfBackEndDefaultMac.copy()   # start with x's keys and values
    dictOfServerToMac.update(dictOfFrontEndDefaultMac) 
    # get Instance of ssh from paramiko
    print("in detach hypervisor servers")
    print(dictOfServerToMac, listOfHyperviserServers)
    ssh  = getSshInstanceFromParamiko(ipaddr, username, password)

    for nameOfServer in listOfHyperviserServers:
        command_to_attach_iface = 'virsh detach-interface --domain '+ nameOfServer + ' --type network --mac ' + dictOfServerToMac[nameOfServer] 
	print(command_to_attach_iface)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_attach_iface)
        print(ssh_stdout.read())
    time.sleep(1)
    ssh.close()
    return


def attachHypervisorLBs(ipaddr, username, password, serverName, networkName):
    # get Instance of ssh from paramiko
    ssh  = getSshInstanceFromParamiko(ipaddr, username, password)

    command_to_attach_iface = 'virsh attach-interface --domain '+ serverName + ' --type network --source '+ networkName +' --model virtio --config --live'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_attach_iface)
    print(ssh_stdout.read(), ssh_stderr.read())
    time.sleep(1)
    ssh.close()
    return





def getFrontEndDetails(connectionURI):
    global dictOfFrontEndDefaultIp, dictOfFrontEndDefaultMac
    
    conn = libvirt.open(connectionURI)
    domainIDs = conn.listDomainsID()
    #domains = conn.listDomains()
    for domainID in domainIDs:
        domain = conn.lookupByID(domainID)
        if(domain.name().startswith( 'S' )):
            ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
            if(bool(ifaces)):
                key, value = ifaces.popitem()
                if 'addrs' in value:
                        dictOfFrontEndDefaultIp[domain.name()] = value['addrs'][0]['addr']
                if 'hwaddr' in value:
                        dictOfFrontEndDefaultMac[domain.name()] = value['hwaddr']
    
    conn.close()


def getBackEndDetails(connectionURI):
    global dictOfBackEndDefaultIp, dictOfBackEndDefaultMac
    
    conn = libvirt.open(connectionURI)
    domainIDs = conn.listDomainsID()
    #domains = conn.listDomains()
    for domainID in domainIDs:
        domain = conn.lookupByID(domainID)
        if(domain.name().startswith( 'T' )):
            ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
            if(bool(ifaces)):
                key, value = ifaces.popitem()
                if 'addrs' in value:
                        dictOfBackEndDefaultIp[domain.name()] = value['addrs'][0]['addr']
                if 'hwaddr' in value:
                        dictOfBackEndDefaultMac[domain.name()] = value['hwaddr']
    
    conn.close()


def collectIpsForServers():
    global  dictOfFrontEndDefaultMac, dictOfFrontEndDefaultIp, dictOfBackEndDefaultIp, dictOfBackEndDefaultMac
    global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2

    print("Waiting for 40 sec before starting collection of IPs from LBs ")
    #time.sleep(40)
    uri1 = 'qemu+ssh://'+userNameOfHypervisor1+'@'+ ipOfHypervisor1 + ':22/system'
    uri2 = 'qemu+ssh://'+userNameOfHypervisor2+'@'+ ipOfHypervisor2 + ':22/system'
    tries1 = 5
    tries2 = 5
    while( tries1 > 0):
        getFrontEndDetails(uri1)
        getBackEndDetails(uri1)
        if('S11' in dictOfFrontEndDefaultIp and 'S12' in dictOfFrontEndDefaultIp and 'T11' in dictOfBackEndDefaultIp and 'T12' in dictOfBackEndDefaultIp and
            'S11' in dictOfFrontEndDefaultMac and 'S12' in dictOfFrontEndDefaultMac and 'T11' in dictOfBackEndDefaultMac and 'T12' in dictOfBackEndDefaultMac ):
                break
        print("Failed to collect IP's from all LBs. Retrying in 30 seconds"+ str(tries1))
        time.sleep(30)
        tries1 -= 1

#    while( tries2 > 0):
#        getFrontEndDetails(uri2)
#        getBackEndDetails(uri2)
#        if('S21' in dictOfFrontEndDefaultIp and 'S22' in dictOfFrontEndDefaultIp and 'T21' in dictOfBackEndDefaultIp and 'T22' in dictOfBackEndDefaultIp and
#            'S21' in dictOfFrontEndDefaultMac and 'S22' in dictOfFrontEndDefaultMac and 'T21' in dictOfBackEndDefaultMac and 'T22' in dictOfBackEndDefaultMac ):
#                break
#        print("Failed to collect IP's from all LBs. Retrying in 30 seconds"+str(tries2))
#        time.sleep(30)
#        tries2 -= 1
#    print("Collected IP's success fully")
    return


def cpShellScriptToHypervisors():
    global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
    srcPath = os.getcwd()
    destPath = "/home/ece792"
    fileName = "hypervisor1.sh"
    cpFileToVM( ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, srcPath, destPath, filename)

    fileName = "hypervisor2.sh"
    cpFileToVM( ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, srcPath, destPath, filename)


def getSshInstanceFromParamiko(ipaddress, username, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=22, username=username, password=password)
    return ssh



def runShellScriptsInHypervisors():
    global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
    global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2

    ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)
    command_to_change_permission1 = 'chmod 777 /home/ece792/hypervisor1.sh'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission1)
    print(ssh_stdout.readlines())
    ssh.close()

    ssh = getSshInstanceFromParamiko(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)
    command_to_change_permission2 = 'chmod 777 /home/ece792/hypervisor2.sh'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission2)
    print(ssh_stdout.readlines())
    ssh.close()


    ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)
    command_to_run_script = "sudo ./hypervisor1.sh"
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_script)
    ssh_stdin.write( 'EcE792net!\n')
    ssh_stdin.flush()
    print(ssh_stdout.readlines())
    ssh.close()

    ssh = getSshInstanceFromParamiko(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)
    command_to_run_script = "sudo ./hypervisor2.sh"
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_script)
    ssh_stdin.write( 'tushar123\n')
    ssh_stdin.flush()
    print(ssh_stdout.readlines())
    ssh.close()


def cpFileToVM(ipaddr, username, password, srcPath, destPath, filename):
        command = 'sshpass -p '+ password +' scp -c aes128-ctr -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' ' + username  +'@'+   ipaddr +':'+ destPath
        print(command)
        os.system(command)

def getInputsFromUser():
    # need to remove following 2 lines 
    inputDetails = '192.168.149.6 ece792 EcE792net!'
    hypervisor1Details = inputDetails.strip().split(" ")
    #hypervisor1Details = getHypervisorDetailsFromUser()

    inputDetails1 = '192.168.149.3 ece792 tushar123'
    hypervisor2Details = inputDetails1.strip().split(" ")
    #hypervisor2Details = getHypervisorDetailsFromUser()

    setGlobalHypervisorDetails(hypervisor1Details, hypervisor2Details)
    setServerDetailsFromUser()

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
    mapOfHypervisorToServer['hypervisor1'] = 2 
    mapOfHypervisorToServer['hypervisor2'] = 2 


if __name__ == "__main__":
	initialize()
