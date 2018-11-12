import paramiko


def health_checkup():
	ipOfHypervisor = '192.168.124.483'
        userNameOfHypervisor = 'root'
        passwordOfHypervisor = 'tushar123'
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ipOfHypervisor, port=22, username=userNameOfHypervisor, password=passwordOfHypervisor)
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('ls')
	print(ssh_stderr)	  
  	#if (ssh_stderr.readlines() != {}):
    	print(ssh_stdout.readlines())


health_checkup()
