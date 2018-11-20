import os
import paramiko
import sys

def assignStaticIPOnHypervisor1(LBIP):
	ssh = getSshInstanceFromParamiko(LBIP , "root" , "tushar123");
	command_to_assign_static_ip_eth0 = 'ip addr add 192.168.110.15/24 dev eth0'
	command_to_assign_static_ip_eth1 = 'ip addr add 192.168.111.15/24 dev eth1'
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth0)
	print(ssh_stdout.readlines())
	print(ssh_stderr.readlines())
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth1)
	print(ssh_stdout.readlines())
	print(ssh_stderr.readlines())
        ssh.close()

def assignStaticIPOnHypervisor2(LBIP):
	ssh = getSshInstanceFromParamiko(LBIP , "root" , "tushar123");
	command_to_assign_static_ip_eth0 = 'ip addr add 192.168.110.35/24 dev eth0'
	command_to_assign_static_ip_eth1 = 'ip addr add 192.168.111.35/24 dev eth1'
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth0)
	print(ssh_stdout.readlines())
	print(ssh_stderr.readlines())
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_assign_static_ip_eth1)
	print(ssh_stdout.readlines())
	print(ssh_stderr.readlines())
        ssh.close()


def getSshInstanceFromParamiko(ipaddress, username, password):
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ipaddress, port=22, username="root", password="tushar123")
	return ssh

if __name__ == "__main__":
	### retrieve hypervisor to use
        hypervisorFlag = sys.argv[1].strip()
        ### retireve ip of load balancer
        lbIp = sys.argv[2].strip()

	if hypervisorFlag == str(1):
                assignStaticIPOnHypervisor1(lbIp)
        else:
                assignStaticIPOnHypervisor2(lbIp)
