import os
import time

mappingOfServerNameToIp = {}



def initialize(listofInterfaces, nameOfServer):
	global mappingOfServerNameToIp
        mappingOfServerNameToIp['S11Interface1'] = '192.168.80.51'
        mappingOfServerNameToIp['S11Interface2'] = '192.168.85.51'
        mappingOfServerNameToIp['S12Interface1'] = '192.168.80.52'
        mappingOfServerNameToIp['S12Interface2'] = '192.168.85.52'
        mappingOfServerNameToIp['S21Interface1'] = '192.168.80.53'
        mappingOfServerNameToIp['S21Interface2'] = '192.168.95.51'
        mappingOfServerNameToIp['S22Interface1'] = '192.168.80.54'
        mappingOfServerNameToIp['S22Interface2'] = '192.168.95.52'
        mappingOfServerNameToIp['T11Interface1'] = '192.168.90.51'
        mappingOfServerNameToIp['T12Interface1'] = '192.168.90.52'
        mappingOfServerNameToIp['T21Interface1'] = '192.168.90.53'
        mappingOfServerNameToIp['T22Interface1'] = '192.168.90.54'

	
	for i in range(0, len(listofInterfaces)):
		key = nameOfServer+ "Interface" + str(i+1)
		if key in mappingOfServerNameToIp:
			ip = mappingOfServerNameToIp[key]
			interface = listofInterfaces[i]
			writeFile(ip, interface)
	
	time.sleep(2)
	# Restarting network
	os.system("service network restart")


def writeFile(ip, interface):
    fileName = "ifcfg-" + interface
    with open('/etc/sysconfig/network-scripts/'+fileName, 'a') as f:
    	f.write("DEVICE="+interface)
	f.write("BOOTPROTO=none")
	f.write("ONBOOT=yes")
	f.write("PREFIX=24")
	f.write("IPADDR="+ip)      
		

if __init__=="__main__":
	nameOfServer = (sys.argv[1]).strip()
	listofInterfaces = os.listdir('/sys/class/net/')
	listofInterfaces.sort()
	initialize(listofInterfaces, nameOfServer)

