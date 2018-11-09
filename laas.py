import  os
import paramiko

listOfAWSServers = []
listOfNCServers = []
ipOfHypervisor = ''
userNameOfHypervisor = ''
passwordOfHypervisor = ''


def initialize():
    print ("Initializing")
    getInputsFromUser()
    # to create 10 AWS load balancers
    # createAWSLoadBalancers()

    # to create 10 NC load balancers
    createNCLoadBalancers()



def setAWSServerList():
    print("YET TO BE IMPLEMENTED")
    return


def getServerList():
    print("YET TO BE IMPLEMENTED")
    return


def createAWSLoadBalancers():
    print("YET TO BE IMPLEMENTED")
    return

def createLBInNCHypervisor(nameOfLoadBalancer, ssh):
    command_to_clone_lbs = 'virt-clone --original VM1 --name ' + nameOfLoadBalancer + ' --auto-clone'
    command_to_destroy_prev_lbs = 'virsh destroy ' + nameOfLoadBalancer
    command_to_undefine_prev_lbs = 'virsh undefine ' + nameOfLoadBalancer + ' --remove-all-storage'
    command_to_start_lb = 'virsh start ' + nameOfLoadBalancer

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_destroy_prev_lbs)
    if (ssh_stderr.readlines() != None):
        print(ssh_stderr.readlines())
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_undefine_prev_lbs)
    if (ssh_stderr.readlines() != None):
        print(ssh_stderr.readlines())
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_clone_lbs)
    if (ssh_stderr.readlines() != None):
        print(ssh_stderr.readlines())

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command_to_start_lb)
    if (ssh_stderr.readlines() != None):
        print(ssh_stderr.readlines())

    # print(ssh_stdin.readlines())
    # print(ssh_stderr.readlines())
    # print(ssh_stdout.readlines())
    return

def createNCLoadBalancers():
    # create lbs in hypervisor
    # wait for 10 s
    # get Ips from respective VMs
    global ipOfHypervisor, userNameOfHypervisor, passwordOfHypervisor
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipOfHypervisor, port=22, username=userNameOfHypervisor, password=passwordOfHypervisor)

    listOfLB = ['LB101', 'LB102', 'LB103','LB104','LB105','LB106','LB107','LB108', 'LB109', 'LB110']

    for nameOfLoadBalancer in listOfLB:
        createLBInNCHypervisor(nameOfLoadBalancer, ssh)

    return


def validateIpProvided(inputDetailsOfHypervisor):
    # ip username pasword format
    # can add ping test to test ip is valid.
    return 0;


def getInputsFromUser():
    global ipOfHypervisor, userNameOfHypervisor, passwordOfHypervisor

    #inputDetails = input("Enter ip address, username and password  of Hypervisor (space Separated): ")
    #inputDetails = raw_input("Enter ip address, username and password  of Hypervisor (space Separated): ")
    inputDetails = '192.168.122.103 ece792 welcome1'
    inputDetailsArray = inputDetails.strip().split(" ")
    if(len(inputDetailsArray) != 3):
        print("Invalid Number of Arguments.")
        exit(1)

    if len(inputDetailsArray[0].strip().split(".")) != 4 :
        print("Please Enter the valid hypervisor ip")
        exit(1)

    if(validateIpProvided(inputDetailsArray) != 0):
        print("Invalid ip provided")
        exit(1)

    #  assigning valid ip to hypervisor
    ipOfHypervisor = inputDetailsArray[0].strip()
    userNameOfHypervisor = inputDetailsArray[1].strip()
    passwordOfHypervisor = inputDetailsArray[2].strip()


initialize()


