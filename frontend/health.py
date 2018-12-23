import paramiko, socket, time, csv, os, subprocess, sys

ipArray = ["192.168.91.51", "192.168.91.52", "192.168.91.53", "192.168.91.54"]
lbNameArray = ["NSLB11", "EWLB11", "NSLB11", "EWLB_11"]
tenantId = 1
currentPublicIp = "192.168.40.2"
remotePublicIp = "192.168.42.2"


def getSshInstanceFromParamiko(ipaddress, username, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=22, username=username, password=password)
    return ssh


def addDynamicLB(lbName):
	currentWorkDir = os.getcwd()
	ipOfHypervisor1= "192.168.149.6"
	userNameOfHypervisor1 = "ece792"
	passwordOfHypervisor1 = "EcE792net!"
	ssh = getSshInstanceFromParamiko(ipOfHypervisor1, userNameOfHypervisor1, passwordOfHypervisor1)
	command_to_run_script = "sudo -S  sh "+ "/home/ece792/Final_Linux_networking/Laas/frontend/" + "sahil_handle_iptables.sh "+ tenantId + "  "+ currentPublicIp + " " + remotePublicIp + " "
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_script)
	ssh_stdin.write( passwordOfHypervisor1 +'\n')
	ssh_stdin.flush()
	print(ssh_stdout.read(), ssh_stderr.read())

	print command_to_run_script

def health_checkup():
	global ipArray, lbNameArray, tenantId
	for i in range (4):
		ip = ipArray[i]
		lbName = lbNameArray[i]
		status = subprocess.call(['ping', '-c', '1', ip],stdout=open(os.devnull, 'wb'))
		#time.sleep(1)
		print("Stats of Load Balancer: " + lbName + " " +  ip )
		if(status==0):
			#result_dict[ipOfHypervisor] = "ACTIVE"
			print("\t Load Balancer is "+ lbName + " is ACTIVE" ) #result_dict[ipOfHypervisor])
		else:
			print("\t Load Balancer is " + lbName + " is INACTIVE ")
			print("Adding new Lb to dynamically")
			addDynamicLB(lbName)


if __name__ == "__main__":
	#tenantId = "1"
	#currentPublicIp = "192.168.40.2"
	#remotePublicIp  = "192.168.42.2"
	#tenantId = raw_input("Please specify the tenant id: ")
	#tenantId = tenantId.strip()
	tenantId = sys.argv[1]
	
	#currentPublicIp = raw_input("Please specify the current public ip: ")
	#currentPublicIp = currentPublicIp.strip()
	currentPublicIp = sys.argv[2]
	
	#remotePublicIp  = raw_input("Please specify the remote public ip: ")
	#remotePublicIp = remotePublicIp.strip()
	remotePublicIp = sys.argv[3]
	health_checkup()
