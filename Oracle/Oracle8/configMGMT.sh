#!/bin/bash

#This is a script to configure and update the firewall on redhat.

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ "$#" -eq 1 ]; then
# $1 is the network interface

echo -e "Configuring mgmt NIC\n"

	ip addr add 192.168.10.10/24 broadcast + dev $1
	ip link set mtu 9000 dev $1

echo -e "Opening firewalld ports.\n"

echo -e "Adding nics to trusted zones.\n"

firewall-cmd --zone=trusted --change-interface=$1 --permanent

exit 0

else
    echo "Usage: ./configMGMT.sh {management-interface}"
    echo "For example, to use eth0 as the management interface:"
    echo "./configMGMT.sh eth0"
    exit 1
fi
