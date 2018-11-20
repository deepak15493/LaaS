import os
import paramiko
import csv
import libvirt
import time
import sys
from collections import defaultdict


listOfLBs=[]
listOfIPOfLBs=[]


def executeCommand(ssh, command, password):
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
	ssh_stdin.write(password+'\n')
        ssh_stdin.flush()                           
        ssh_stdout.readlines()

def assignStaticIPOnHypervisor1():
	global listOfLBs,listOfIPOfLBs
	last_octet = 5 ;
		
	for iter in range(len(listOfIPOfLBs)):
		LBIP = listOfIPOfLBs[iter]
		LBNAME = listOfLBs[iter]
		ssh = getSshInstanceFromParamiko(LBIP , "root" , "tushar123");	
		srcPath  = '/tmp/'
		destPath = '/etc/sysconfig/network-scripts/'
		if(LBNAME == "LB401"):
			srcPath += 'LB401'
		elif (LBNAME == "LB402"):
			srcPath += 'LB402'
 
		filename = "ifcfg-eth0"
		command_eth0  = 'sshpass -p tushar123 scp -c aes128-ctr -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' root@'+  LBIP +':'+ destPath
        
		filename = "ifcfg-eth1"
		command_eth1  = 'sshpass -p tushar123 scp -c aes128-ctr -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' root@'+  LBIP +':'+ destPath
		
		print(command_eth0)
        	os.system(command_eth0)
		print(command_eth1)
		os.system(command_eth1)

		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("service network restart")
		ssh_stdout.readlines()

		#command_to_shutdown_interface_eth0 = 'sudo ip link set eth0 down'
		#command_to_shutdown_interface_eth1 = 'sudo ip link set eth1 down'

		#command_to_poweron_interface_eth0 = 'sudo ip link set eth0 up'
		#command_to_poweron_interface_eth1 = 'sudo ip link set eth1 up'

    		#command_to_assign_static_ip_eth0 = 'ip addr add 192.168.110.' + str(last_octet) + '/24 dev eth0'
    		#command_to_assign_static_ip_eth1 = 'ip addr add 192.168.111.' + str(last_octet) + '/24 dev eth1'


		#executeCommand(ssh, command_to_shutdown_interface_eth0, 'tushar123')
		#executeCommand(ssh, command_to_shutdown_interface_eth1, 'tushar123')
		#time.sleep(2)
		#executeCommand(ssh, command_to_assign_static_ip_eth0, 'tushar123')
		#executeCommand(ssh, command_to_assign_static_ip_eth1, 'tushar123')
		#
		#time.sleep(4)
		#executeCommand(ssh, command_to_assign_static_ip_eth0, 'tushar123')
		#executeCommand(ssh, command_to_assign_static_ip_eth1, 'tushar123')
		#time.sleep(4)
		#executeCommand(ssh, command_to_assign_static_ip_eth0, 'tushar123')
		#executeCommand(ssh, command_to_assign_static_ip_eth1, 'tushar123')
		#time.sleep(2)
		#executeCommand(ssh, command_to_poweron_interface_eth0, 'tushar123')
		#executeCommand(ssh, command_to_poweron_interface_eth1, 'tushar123')

		#last_octet += 10
		ssh.close()
		time.sleep(2)

def assignStaticIPOnHypervisor2():
	global listOfLBs,listOfIPOfLBs
	last_octet = 25 ;
		
	for iter in range(len(listOfIPOfLBs)):
		LBIP = listOfIPOfLBs[iter]
		LBNAME = listOfLBs[iter]
		ssh = getSshInstanceFromParamiko(LBIP , "root" , "tushar123");	
    		
                srcPath  = '/tmp/'
                destPath = '/etc/sysconfig/network-scripts/'
                if(LBNAME == "LB501"):
                        srcPath += 'LB501'
                elif (LBNAME == "LB502"):
                        srcPath += 'LB502'

                filename = "ifcfg-eth0"
                command_eth0  = 'sshpass -p tushar123 scp -c aes128-ctr -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' root@'+  LBIP +':'+ destPath

                filename = "ifcfg-eth1"
                command_eth1  = 'sshpass -p tushar123 scp -c aes128-ctr -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' root@'+  LBIP+':'+ destPath

                print(command_eth0)
                os.system(command_eth0)
                print(command_eth1)
                os.system(command_eth1)

                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("service network restart")
                ssh_stdout.readlines()

        #        command_to_shutdown_interface_eth1 = 'sudo ip link set eth1 down'

        #        command_to_poweron_interface_eth0 = 'sudo ip link set eth0 up'
        #        command_to_poweron_interface_eth1 = 'sudo ip link set eth1 up'

	#	command_to_assign_static_ip_eth0 = 'ip addr add 192.168.110.' + str(last_octet) + '/24 dev eth0'
    	#	command_to_assign_static_ip_eth1 = 'ip addr add 192.168.111.' + str(last_octet) + '/24 dev eth1'

	#	executeCommand(ssh, command_to_shutdown_interface_eth0, 'tushar123')
	#	executeCommand(ssh, command_to_shutdown_interface_eth1, 'tushar123')
	#	time.sleep(2)
	#	executeCommand(ssh, command_to_assign_static_ip_eth0, 'tushar123')
	#	executeCommand(ssh, command_to_assign_static_ip_eth1, 'tushar123')
	#	time.sleep(4)
	#	executeCommand(ssh, command_to_assign_static_ip_eth0, 'tushar123')
	#	executeCommand(ssh, command_to_assign_static_ip_eth1, 'tushar123')
	#	time.sleep(4)
	#	executeCommand(ssh, command_to_assign_static_ip_eth0, 'tushar123')
	#	executeCommand(ssh, command_to_assign_static_ip_eth1, 'tushar123')
	#	time.sleep(2)
	#	executeCommand(ssh, command_to_poweron_interface_eth0, 'tushar123')
	#	executeCommand(ssh, command_to_poweron_interface_eth1, 'tushar123')
	#	last_octet += 10
		ssh.close()
		time.sleep(2)


def getSshInstanceFromParamiko(ipaddress, username, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=22, username="root", password="tushar123")
    return ssh

if __name__ == "__main__":
	arrOfLBs = (sys.argv[1]).strip().split(",")
	arrIPOfLBs = (sys.argv[2]).strip().split(",")
	hypervisorFlag = sys.argv[3].strip()
	print(arrIPOfLBs)
	for LB in arrOfLBs:
		listOfLBs.append(LB)
	
	for IP in arrIPOfLBs:
		listOfIPOfLBs.append(IP)
	
	if hypervisorFlag == str(1):
		assignStaticIPOnHypervisor1()
	else:
		assignStaticIPOnHypervisor2()
