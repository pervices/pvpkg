#!/bin/bash

#This is a script to configure and update the firewall on redhat.

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ "$#" -eq 2 ]; then
# $1 is the network interface and $2 is the number

ports='42836 42837 42838 42839 42840 42841 42842 42843 42809 42810 42811 42812 42799'

echo -e "Configuring qSFP+ NIC\n"

	ip addr add 10.10.1$2.10/24 broadcast + dev $1
	ip link set mtu 9000 dev $1

echo -e "Opening firewalld ports.\n"

for port in $ports
do
	firewall-cmd --zone=trusted --add-port=$port/udp
done

echo -e "Adding nics to trusted zones.\n"

	firewall-cmd --zone=trusted --change-interface=$1 --permanent

exit 0

else
    echo "Usage: ./openports-configSFP.sh {network interface} {number}"
    echo "For example, to use enp1s0 with the IP address 10.10.10.10 (corresponding to SPFA):"
    echo "./openports-configSFP.sh enp1s0 0"
    exit 1
fi
