;
; BIND data file for local loopback interface
;
$TTL	604800
@	IN	SOA	tushar.com. root.tushar.com. (
			      7		; Serial
			 604800		; Refresh
			  86400		; Retry
			2419200		; Expire
			 604800 )	; Negative Cache TTL
;
@	IN	NS	tushar.com.
@	IN	A	192.168.124.99
@	IN	A	192.168.124.147
@	IN	AAAA	::1
