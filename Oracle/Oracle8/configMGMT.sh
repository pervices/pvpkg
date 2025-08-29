#!/bin/bash

#This is a script to configure and update the firewall on redhat.

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ "$#" -eq 1 ]; then
# $1 is the network interface

echo -e "Configuring mgmt NIC\n"

nmcli connection modify "$1" \
	ipv4.method manual \
	ipv4.addresses "192.168.10.10/24" \
	connection.autoconnect yes # This ensures the connection is activated on boot.

nmcli connection up "$1"

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
