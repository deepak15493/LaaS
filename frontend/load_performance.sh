#!/bin/bash

HOST=10.0.0.183
#HYP=192.168.122.58
HOSTUSER=root
#HYPHOST=ece792

sshpass -p dpatil ssh -o StrictHostKeyChecking=no $HOSTUSER@$HOST 'bash -s' < command_script.sh
