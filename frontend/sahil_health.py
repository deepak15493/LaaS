import paramiko, socket, time, csv, os, subprocess

ipArray = ["192.168.91.51", "192.168.91.52", "192.168.91.53", "192.168.91.54"]
lbNameArray = ["NSLB11", "EWLB11", "NSLB11", "EWLB_11"]
tenantId = 1
currentPublicIp = 192.168.40.2
remotePublicIp = 192.168.42.2

def addDynamicLB(lbName):
	currentWorkDir = os.getcwd()
	os.system("sh ./"+ currentWorkDir + "handle_iptables.sh "+ tenantId + " 4 "+ " 192.168.40.2 192.168.42.2")

def health_checkup():
	global ipArray, lbNameArray, tenantId
	for i in range (4):
		ip = ipArray[i]
		lbName = lbNameArray[i]
		status = subprocess.call(['ping', '-c', '1', ip],stdout=open(os.devnull, 'wb'))
		time.sleep(1)
		print("Stats of Load Balancer: " + lbName + " " +  ip )
		if(status==0):
			#result_dict[ipOfHypervisor] = "ACTIVE"
			print("\t Load Balancer is "+ lbName + " is ACTIVE" ) #result_dict[ipOfHypervisor])
		else:
			print("\t Load Balancer is " + lbName + " is INACTIVE ")
			print("Adding new Lb to dynamically")
			addDynamicLB(lbName)
			### do something here 
			### call tushar script for adding load balancing 
			#dynamicLBConfig()


if __name__ == "__main__":
	tenantId = raw_input("Please specify the tenant id: ")
	tenantId = tenantId.strip()
	currentPublicIp = raw_input("Please specify the current public ip: ")
	currentPublicIp = currentPublicIp.strip()
	remotePublicIp  = raw_input("Please specify the remote public ip: ")
	remotePublicIp = remotePublicIp.strip()
	health_checkup()
