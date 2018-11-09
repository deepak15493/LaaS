 // This file contains all the to do list for the project .

1. DNS reconfigure hook

[
 
When AM to PM and PM to AM transition happens, we change the list of DNS Server IP's so that DNS Round Robin load balancing can ease up the load. Cron script in dns server run helper script [ update_dns_entry.sh ] that does this changes on the DNS server. One of the load balancing VM's [ all of them can too ] need to writea file in /tmp named as dns_servers. 
Cron script will check for this file once every 12 hours and perform the required update.
 
]
