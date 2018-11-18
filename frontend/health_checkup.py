import paramiko, socket, time, csv, os, subprocess

result_dict ={}
dictOfLBWithTheirIp={}

def readIPListOfLoadBalancersFromFile():
        with open('health_check_ip_list.txt', 'r') as csv_file:
                reader = csv.reader(csv_file, delimiter=',')
                for row in reader:
                        dictOfLBWithTheirIp[row[0]] = row[1]

        return

def getSshInstanceFromParamiko(ipaddress, username, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=22, username=username, password=password)
    return ssh


def cpFileToVM(ipaddr, username, password, srcPath, destPath, filename):
        command = 'sshpass -p '+ password +' scp -c aes128-ctr -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' ' + username  +'@'+   ipaddr +':'+ destPath
        os.system(command)

def health_checkup():
	#for LBIP in dictOfLBWithTheirIp.values():
	type_of_checkup = input("Enter 1 for Low-Level HealthCheck, 2 for High-Level HealthCheck:")
	for value in dictOfLBWithTheirIp.values():
		ipOfHypervisor = value
		status = subprocess.call(['ping', '-c', '1', ipOfHypervisor],stdout=open(os.devnull, 'wb'))
		time.sleep(1)
		print("Stats of Load Balancer:" + ipOfHypervisor )
		if(status==0):
			result_dict[ipOfHypervisor] = "ACTIVE"
			print("\t Load Balancer is " + result_dict[ipOfHypervisor])
			if(type_of_checkup==2):
	                        userNameOfHypervisor = "root"
        	                passwordOfHypervisor = "tushar123"

                	        currentWorkingDirectory = os.getcwd()
                        	destDirectory = '/tmp'
                        	staticIPScript = "health_check_helper.py"
                        	### Copy script on LB
                        	cpFileToVM(ipOfHypervisor, userNameOfHypervisor, passwordOfHypervisor, currentWorkingDirectory, destDirectory, staticIPScript )

                        	ssh = getSshInstanceFromParamiko(ipOfHypervisor, userNameOfHypervisor, passwordOfHypervisor)
                        	command_to_change_permission = 'chmod 777 /tmp/'+ staticIPScript
                                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission)
                        	command_to_run_health_check = 'python /tmp/' + staticIPScript
                                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_health_check)
                        	print(ssh_stdout.readlines())

		else:
			result_dict[ipOfHypervisor] = "NOT ACTIVE"
			print("\t Load Balancer is " + result_dict[ipOfHypervisor])
	return

readIPListOfLoadBalancersFromFile()
health_checkup()
