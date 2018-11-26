import paramiko



def getSshInstanceFromParamiko(ipaddress, username, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=22, username=username, password=password)
    return ssh

def cpFileToVM(ipaddr, username, password, srcPath, destPath, filename):
        command = 'sshpass -p '+ password +' scp -c aes128-ctr -o StrictHostKeyChecking=no ' + srcPath + '/' + filename + ' ' + username  +'@'+   ipaddr +':'+ destPath
        print(command)
        os.system(command)




if __init__=="__main__":
	serverName = (sys.argv[1]).strip()
	ipAddressOfServer = (sys.argv[2]).strip()

	
	srcPath = "/home/ece792/" 
	cpFileToVM(ipAddressOfServer, "root", "tushar123", srcPath, '/root/', "assign.py")
	ssh = getSshInstanceFromParamiko(ipAddressOfServer, "root", "tushar123")
	
	command_to_change_permission1 = 'chmod 777 /root/assign.py'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_change_permission1)
        print(ssh_stdout.readlines())
	
	command_to_execute = "python assign.py "+serverName 
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_execute)
        print(ssh_stdout.readlines())
	ssh.close()
