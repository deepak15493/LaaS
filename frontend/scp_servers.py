import csv
import os

with open('load_servers.csv',mode='r') as csv_file:
	csv_reader = csv.DictReader(csv_file)
	line_count = 0
	for row in csv_reader:
		#print(row["load_balancer"]+ ' '+ row["ip"]+ ' '+ row["user"]+ ' ' + row['pass'])
		#os.system('echo '+row["pass"]+'| sudo -S mkdir /temp1')
		os.system('sshpass -p '+row["pass"]+' scp -o StrictHostKeyChecking=no /home/ece792/web_server.csv '+row["user"]+'@'+row["ip"]+':/tmp')
		line_count+=1		 
