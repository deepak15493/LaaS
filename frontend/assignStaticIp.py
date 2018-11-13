
import  os
import paramiko
import csv
import libvirt
import time
from collections import defaultdict


hypervisorIP=""
username=""
password=""
listOfLBs=[]
listOfIPOfLBs=[]

def assignStaticIPOnHypervisor1():
	global listOfLBs, username, password , hypervisorIP
	last_octet = 0 ;
		
	for LBIP in listOfIPOfLBs:
		ssh = getSshInstanceFromParamiko(LBIP , username , password);	
    		command_to_assign_static_ip_eth0 = 'ip addr add 192.168.10.' + last_octet + '/24 dev eth0'
    		command_to_assign_static_ip_eth1 = 'ip addr add 192.168.20.' + last_octet + '/24 dev eth1'
    		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth0)
    		print(ssh_stdout.readlines())
    		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth1)
    		print(ssh_stdout.readlines())


def assignStaticIPOnHypervisor2():
	global listOfLBs, username, password , hypervisorIP
	last_octet = 10 ;
		
	for LBIP in listOfIPOfLBs:
		ssh = getSshInstanceFromParamiko(LBIP , username , password);	
    		command_to_assign_static_ip_eth0 = 'ip addr add 192.168.10.' + last_octet + '/24 dev eth0'
    		command_to_assign_static_ip_eth1 = 'ip addr add 192.168.20.' + last_octet + '/24 dev eth1'
    		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth0)
    		print(ssh_stdout.readlines())
    		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth1)
    		print(ssh_stdout.readlines())
	


def getSshInstanceFromParamiko(ipaddress, username, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=22, username=username, password=password)
    return ssh

if __name__ == "__main__":
	global listOfLBs, username, password , hypervisorIP
	hypervisorIP = sys.argv[1]
	username = sys.argv[2]
	password = sys.argv[3]
	arrOfLBs = (sys.argv[4]).strip().split(",")
	arrIPOfLBs = (sys.argv[5]).strip().split(",")
	hypervisorFlag = sys.argv[6].strip()
	
	for LB in arrOfLBs:
		listOfLBs.append(LB)
	
	for IP in arrIPOfLBs:
		listOfIPOfLBs.append(LB)
	
	if hypervisorFlag == str(1):
		assignStaticIPOnHypervisor1()
	else:
		assignStaticIPOnHypervisor2()
