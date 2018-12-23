import  os
import paramiko
import time
from collections import defaultdict


ipOfHypervisor1 = ''
userNameOfHypervisor1 = ''
passwordOfHypervisor1 = ''

ipOfHypervisor2 = ''
userNameOfHypervisor2 = ''
passwordOfHypervisor2 = ''
tenant_id = 1

def initialize():
	print ("Initializing")
	global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
        global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
	global tenant_id 
	inputDetails = '192.168.149.6 ece792 EcE792net!'
        hypervisor1Details = inputDetails.strip().split(" ")
        inputDetails1 = '192.168.149.3 ece792 tushar123'
        hypervisor2Details = inputDetails1.strip().split(" ")

	ipOfHypervisor1= hypervisor1Details[0]
	userNameOfHypervisor1= hypervisor1Details[1]
	passwordOfHypervisor1= hypervisor1Details[2]

	ipOfHypervisor2= hypervisor2Details[0]
	userNameOfHypervisor2= hypervisor2Details[1]
	passwordOfHypervisor2= hypervisor2Details[2]

        tenant_id = raw_input("Please Enter tenant_id ")
	tenant_id = int(tenant_id.strip())
	#Copy files required to set Load Balancer topology
	copyFilesToHypervisors()

	#Change permission for files ssh'ed
	changePermissionForFilesInHypervisor()

	#Execute the files in hypervisor to setup topology
	executeShellScriptsInHypervisors()


def cpFileToVM(ipaddr, username, password, srcPath, destPath, filename):
        command = 'sshpass -p '+ password +' scp -c aes128-ctr -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' ' + username  +'@'+   ipaddr +':'+ destPath
        print (command)
        os.system(command)

def executeShellScriptsInHypervisors():
	global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
        global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2

	ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)
	#command_to_run_script = './configure_onetime.sh 1 192.168.149.6 192.168.149.3'
        #ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_script)
        #print(ssh_stdout.readlines())
	if(tenant_id == 1):
		command_to_run_script = 'sudo -S sh /tmp/sahil_hypervisor.sh 1 1 192.168.40.2 192.168.40.3 50 192.168.41.2 192.168.41.3 192.168.42.2 192.168.42.3'
	else: 
		command_to_run_script = 'sudo -S sh /tmp/sahil_hypervisor.sh 1 2 192.168.60.2 192.168.60.3 60 192.168.61.2 192.168.61.3 192.168.62.2 192.168.62.3'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_script)
	ssh_stdin.write( passwordOfHypervisor1 +'\n')
        ssh_stdin.flush()
        print(ssh_stdout.readlines())
        ssh.close()

	ssh = getSshInstanceFromParamiko(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)
        #command_to_run_script = './configure_onetime.sh 1 192.168.149.3 192.168.149.6'
        #ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_script)
        #print(ssh_stdout.readlines())
	if(tenant_id == 1):
	        command_to_run_script = 'sudo -S sh /tmp/sahil_hypervisor.sh 2 1 192.168.40.2 192.168.40.3 50 192.168.41.2 192.168.41.3 192.168.42.2 192.168.42.3'
	else:
	        command_to_run_script = 'sudo -S sh /tmp/sahil_hypervisor.sh 2 2 192.168.60.2 192.168.60.3 60 192.168.61.2 192.168.61.3 192.168.62.2 192.168.62.3'
		
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_script)
	ssh_stdin.write( passwordOfHypervisor2 +'\n')
        ssh_stdin.flush()
        print(ssh_stdout.readlines())
        ssh.close()


def changePermissionForFilesInHypervisor():
	global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
        global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2

	ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)
        ### give files executing permission
	fileName = "sahil_hypervisor.sh"
        command_to_change_permission = 'chmod 777 /tmp/'+ fileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
        print(ssh_stdout.readlines())
	fileName = "configure_onetime.sh"
        command_to_change_permission = 'chmod 777 /tmp/'+ fileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
        print(ssh_stdout.readlines())
	ssh.close()

	ssh = getSshInstanceFromParamiko(ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2)
        ### give files executing permission
        fileName = "sahil_hypervisor.sh"
        command_to_change_permission = 'chmod 777 /tmp/'+ fileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
        print(ssh_stdout.readlines())
        fileName = "configure_onetime.sh"
        command_to_change_permission = 'chmod 777 /tmp/'+ fileName
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
        print(ssh_stdout.readlines())
        ssh.close()



def copyFilesToHypervisors():
	global ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1
        global ipOfHypervisor2, userNameOfHypervisor2, passwordOfHypervisor2
	currentWorkingDirectory = os.getcwd()
        destDirectory = '/tmp'
        fileName = "sahil_hypervisor.sh"
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


if __name__ == "__main__":
	initialize()
