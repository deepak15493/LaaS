#!/bin/bash

HYPHOST=ece792
HYP=192.168.122.58
PASS=EcE792net!
top -b -n 1 > top.txt
sshpass -p $PASS scp -o StrictHostKeyChecking=no /root/top.txt $HYPHOST@$HYP:/home/$HYPHOST
exit
