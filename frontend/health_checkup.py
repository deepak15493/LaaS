import paramiko, socket, time, csv

result_dict ={}
dictOfLBWithTheirIp={}

def readIPListOfLoadBalancersFromFile():
        with open('load_balancers.txt', 'r') as csv_file:
                reader = csv.reader(csv_file, delimiter=',')
                for row in reader:
                        dictOfLBWithTheirIp[row[0]] = row[1]

        return

def health_checkup():
	#for LBIP in dictOfLBWithTheirIp.values():
	ipOfHypervisor = '192.168.189.8'
       	print(ipOfHypervisor)
	userNameOfHypervisor = 'root'
        passwordOfHypervisor = 'tushar123'
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print("before")
	try:
        	ssh.connect(ipOfHypervisor, port=22, username=userNameOfHypervisor, password=passwordOfHypervisor)
		result_dict[ipOfHypervisor]="ACTIVE"
		print("try")
	except paramiko.SSHException:
		result_dict[ipOfHypervisor]="NOT ACTIVE"
	except socket.gaierror:
		result_dict[ipOfHypervisor]="NOT ACTIVE"
	except paramiko.ssh_exception.NoValidConnectionsError:
		result_dict[ipOfHypervisor]="NOT ACTIVE"
	except socket.timeout:
		result_dict[ipOfHypervisor]="NOT ACTIVE"
		print("time")
	print("end")	
	ssh.close()
	
	for key, value in result_dict.iteritems():
		print(key,value)
	
#readIPListOfLoadBalancersFromFile()
health_checkup()
