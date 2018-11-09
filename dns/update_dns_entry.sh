#!/bin/bash


create_tmp_dns_config(){
	DOLLAR="$"
echo ";
; BIND data file for local loopback interface
;
${DOLLAR}TTL	604800
@	IN	SOA	tushar.com. root.tushar.com. (
			      7		; Serial
			 604800		; Refresh
			  86400		; Retry
			2419200		; Expire
			 604800 )	; Negative Cache TTL
;
@	IN	NS	tushar.com." > ${TMP_DNS_CONFIG} 


	while IFS='' read -r line || [[ -n "$line" ]]; do
	    dns_server_ip=${line}
	    echo "@	IN	A	${dns_server_ip}" >> ${TMP_DNS_CONFIG}        
	done < ${DNS_SERVER_FILE}


echo "@	IN	AAAA	::1" >> ${TMP_DNS_CONFIG}

}

update_main_dns_config(){
	MAIN_DNS_CONFIG="/etc/bind/db.tushar.com"
	sudo mv ${TMP_DNS_CONFIG} ${MAIN_DNS_CONFIG}
}

restart_daemon(){
	a="a"
	sudo /etc/init.d/bind9 restart
}

DNS_SERVER_FILE="/tmp/dns_servers"
TMP_DNS_CONFIG="/tmp/db.tushar.com"

if [ ! -f ${DNS_SERVER_FILE} ];then
    echo " No new dns work to be done"
    exit 1;
fi


create_tmp_dns_config 

update_main_dns_config

restart_daemon
exit 0;
