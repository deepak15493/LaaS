import  os
import paramiko
import csv
import libvirt
import time
from collections import defaultdict
 
#listOfAWSServers = []
listOfNCServersIP = []
#listOfLB = []
#load balancer common credentials
lbUserName = ''
lbPassword = ''
listOfHypervisor1LBs = []
listOfHypervisor2LBs = []
mapOfHypervisorToServer = {} 

dictOfNCLBIps= {}
dictOfNCLBDefaultMac= {}


dictOfNCServerIps = {}
dictOfNCServerDefaultMac = {}

ipOfHypervisor1 = ''
userNameOfHypervisor1 = ''
passwordOfHypervisor1 = ''


ipOfHypervisor2 = ''
userNameOfHypervisor2 = ''
passwordOfHypervisor2 = ''

def initialize():
    #initialize lb credentials
	global listOfHypervisor1LBs, listOfHypervisor2LBs, lbUserName, lbPassword, mapOfHypervisorToServer
	lbUserName = 'root'
	lbPassword = 'tushar123'

	listOfHypervisor1LBs = ['LB401', 'LB402'] 
	listOfHypervisor2LBs = [ 'LB501','LB502']
	
	getInputsFromUser()
	
	# SCP hypervisor1.sh script to hypervisor 1 & hypervisor2.sh to hypervisor2
	cpFileToVM()			# For hypervisor1
	cpFileToVM()			# For hypervisor2
	
	# Run hypervisor1.sh script in hypervisor 1 & hypervisor2.sh in hypervisor2
	runScriptsInHypervisor()	# For hypervisor1
	runScriptsInHypervisor()	# For hypervisor2

	# Collect IP's for front-end servers
	collectIpsForFrontEndLBs()

	# Collect IP's for back-end servers
	collectIpsForBackEndLBs()

	# Detach and Attach interfaces for front-end servers
	detachAndAttachInterfacesForFro 	
	# Detach and Attach interfaces for back-end servers

	# Assign static IP's to front-end servers

	# Assign static IP's to back-end servers

	return

if __name__ == "__main__":
	initialize()
