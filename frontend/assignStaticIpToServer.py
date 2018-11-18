import os
import paramiko
import csv
import libvirt
import time
import sys
from collections import defaultdict


listOfServers=[]
listOfIPOfServers=[]

def assignStaticIPOnHypervisor1():
	global listOfServers,listOfIPOfServers
	last_octet = 51 ;
		
	for ServerIP in listOfIPOfServers:
		ssh = getSshInstanceFromParamiko(ServerIP , "root" , "tushar123");	
    		command_to_assign_static_ip_eth0 = 'ip addr add 192.168.111.' + str(last_octet) + '/24 dev eth0'
    		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth0)
    		print(ssh_stdout.readlines())
		last_octet += 1
	ssh.close()

def assignStaticIPOnHypervisor2():
	global listOfServers,listOfIPOfServers
	last_octet = 53 ;
		
	for ServerIP in listOfIPOfServers:
		print " ServerIP ", ServerIP
		ssh = getSshInstanceFromParamiko(ServerIP , "root" , "tushar123");	
    		command_to_assign_static_ip_eth0 = 'ip addr add 192.168.111.' + str(last_octet) + '/24 dev eth0'
    		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth0)
    		print(ssh_stdout.readlines())
		last_octet += 1
	ssh.close()


def getSshInstanceFromParamiko(ipaddress, username, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=22, username="root", password="tushar123")
    return ssh

if __name__ == "__main__":
	arrOfServers = (sys.argv[1]).strip().split(",")
	arrIPOfServers = (sys.argv[2]).strip().split(",")
	hypervisorFlag = sys.argv[3].strip()
	
	for server in arrOfServers:
		listOfServers.append(server)
	
	for IP in arrIPOfServers:
		listOfIPOfServers.append(IP)
	
	if hypervisorFlag == str(1):
		assignStaticIPOnHypervisor1()
	else:
		assignStaticIPOnHypervisor2()
