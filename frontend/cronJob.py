import os
import csv
import paramiko
import datetime as dt

dictOfLBWithTheirIp = {}
listOfLB = []
dnsUserName = ''
dnsPassword = ''  
dnsVMIP = ''

def init():
	global listOfLB, dnsPassword, dnsUserName, dnsVMIP
	dnsUserName = 'root'
	dnsPassword = 'tushar123'
	dnsVMIP= '192.168.98.70'
	listOfLB = ['LB101', 'LB201', 'LB102','LB202']
	
	### read load_balancers.txt to get all lbs and their ip mappings
	readIPListOfLoadBalancersFromFile()

	assignLBAccordingToTime()
	
	return 

def getSshInstanceFromParamiko(ipaddress, username, passwd):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=22, username=username, password=passwd)
    return ssh

def assignLBAccordingToTime():
	#check if current time is am or pm and according to rule assign or shut lb
	global listOfLB, dictOfLBWithTheirIp
	currentHour = dt.datetime.now().hour
	updatedDictOfLB = {}

	if(currentHour == 20):
		print("trying to suspend lbs")
		for i in range(2,4):
			key = listOfLB[i]
			if(key in dictOfLBWithTheirIp):
				suspendNCLB(key)
		for j in range(0,2):
			key = listOfLB[j]
			updatedDictOfLB[key] = dictOfLBWithTheirIp[key]
				
	elif( currentHour == 21):
		for i in range(2,4):   
                        key = listOfLB[i]
                        if(key in dictOfLBWithTheirIp): 
                                resumeNCLB(key)
				
		### need to assign static ips again
		assignStaticIpToLB()
		for j in range(0,4):
			key = listOfLB[j]
			updatedDictOfLB[key] = dictOfLBWithTheirIp[key]

	### write updated load balancer ips
	writeUpdatedLBIpsToFile(updatedDictOfLB)
	transferFileToDNSServer()
	return	


def transferFileToDNSServer():
        global dnsVMPassword, dnsUserName, dnsVMIP
	command = 'sshpass -p '+ dnsPassword +' scp -c aes128-ctr -o StrictHostKeyChecking=no /root/LaaS/frontend/updated_load_balancers.txt '+ dnsUserName  +'@'+ dnsVMIP +':/tmp'
	#print (command)
	os.system(command)



def writeUpdatedLBIpsToFile(updatedDictOfLB):
    # writing server ip in file
    with open('updated_load_balancers.txt', 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(updatedDictOfLB.iteritems())


def readIPListOfLoadBalancersFromFile():
	global dictOfLBWithTheirIp
	with open('/root/LaaS/frontend/load_balancers.txt', 'r') as csv_file:
		reader = csv.reader(csv_file, delimiter=',')
		for row in reader:
		        dictOfLBWithTheirIp[row[0]] = row[1]

	return

def suspendNCLB(nameOfLB):
	ssh = None
	if(nameOfLB == "LB102"):
		ssh = getSshInstanceFromParamiko("192.168.149.6" , "ece792" , "EcE792net!")
	elif (nameOfLB == "LB202"):
		ssh = getSshInstanceFromParamiko("192.168.149.3" , "ece792" , "welcome1")

	command_to_suspend_lb = 'virsh suspend ' + nameOfLB 
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_suspend_lb)
	print(ssh_stdout.readlines())
	print(nameOfLB , " suspended successfully!")
	return

def assignStaticIpToLB():
	 ssh = getSshInstanceFromParamiko("192.168.149.6" , "ece792" , "EcE792net!");
   	 command_to_run_staticIP_assign_script = 'python /tmp/cronAssignStaticIPs.py 1 '+dictOfLBWithTheirIp['LB102']	 
         ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_staticIP_assign_script)
  	 print(ssh_stdout.readlines())
	 ssh.close()
	
	 ssh = getSshInstanceFromParamiko("192.168.149.3" , "ece792" , "welcome1");
   	 command_to_run_staticIP_assign_script = 'python /tmp/cronAssignStaticIPs.py 2 '+dictOfLBWithTheirIp['LB202']	 
         ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_run_staticIP_assign_script)
  	 print(ssh_stdout.readlines())
	 ssh.close()
	 return

def resumeNCLB(nameOfLB):
	ssh = None
        if(nameOfLB == "LB102"):
                ssh = getSshInstanceFromParamiko("192.168.149.6" , "ece792" , "EcE792net!")
        elif (nameOfLB == "LB202"):
                ssh = getSshInstanceFromParamiko("192.168.149.3" , "ece792" , "welcome1")

	command_to_start_lb =  'virsh resume ' + nameOfLB
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_start_lb)
	print(ssh_stdout.readlines())
        print(nameOfLB , " started successfully")
	return


if __name__ == "__main__":
	init()

