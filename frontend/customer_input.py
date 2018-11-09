import os
import csv

l = []


def read_file():
    with open('customer_vms.txt', mode='r') as csv_file:
        # csv_reader = csv.DictReader(csv_file)
        for row in csv_file:
            if row=='' or row==' ':
                continue
            l.append(row[:-1])
    #print(l)


def write_file():
    print('writing')
    with open('customer_vms.txt', mode='w') as csv_write_file:
        pass
        csv_writer = csv.writer(csv_write_file, delimiter='\n')
        csv_writer.writerow(l)


def add():
    while True:
        print('Please enter web server ip to be added')
        val = input()
        if str(val)==str(5):
            print('You are in main menu now.. Please select 1. Add 2. Delete 3.Display 4.Exit')
            return
        l.append(str(val))
        print('value added')
        print('Press 5 to return to main menu')


def delete():
    while True:
        print('Please enter web server ip to be deleted')
        val = input()
        if str(val)==str(5):
            print('You are in main menu now.. Please select 1. Add 2. Delete 3.Display 4.Exit')
            return
        l.remove(str(val))
        print('value deleted')
        print('Press 5 to return to main menu')


def display():
    print('display')
    print(l)


if __name__ == "__main__":
    read_file()
    l = list(filter(None, l))
    while True:
        print('Please select below options:')
        print('1. Add  2. Delete 3. Display 4. Exit')
        inp = int(input())
        if inp == 4:
            write_file()
            import scp_servers
            print("New list is sent to load balancer vms")
            exit(0)
        elif inp == 1:
            add()
        elif inp == 2:
            delete()
        elif inp == 3:
            display()
