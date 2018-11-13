import os
import paramiko
import csv
import libvirt
import time
import sys
from collections import defaultdict


listOfLBs=[]
listOfIPOfLBs=[]

def assignStaticIPOnHypervisor1():
	global listOfLBs,listOfIPOfLBs
	last_octet = 1 ;
		
	for LBIP in listOfIPOfLBs:
		ssh = getSshInstanceFromParamiko(LBIP , "root" , "tushar123");	
    		command_to_assign_static_ip_eth0 = 'ip addr add 192.168.10.' + str(last_octet) + '/24 dev eth0'
    		command_to_assign_static_ip_eth1 = 'ip addr add 192.168.20.' + str(last_octet) + '/24 dev eth1'
    		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth0)
    		print(ssh_stdout.readlines())
    		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth1)
    		print(ssh_stdout.readlines())
		last_octet += 1
	ssh.close()

def assignStaticIPOnHypervisor2():
	global listOfLBs,listOfIPOfLBs
	last_octet = 10 ;
		
	for LBIP in listOfIPOfLBs:
		print " LBIP ", LBIP
		ssh = getSshInstanceFromParamiko(LBIP , "root" , "tushar123");	
    		command_to_assign_static_ip_eth0 = 'ip addr add 192.168.10.' + str(last_octet) + '/24 dev eth0'
    		command_to_assign_static_ip_eth1 = 'ip addr add 192.168.20.' + str(last_octet) + '/24 dev eth1'
    		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth0)
    		print(ssh_stdout.readlines())
    		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth1)
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
	arrOfLBs = (sys.argv[1]).strip().split(",")
	arrIPOfLBs = (sys.argv[2]).strip().split(",")
	hypervisorFlag = sys.argv[3].strip()
	
	for LB in arrOfLBs:
		listOfLBs.append(LB)
	
	for IP in arrIPOfLBs:
		listOfIPOfLBs.append(IP)
	
	if hypervisorFlag == str(1):
		assignStaticIPOnHypervisor1()
	else:
		assignStaticIPOnHypervisor2()


