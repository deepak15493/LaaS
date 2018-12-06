import paramiko, socket, time, csv, os, subprocess


def health_checkup():
	ipArray = ["192.168.91.51", "192.168.91.52", "192.168.91.53", "192.168.91.54"]
	for ip in ipArray:
		status = subprocess.call(['ping', '-c', '1', ipOfHypervisor],stdout=open(os.devnull, 'wb'))
		time.sleep(1)
		print("Stats of Load Balancer:" + ipOfHypervisor )
		if(status==0):
			result_dict[ipOfHypervisor] = "ACTIVE"
			print("\t Load Balancer is " + result_dict[ipOfHypervisor])
		else:
			### do something here 
			### call tushar script for adding load balancing 
			print("Not Active")
