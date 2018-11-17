import os
import csv
import datetime as dt

dictOfLBWithTheirIp = {}
listOfLB = []
lbUserName = ''
lbPassword = ''
dnsUserName = ''
dnspassword = ''  
def init():
	global listOfLB, lbUserName, lbPassword, dnsPassword, dnsUserName, dnsVMIP
	lbUserName = 'root'
	lbPassword = 'tushar123'
	dnsUserName = 'root'
	dnsPassword = 'tushar123'
	dnsVMIP= '192.168.124.139'
	listOfLB = ['LB101', 'LB102', 'LB103','LB104','LB105','LB106','LB107','LB108', 'LB109', 'LB110']
	readIPListOfLoadBalancersFromFile()

	assignLBAccordingToTime()
	
	return 

def assignLBAccordingToTime():
	#check if current time is am or pm and according to rule assign or shut lb
	global listOfLB, dictOfLBWithTheirIp
	currentHour = dt.datetime.now().hour
	updatecDictOfLB = {}

	if(currentHour == 0):
		for i in range(5,10):
			key = listOfLB[i]
			if(key in dictOfLBWithTheirIp):
				shutDownNCLB(key)
	else:
		for i in range(5,10):   
                        key = listOfLB[i]
                        if(key in dictOfLBWithTheirIp): 
                                powerOnNCLB(key)
				updatecDictOfLB[key] = dictOfLBWithTheirIp[key]
	for i in range(0,5):
		key = listOfLB[i]
		if(key in dictOfLBWithTheirIp):
			updatecDictOfLB[key] = dictOfLBWithTheirIp[key]

	writeServerIpsfile(updatecDictOfLB)
	transferFileToDNSServer()
	
	return	


def transferFileToDNSServer():
        global dnsVMPassword, dnsUserName, dnsVMIP
	command = 'sshpass -p '+ dnsPassword +' scp -o StrictHostKeyChecking=no /home/ece792/LaaS/updated_load_balancers.txt '+ dnsUserName  +'@'+ dnsVMIP +':/tmp'
	#print (command)
	os.system(command)



def writeServerIpsfile(updatedDictOfLB):
    # writing server ip in file
    with open('updated_load_balancers.txt', 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(updatedDictOfLB.iteritems())


def readIPListOfLoadBalancersFromFile():
	global dictOfLBWithTheirIp
	with open('load_balancers.txt', 'r') as csv_file:
		reader = csv.reader(csv_file, delimiter=',')
		for row in reader:
		        dictOfLBWithTheirIp[row[0]] = row[1]

	return

def shutDownNCLB(nameOfLB):
	command_to_shut_down_lb = 'virsh shutdown' + nameOfLB 

	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_shut_down_lb)
	if (ssh_stderr.readlines() != {}):
		print(ssh_stderr.readlines())
	else: 
		print(nameOfLB + " has shutdown.")
	return

def powerOnNCLB(nameOfLB):
	command_to_start_lb =  'virsh start ' + nameOfLB
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_start_lb)
	
	if (ssh_stderr.readlines() != None):
		print(ssh_stderr.readlines())
	else:
		print (nameOfLB + " has started.")
	return


if __name__ == "__main__":
	init()


