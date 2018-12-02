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
        global lbUserName, lbPassword
	global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
        global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2

        lbUserName = 'root'
        lbPassword = 'tushar123'

	inputDetails = '192.168.149.6 ece792 EcE792net!'
        hypervisor1Details = inputDetails.strip().split(" ")
        inputDetails1 = '192.168.149.3 ece792 welcome1'
        hypervisor2Details = inputDetails1.strip().split(" ")

	#Copy files required to set Load Balancer topology
	copyFilesToHypervisors()

	#Change permission for files ssh'ed
	changePermissionForFilesInHypervisor()

	#Execute the files in hypervisor to setup topology
	executeShellScriptsInHypervisors()


def executeShellScriptsInHypervisors():
	global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
        global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2

	ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)
	command_to_run_script = './configure_onetime.sh 1 192.168.149.6 192.168.149.3'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_script)
        print(ssh_stdout.readlines())
	command_to_run_script = './hypervisor1.sh 1 1 192.168.40.2 192.168.40.3 50 192.168.41.2 192.168.41.3 192.168.42.2 192.168.42.3'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_script)
        print(ssh_stdout.readlines())
        ssh.close()

	ssh = getSshInstanceFromParamiko(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)
        command_to_run_script = './configure_onetime.sh 1 192.168.149.3 192.168.149.6'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_script)
        print(ssh_stdout.readlines())
        command_to_run_script = './hypervisor1.sh 2 1 192.168.40.2 192.168.40.3 50 192.168.41.2 192.168.41.3 192.168.42.2 192.168.42.3'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_script)
        print(ssh_stdout.readlines())
        ssh.close()


def changePermissionForFilesInHypervisor():
	global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
        global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2

	ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)
        ### give files executing permission
	fileName = "hypervisor1.sh"
        command_to_change_permission = 'chmod 777 /home/ece792/'+ fileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
        print(ssh_stdout.readlines())
	fileName = "configure_onetime.sh"
        command_to_change_permission = 'chmod 777 /home/ece792/'+ fileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
        print(ssh_stdout.readlines())
	ssh.close()

	ssh = getSshInstanceFromParamiko(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)
        ### give files executing permission
        fileName = "hypervisor1.sh"
        command_to_change_permission = 'chmod 777 /home/ece792/'+ fileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
        print(ssh_stdout.readlines())
        fileName = "configure_onetime.sh"
        command_to_change_permission = 'chmod 777 /home/ece792/'+ fileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
        print(ssh_stdout.readlines())
        ssh.close()



def copyFilesToHypervisors():
	global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
        global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
	currentWorkingDirectory = os.getcwd()
        destDirectory = '/home/ece792'
        fileName = "hypervisor1.sh"
        cpFileToVM(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, currentWorkingDirectory, destDirectory, fileName )
        cpFileToVM(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, currentWorkingDirectory, destDirectory, fileName )
        fileName = "configure_onetime.sh"
        cpFileToVM(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1, currentWorkingDirectory, destDirectory, fileName )
        cpFileToVM(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2, currentWorkingDirectory, destDirectory, fileName )


def getSshInstanceFromParamiko(ipaddress, username, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=22, username=username, password=password)
    return ssh

def cpFileToVM(ipaddr, username, password, srcPath, destPath, filename):
        command = 'sshpass -p '+ password +' scp -c aes128-ctr -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' ' + username  +'@'+   ipaddr +':'+ destPath
        print (command)
        os.system(command)



if __name__ == "__main__":
   	initialize()

